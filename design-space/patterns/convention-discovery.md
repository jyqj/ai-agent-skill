# Convention-based Discovery

> **Evidence Status** — grounded. 源自 Generic Agent 的 dispatch 实现和多个极简 Agent 框架的共同做法，属于实践中反复出现的轻量模式。

工具系统最常见的问题不是"怎么实现工具"，而是"怎么注册工具"。注册表、配置文件、装饰器——这些方式都要求开发者在实现之外再做一次显式声明。约定式发现（Convention-based Discovery）的思路是：**用命名约定替代注册，让方法名本身就是声明**。

## 核心机制

约定很简单：方法名以 `do_` 开头即为工具。框架通过反射（Reflection）扫描所有 `do_*` 方法，自动生成工具列表和调用入口。

```python
# 不需要显式注册
@register_tool("code_run")
def code_run(args): ...

# 只需要命名约定
def do_code_run(self, args, response): ...
```

方法的 docstring 直接作为工具描述，参数签名用于生成 Schema——整个过程零配置。

## 调度与三阶段钩子

`dispatch` 方法根据工具名拼接方法名，查找并调用。调用前后提供钩子（Hook），用于注入权限检查、参数改写、日志等横切逻辑：

```python
class BaseHandler:
    def dispatch(self, tool_name, args, response):
        method_name = f"do_{tool_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            yield from self.tool_before_callback(tool_name, args)
            result = yield from method(args, response)
            yield from self.tool_after_callback(tool_name, args, result)
            return result
        else:
            return StepOutcome(None, next_prompt=f"未知工具 {tool_name}")
```

扩展时只需继承并覆写钩子方法，比如在 `tool_before_callback` 中对 `code_run` 注入安全头。

## Schema 自动生成

框架遍历所有 `do_*` 方法，从方法名、docstring 和签名中提取工具名、描述和参数，生成符合 function-calling 规范的 Schema。这意味着新增工具只需要写一个方法，不需要维护任何配置文件。

## 权衡

这个模式最大的优势是**极低的样板开销**——新增工具就是新增方法，继承即可定制。它非常适合工具数量少、迭代快的极简框架（核心代码约 100 行量级）和快速原型。

代价是隐式性。工具的存在完全由命名约定决定，没有静态类型检查，IDE 和新成员都不容易一眼看出"这个类提供了哪些工具"。对于工具数量多、参数结构复杂、需要严格类型校验的系统，注册表或装饰器模式仍然更合适。

简单对比：

| 模式 | 配置方式 | 类型安全 | 代码量 |
|-----|---------|---------|-------|
| 注册表 | 显式 | 高 | 多 |
| 装饰器 | 显式 | 高 | 中 |
| 约定发现 | 隐式 | 低 | 少 |

## 参考实现

- `projects/general-agents/generic-agent/agent-loop.snippet.md` — dispatch 方法
- `projects/general-agents/generic-agent/tool-system.snippet.md` — do_* 工具实现
