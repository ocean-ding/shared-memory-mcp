# shared-memory-mcp

一个独立的、stdio 传输的 MCP 记忆服务。它把记忆写入调用者自己指定的目录，程序仓库与记忆数据分离，因此可以把这套能力分享给朋友，而不分享你的项目源码和现有记忆。

## 设计边界

- 仓库只放 MCP 程序、启动脚本、配置模板和通用策略。
- 每个使用者都有自己的 `MDCG_ROOT`，默认是 `~/.shared-memory-mcp/memory`；辅助状态默认放在同目录旁的隐藏 runtime 目录。
- 记忆目录不在 Git 仓库内，也不会自动扫描当前项目目录。
- 不要把 `business/memory/`、`~/.dsh/`、Harness 会话、日志、令牌或 `.env` 复制到本仓库。
- 本仓库保留 MIT 授权文件；当前运行代码基于本机使用的 `@furongjun1999/dsh-memory` 0.9.17 MCP 运行时，并保留上游归因信息。

## 环境要求

- Python 3.10 或更高版本
- 不需要安装第三方 Python 依赖即可运行 stdio MCP
- DeepSeek Harness、Claude Code、Codex CLI 等支持 stdio MCP 的宿主

## 本地验证

```bash
python3 scripts/smoke_test.py
```

该命令使用临时空记忆目录，只验证 MCP `initialize` 握手，不读取你的项目记忆。

## 启动 MCP

```bash
MDCG_ROOT="$HOME/.shared-memory-mcp/memory" \
  python3 scripts/run_mcp.py
```

不设置 `MDCG_ROOT` 时，启动脚本会使用 `~/.shared-memory-mcp/memory`，并自动设置独立的 `MDCG_AUX_ROOT`、`MDCG_STATE_ROOT`、`MDCG_DATA_ROOT`。如果要让多人共享同一份记忆，必须改成远程、带认证和命名空间隔离的 MCP 服务；不要通过共享本地目录或把你的记忆文件提交到 Git 来实现。

## DeepSeek Harness 配置

复制 [`dsh/cordis.patch.example.yml`](dsh/cordis.patch.example.yml) 中的配置到 Harness profile 的 `cordis.patch.yml`，并替换：

1. `args` 中仓库的绝对路径；
2. `cwd` 中仓库的绝对路径；
3. `MDCG_ROOT` 为朋友自己的私有记忆目录；
4. `MDCG_ACTOR` 为朋友自己的标识。

建议先保持 `MDCG_MCP_SURFACE: kernel`，确认能启动后再按需切换到 `full`。不同 Harness 版本的 MCP 配置字段可能略有差异，但核心是以 stdio 方式运行 `scripts/run_mcp.py`。

## 直接运行协议探针

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"manual","version":"0.1.0"}}}' \
  | python3 scripts/run_mcp.py
```

## 目录说明

```text
md_cg/                 MCP 记忆运行时源码
data/policy.json       通用策略，不包含个人记忆
scripts/run_mcp.py     使用独立记忆根目录启动服务
scripts/smoke_test.py  空目录握手自检
dsh/                   DeepSeek Harness 配置模板
```
