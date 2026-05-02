# 自我进化机制

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 核心理念：**能力不预设，靠进化获得**

## 进化流程图

```
[新任务]
    ↓
[自主摸索] (安装依赖、编写脚本、调试验证)
    ↓
[执行成功]
    ↓
[调用 start_long_term_update]
    ↓
[分类信息] → L2 (事实) / L3 (SOP) / L1 (索引)
    ↓
[file_patch 更新记忆层]
    ↓
[下次同类任务]
    ↓
[skill_search 召回] → 直接执行
```

## 进化前后对比

| 你说的话 | 第一次 Agent 做了什么 | 之后每次 |
|---------|---------------------|---------|
| "监控股票并提醒我" | 安装 mootdx → 构建选股流程 → 配置定时 → 保存 Skill | 一句话启动 |
| "用 Gmail 发文件" | 配置 OAuth → 编写发送脚本 → 保存 Skill | 直接可用 |
| "读取微信消息" | 安装依赖 → 逆向数据库 → 写读取脚本 → 保存 Skill | 一句话调用 |

## skill_search 集成

```python
# memory/skill_search/skill_search/engine.py
class SkillSearchEngine:
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        '''语义匹配，返回相关 Skill'''
        # 远端 API (105K+ 技能库)
        response = requests.post(API_URL, json={"query": query, "top_k": top_k})
        return [SearchResult(**r) for r in response.json()]

@dataclass
class SearchResult:
    skill_name: str
    description: str
    file_path: str      # SOP 或脚本路径
    confidence: float
```

## 记忆固化触发

```python
def do_start_long_term_update(self, args, response):
    '''Agent 自主判断是否触发'''

    # 1. 注入现有记忆
    result = get_global_memory()

    # 2. 注入 L0 指导
    if os.path.exists('./memory/memory_management_sop.md'):
        result = file_read('./memory/memory_management_sop.md')

    # 3. 返回结算 prompt
    prompt = '''### [总结提炼经验]
    提取【事实验证成功且长期有效】的信息：
    - **环境事实** → file_patch 更新 L2 + 同步 L1
    - **复杂任务经验** → L3 精简 SOP（仅记核心坑点）

    禁止：临时变量、推理过程、未验证信息、通用常识
    '''
    return StepOutcome(result, next_prompt=prompt)
```

## L3 SOP 格式示例

```markdown
# tmwebdriver_sop.md

## 前置条件
- Chrome 已安装
- TMWebDriver CDP 桥接已配置

## 典型坑点
1. 文件上传需要用 input[type=file].sendKeys()，不能用 click()
2. iframe 内元素需要先 switchTo().frame()
3. 动态加载元素需要显式等待

## 常用代码
```python
# 文件上传
driver.find_element("css selector", "input[type=file]").send_keys(file_path)
```
```

## 权限边界

```python
# 自主行动框架 (autonomous_operation_sop)
PERMISSIONS = {
    'read_only': True,           # 只读操作无需审批
    'write_in_cwd': True,        # cwd 内写操作无需审批
    'modify_L1_L2_L3': 'pending', # 记忆层修改需待审
    'external_api': 'ask_user',   # 外部 API 需确认
}
```

## 进化指标

用几周后的典型结果：
- **Skill 数量**：从 0 → 50+
- **平均任务轮次**：从 10+ → 2-3
- **重复任务耗时**：从分钟级 → 秒级
