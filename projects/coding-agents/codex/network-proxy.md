# Network Proxy MITM 代理架构

> **Evidence Status** — grounded. 基于 Codex 参考源码观察整理。

## 概述

Codex 在沙箱层之上实现了独立的网络控制层，通过本地代理拦截所有出站流量，实现域名级访问策略。

## 代理架构

- sandbox 内进程的所有网络请求被重定向到本地 SOCKS5 + HTTP CONNECT 代理
- 代理在 sandbox 外运行，拥有完整网络访问能力
- 与文件系统沙箱正交：两层控制可独立开启/关闭

## 域名级策略

`NetworkDomainPermissions` 支持 glob pattern 匹配（如 `*.github.com`）：
- **None**：未配置，走默认策略
- **Allow**：允许访问
- **Deny**：拒绝访问，Deny 优先于 Allow

## Loopback 特殊处理

localhost（`127.0.0.1`, `::1`）和非公网 IP 地址有独立判断逻辑，避免误拦本地开发服务。

## MITM TLS

`mitm.rs` 实现中间人证书注入：
- 对 HTTPS 流量进行 TLS 终结，提取目标域名
- 根据域名策略决定放行或拒绝
- 确保域名级策略对加密流量同样有效

## DeferredNetworkApproval

某些网络请求可在命令执行期间暂挂，命令完成后异步提交给用户审批。适用于非阻塞场景下的后置确认。

## 设计要点

网络代理层与文件系统沙箱共同构成双重隔离，但职责正交：文件系统沙箱控制本地资源访问，网络代理控制外部通信。任一层可独立禁用而不影响另一层。
