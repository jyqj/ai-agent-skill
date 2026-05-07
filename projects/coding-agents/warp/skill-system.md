# Warp Skill System Source Analysis

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。

> **Evidence Status** — grounded. `crates/ai/src/skills/` 全部源码、`app/src/ai/skills/skill_manager.rs` 源码。

## 架构总览

Warp 的 skill 系统分为两层：
1. **crates/ai/src/skills/** — 底层解析和发现（纯逻辑，无 UI 依赖）
2. **app/src/ai/skills/** — 应用层管理（文件监控、UI 集成、生命周期）

```text
crates/ai/src/skills/
├── mod.rs              ← 公开 API
├── parse_skill.rs      ← SKILL.md 解析（frontmatter + body）
├── parser.rs           ← Markdown front matter 解析器
├── read_skills.rs      ← 目录递归扫描
├── skill_provider.rs   ← 10 种 provider 定义与路径匹配
├── skill_reference.rs  ← Skill 引用类型
└── conversion.rs       ← 格式转换

app/src/ai/skills/
├── mod.rs              ← 模块入口
├── skill_manager.rs    ← SkillManager singleton（600+ 行）
├── listed_skill.rs     ← UI 展示用 skill
├── resolve_skill_spec.rs ← Skill spec 解析
├── skill_utils.rs      ← 去重、排序工具
├── dummy_skill_manager.rs ← 测试用 mock
├── file_watchers/      ← 文件系统监控
│   ├── mod.rs
│   ├── skill_watcher.rs ← SkillWatcher（监控 skill 文件变更）
│   ├── subscribers.rs
│   └── utils.rs
└── telemetry.rs        ← Skill 使用遥测
```

## 10 种 Skill Provider

```rust
// crates/ai/src/skills/skill_provider.rs

pub enum SkillProvider {
    Warp,       // .warp/skills/
    Agents,     // .agents/skills/  (最高优先级)
    Claude,     // .claude/skills/
    Codex,      // .codex/skills/
    Cursor,     // .cursor/skills/
    Gemini,     // .gemini/skills/
    Copilot,    // .copilot/skills/
    Droid,      // .factory/skills/
    Github,     // .github/skills/
    OpenCode,   // .opencode/skills/
}

pub enum SkillScope {
    Home,       // ~/.agents/skills/ 等
    Project,    // ./repo/.agents/skills/ 等
    Bundled,    // Warp 内置
}

// 优先级由定义顺序决定
pub static SKILL_PROVIDER_DEFINITIONS: LazyLock<Vec<SkillProviderDefinition>> =
    LazyLock::new(|| vec![
        // Agents > Warp > Claude > Codex > Cursor > Gemini > Copilot > Droid > Github > OpenCode
        SkillProviderDefinition {
            provider: SkillProvider::Agents,
            skills_path: PathBuf::from(".agents").join("skills"),
        },
        SkillProviderDefinition {
            provider: SkillProvider::Warp,
            skills_path: PathBuf::from(".warp").join("skills"),
        },
        // ... 其余 8 个 provider
    ]);
```

**关键洞察**：Warp 不只支持自己的 skill 格式，而是兼容 10 种 agent 工具的 skill 目录。这意味着一个 repo 中来自 Claude Code、Codex、Cursor 等不同 agent 的 skills 都能被 Warp 发现和使用。

## Skill 解析

```rust
// crates/ai/src/skills/parse_skill.rs

const MAX_SKILL_DESCRIPTION_CHARS: usize = 512;

#[derive(Debug, Clone, PartialEq)]
pub struct ParsedSkill {
    pub path: PathBuf,
    pub name: String,
    pub description: String,
    pub content: String,               // 完整文件内容（含 frontmatter）
    pub line_range: Option<Range<usize>>, // markdown body 的行范围
    pub provider: SkillProvider,        // 来自哪个 provider
    pub scope: SkillScope,             // Home / Project / Bundled
}

pub fn parse_skill(path: &Path) -> Result<ParsedSkill> {
    let provider = get_provider_for_path(path).unwrap_or(SkillProvider::Agents);
    let scope = get_scope_for_path(path);
    parse_skill_internal(path, provider, scope)
}

pub fn parse_bundled_skill(path: &Path) -> Result<ParsedSkill> {
    parse_skill_internal(path, SkillProvider::Warp, SkillScope::Bundled)
}

fn parse_skill_internal(path: &Path, provider: SkillProvider, scope: SkillScope) -> Result<ParsedSkill> {
    let parsed = parse_markdown_file(path)?;

    // name: 优先从 frontmatter，降级从目录名推导
    let name = parsed.front_matter.get("name")
        .map(|v| v.trim()).filter(|v| !v.is_empty())
        .map(|n| n.to_string())
        .unwrap_or_else(|| derive_skill_name_from_path(path));

    // description: 优先从 frontmatter，降级从内容首段推导
    let description = parsed.front_matter.get("description")
        .map(|v| v.trim()).filter(|v| !v.is_empty())
        .map(|d| d.to_string())
        .unwrap_or_else(|| truncate_skill_description(
            &derive_description_from_content(&parsed.content, parsed.line_range.as_ref())
        ));

    Ok(ParsedSkill { path, name, description, content: parsed.content, line_range: parsed.line_range, provider, scope })
}
```

**设计洞察**：
- Skill 解析是**容错**的：没有 frontmatter 也能从路径和内容推导 name/description
- Description 有 512 字符限制，且在句子边界截断
- 提供两个入口：`parse_skill`（自动检测 provider）和 `parse_bundled_skill`（强制 Warp + Bundled）

## SkillManager：应用层管理器

```rust
// app/src/ai/skills/skill_manager.rs

pub struct SkillManager {
    // 目录 → skill 路径集合
    directory_skills: HashMap<PathBuf, HashSet<PathBuf>>,
    // 路径 → 解析后的 skill
    skills_by_path: HashMap<PathBuf, ParsedSkill>,
    // 名称 → 路径集合（同名 skill 可能来自多个源）
    skills_by_name: HashMap<String, HashSet<PathBuf>>,
    // 内置 skills
    bundled_skills: HashMap<String, BundledSkill>,
    // Cloud 环境下所有 skills 都在作用域内
    is_cloud_environment: bool,
    // 文件监控器
    skill_watcher: ModelHandle<SkillWatcher>,
}

// 内置 Skill 的激活条件
pub enum BundledSkillActivation {
    Always,                        // 始终可用
    RequiresMcp(McpIntegration),   // 需要特定 MCP 服务器在运行
    RequiresFile(PathBuf),         // 需要特定文件存在
}

pub struct BundledSkill {
    pub skill: ParsedSkill,
    pub activation: BundledSkillActivation,
    pub icon: Icon,
}

impl SkillManager {
    pub fn new(ctx: &mut ModelContext<Self>) -> Self {
        // 1. 创建异步 channel 接收 file watcher 事件
        let (skill_watcher_tx, skill_watcher_rx) = async_channel::unbounded();

        // 2. 订阅 file watcher 事件流
        ctx.spawn_stream_local(skill_watcher_rx, |me, message, _ctx| {
            me.handle_skill_watcher_event(message);
        }, |_, _| {});

        // 3. 创建 SkillWatcher model
        let skill_watcher = ctx.add_model(|ctx| SkillWatcher::new(ctx, skill_watcher_tx));

        // 4. 异步加载内置 skills
        if FeatureFlag::BundledSkills.is_enabled() {
            ctx.spawn(Self::load_bundled_skills(), |me, result, _| {
                me.bundled_skills = result;
            });
        }
        // ...
    }

    /// 按工作目录返回可用 skills（含 scope 过滤）
    pub fn get_skills_for_working_directory(
        &self,
        working_directory: Option<&Path>,
        ctx: &AppContext,
    ) -> Vec<SkillDescriptor> {
        // Home skills 始终可用
        // Project skills 需要 cwd 在对应目录下
        // Cloud 环境下所有 project skills 可用
        // Bundled skills 需要检查 activation 条件
        // 最后去重（同名 skill 取优先级最高的 provider）
    }
}
```

**设计洞察**：
- SkillManager 是 **SingletonEntity**，全局唯一实例
- 通过 SkillWatcher 实时响应文件变更（创建/修改/删除 skill）
- 内置 skills 有条件激活：Always / 需要 MCP / 需要文件存在
- Cloud 环境下的 scope 扩展：本地需要 cwd 匹配，Cloud 下全部可见
- 去重策略：同名 skill 取优先级最高的 provider

## Skill 去重与优先级

```rust
// app/src/ai/skills/skill_utils.rs

pub fn unique_skills(skills: Vec<SkillDescriptor>) -> Vec<SkillDescriptor> {
    // 按 (name, provider_rank) 分组
    // 同名 skill 保留 provider_rank 最小（优先级最高）的那个
    // Agents(0) > Warp(1) > Claude(2) > Codex(3) > ...
}
```

## 与知识库的关联

### 印证

- `paradigms/tool-paradigms.md`：Skills 是"元工具"— 结构化指令，而非直接 API 调用
- `architecture/planes/tools/overview.md`：10 种 provider 实现了跨工具链的 skill 发现
- `design-space/patterns/progressive-disclosure.md`：三层加载（metadata → body → references）

### 独特贡献

1. **10 种 Provider 兼容**：一个系统发现和使用来自 10 种不同 agent 工具的 skills
2. **条件激活**：BundledSkillActivation 让 skill 可用性依赖运行时状态（MCP、文件）
3. **容错解析**：没有 frontmatter 也能工作，从路径和内容推导元数据
4. **实时文件监控**：SkillWatcher 响应 skill 文件的增删改
5. **Cloud Scope 扩展**：本地 vs Cloud 环境的 skill 可见性不同
