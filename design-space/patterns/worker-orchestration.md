# Worker Agent 编排 (Worker Orchestration)

> **Evidence Status** — grounded. Augment 通过 7 个 LOCAL_TOOL_TYPE 实现了完整 Worker 生命周期管理；Claude Code 通过 Agent 工具 + subagent_type 参数实现类似能力。两者路径不同但模式趋同。

当一个复杂任务需要拆分给多个 Agent 并行或串行执行时，核心问题是拆完之后怎么管：主 Agent 如何启动、监控、收集结果、处理失败、清理资源。Worker Orchestration 就是这套生命周期管理机制。

## 生命周期工具

主 Agent 通过一组标准化工具来编排 Worker：

```typescript
interface WorkerTools {
  start(config: WorkerConfig): Promise<WorkerId>;
  sendInstruction(id: WorkerId, instruction: string): Promise<void>;
  readState(id: WorkerId): Promise<WorkerState>;
  waitFor(id: WorkerId, timeout?: number): Promise<WorkerResult>;
  readEdits(id: WorkerId): Promise<Edit[]>;
  applyEdits(id: WorkerId, editIds: string[]): Promise<void>;
  stop(id: WorkerId): Promise<void>;
  delete(id: WorkerId): Promise<void>;
}
```

典型流程是：启动 Worker -> 等待完成 -> 审核编辑 -> 决定是否应用 -> 清理。其中"审核编辑"这一步是关键：主 Agent 对 Worker 产生的代码变更有最终决定权，而非自动应用。

## 编排模式

根据任务依赖关系，有三种常见拓扑：

**并行扇出**（Fan-out）适用于子任务之间没有依赖的场景，比如同时搜索多个代码库：

```
Main --+-- Worker 1 --+-- Main
       +-- Worker 2 --+
       +-- Worker 3 --+
```

**串行流水线**（Pipeline）适用于上游输出是下游输入的场景，比如"分析需求 -> 生成代码 -> 运行测试"：

```
Main -- Worker 1 -- Worker 2 -- Worker 3 -- Main
```

**监督者模式**（Supervisor）适用于需要动态调整的场景——主 Agent 持续观察 Worker 状态，根据进展决定是继续、调整指令还是提前终止：

```
Main (Supervisor)
  |
  +-- sendInstruction --> Worker (执行中)
  |
  +-- readState <-------- Worker (汇报)
  |
  +-- 决策: 继续/调整/停止
```

## 权衡

Worker 编排带来的最大收益是并行化和故障隔离：一个 Worker 失败不会污染其他 Worker 的上下文，主 Agent 可以决定重试或跳过。但代价也很实在：Worker 之间没有直接通信能力，所有协调必须经过主 Agent 中转，这在需要频繁交互的场景下会成为瓶颈。状态同步也存在延迟，readState 拿到的永远是某个时刻的快照而非实时状态。

此外，资源管理不能掉以轻心。Worker 必须有超时机制（waitFor 的 timeout 参数），并且确保无论成功还是失败都会被清理（delete），否则长时间运行的 Agent 会积累僵尸 Worker。

## 关键设计点

1. **编辑审核**：主 Agent 决定是否应用 Worker 的编辑，这是安全性的最后一道防线
2. **超时处理**：waitFor 必须有超时机制，避免无限等待
3. **资源清理**：确保 Worker 最终被删除，建议用 try/finally 模式
4. **状态可见**：readState 提供进度感知，让主 Agent 能做出及时决策

## 实践参考

- **Augment**：7 个 LOCAL_TOOL_TYPE (21-28) 实现完整生命周期
- **Claude Code**：Agent 工具 + subagent_type 参数
