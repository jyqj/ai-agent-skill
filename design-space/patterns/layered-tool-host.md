# Layered Tool Host

> **Evidence Status** — grounded. 从 Augment、Claude Code 等产品的工具架构中提炼，属于工程层面的成熟模式。

Agent 可用的工具风险差异巨大。调用一个只读的搜索 API 几乎没有副作用，读取本地文件需要路径权限，而执行 Shell 命令则可能删除数据甚至破坏系统。如果所有工具共享同一套安全策略，要么过于宽松导致高风险操作不受控，要么过于严格导致低风险操作也需要频繁审批。

## 解法

按执行位置和风险等级将工具分为四层，每层有独立的安全策略：

```typescript
enum ToolHostLayer {
  REMOTE = 1,   // 云端执行，API 调用
  LOCAL = 2,    // 本地 IDE/CLI 进程
  SIDECAR = 3,  // 独立沙箱进程
  EXTERNAL = 4  // 外部协议（MCP 等）
}
```

工具调度器（Tool Dispatcher）在执行前先确定目标工具属于哪一层，然后调用该层的安全检查：

```typescript
interface ToolHost {
  layer: ToolHostLayer;
  listTools(): ToolDefinition[];
  runTool(name: string, input: object): Promise<ToolResult>;
  checkSafety?(name: string, input: object): Promise<SafetyLevel>;
}

class LayeredToolDispatcher {
  private hosts: Map<ToolHostLayer, ToolHost>;

  async dispatch(toolName: string, input: object): Promise<ToolResult> {
    const tool = this.findTool(toolName);
    const host = this.hosts.get(tool.hostLayer);

    if (host.checkSafety) {
      const safety = await host.checkSafety(toolName, input);
      if (safety === SafetyLevel.BLOCKED) throw new Error('Tool blocked');
      if (safety === SafetyLevel.NEEDS_APPROVAL) await this.requestApproval();
    }

    return host.runTool(toolName, input);
  }
}
```

## 权衡

分层带来的最大好处是职责隔离——REMOTE 层可以放心开放，SIDECAR 层可以严格限制，两者互不干扰。新增一类工具只需要决定它属于哪一层，安全策略自动继承，不用逐个工具配置。

代价主要有两方面。一是跨层通信开销：当一个任务需要先调用 REMOTE 层拿到数据、再传给 SIDECAR 层执行，数据序列化和传输会增加延迟。二是工具归属判断并不总是清晰的——比如一个既可以读也可以写的文件操作工具，是放在 LOCAL 层还是 SIDECAR 层？这类边界情况需要明确的分类规则，否则分层反而增加认知负担。

在实践中，大多数团队会发现 80% 的工具归属是显而易见的，需要讨论的只有剩下 20% 的边界工具。为这 20% 建立一条判断规则（例如"有任何写操作的工具默认归入 SIDECAR"）通常就够了。

## 实践参考

- **Augment**：Remote（WEB_SEARCH, GITHUB）/ Local（READ_FILE）/ Sidecar（SHELL）/ MCP
- **Claude Code**：类似思路，MCP 作为扩展层

## 适用场景

- 企业级 Agent 需要细粒度权限控制
- 工具集包含高风险操作（Shell、文件删除）
- 需要支持外部工具协议（如 MCP）
