# Mini-Codex

**A Lightweight Coding Agent Harness Built from Scratch with Python**

Mini-Codex 是一个使用 Python 从零构建的轻量级 Coding Agent Harness 项目。

项目旨在通过工程实践理解和实现 Agent Runtime 的核心机制，包括 Agent Loop、LLM Client、Tool Registry、Tool Executor、Context Management 和 Permission System。

不同于直接使用 LangChain 或 LangGraph 等 Agent 框架，Mini-Codex 尝试自己实现 Agent 的核心执行机制，理解一个 Coding Agent 是如何接收任务、调用工具、执行操作、观察结果并持续迭代的。

## 1. Project Goals

本项目的主要目标：

- 理解 LLM Agent 的运行机制与 Harness 架构。
- 从零实现一个可扩展的 Agent Runtime。
- 实现 OpenAI-compatible LLM Client，接入真实大语言模型。
- 实现动态 Tool Registry 和 Tool Execution System。
- 构建具备文件操作和 Shell 执行能力的 Coding Agent。
- 探索 Context Management、Permission Control 和 Error Recovery 等核心机制。

**Design Principles**

- 不依赖 LangChain / LangGraph 实现核心 Runtime。
- 使用 Python 实现核心 Agent 执行逻辑。
- 通过统一接口隔离模型供应商。
- 使用 Pydantic 实现工具参数定义与校验。
- 使用 Mock 测试与真实 API 测试相结合的方式验证系统。
- 优先考虑工具执行安全性和可扩展性。

## 2. Architecture

```text
                    User Input
                        |
                        v
                 Agent Runtime
                        |
                 +------+------+
                 |             |
                 v             v
             Model Client   Tool Registry
                 |             |
                 v             v
             DeepSeek API  Tool Executor
                               |
                       +-------+-------+
                       |               |
                       v               v
                  Filesystem       Built-in Tools
                       |
                       v
                  Tool Result
                       |
                       v
                 Message History
                       |
                       v
                  Agent Loop
                       |
                       v
                  Final Answer
```

### Core Components

| Component | Responsibility |
|---|---|
| Agent Runtime | 管理 Agent Loop、消息历史和执行流程 |
| Model Client | 定义统一模型调用接口 |
| DeepSeek Client | 负责 DeepSeek API 请求和响应解析 |
| Tool Registry | 注册、管理和查询工具 |
| Tool Definition | 定义工具名称、描述、参数模型和执行函数 |
| Tool Executor | 校验参数、执行工具并处理异常 |
| Tool Result | 统一封装工具执行结果 |
| Filesystem Tools | 提供工作目录内的文件读取和写入能力 |

## 3. Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core development language |
| OpenAI Python SDK | OpenAI-compatible API client |
| DeepSeek API | LLM inference |
| Pydantic | Tool argument validation and schema generation |
| python-dotenv | Environment configuration |
| pytest | Unit testing |
| setuptools | Python package management |

## 4. Project Structure

```text
mini-codex/
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
│
├── src/
│   └── mini_codex/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── runtime.py
│       │   └── state.py
│       │
│       ├── model/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── deepseek.py
│       │   └── messages.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── definition.py
│       │   ├── registry.py
│       │   ├── executor.py
│       │   ├── result.py
│       │   └── builtin/
│       │       └── filesystem.py
│       │
│       ├── context/
│       │   ├── __init__.py
│       │   └── manager.py
│       │
│       ├── security/
│       │   ├── __init__.py
│       │   └── permission.py
│       │
│       └── storage/
│           ├── __init__.py
│           └── session.py
│
├── scripts/
│   └── test_filesystem_agent.py
│
└── tests/
    ├── test_python_environment.py
    ├── test_runtime.py
    ├── test_tools.py
    ├── test_deepseek_client.py
    └── test_filesystem.py
```

> Note: The structure above describes the planned and current project organization. Some modules are reserved for future implementation.

## 5. Getting Started

### Requirements

- Python 3.11+
- pip
- A DeepSeek API Key

### 5.1 Clone the Repository

```bash
git clone <your-repository-url>
cd mini-codex
```

### 5.2 Create Virtual Environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5.3 Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 5.4 Configure Environment Variables

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
```

Never commit your `.env` file or expose your API Key.

## 6. Current Features

### 6.1 Agent Runtime

Implemented a basic Agent Loop:

1. Receive user input.
2. Send message history to the LLM.
3. Parse the model response.
4. Execute requested tool calls.
5. Append tool results to message history.
6. Send updated history back to the LLM.
7. Return the final answer.

The Runtime also supports a configurable maximum execution step count.

### 6.2 LLM Client

Implemented a DeepSeek API client using the OpenAI Python SDK.

Features:

- OpenAI-compatible Chat Completions API integration.
- Internal message serialization.
- Text response parsing.
- Tool Call response parsing.
- Tool Schema transmission.
- Tool Call history serialization.

### 6.3 Tool System

Implemented a modular Tool System.

**Tool Definition**

Each tool consists of:

- Name
- Description
- Pydantic argument model
- Python execution function

**Tool Registry**

Supports:

- Dynamic tool registration.
- Tool lookup.
- Duplicate registration protection.
- OpenAI-compatible Function Calling Schema generation.

**Tool Executor**

Supports:

- Argument validation.
- Tool execution.
- Unified execution results.
- Exception handling.

### 6.4 Filesystem Tools

Implemented the first two filesystem tools:

| Tool | Description |
|---|---|
| `read_file` | Read a text file inside the workspace |
| `write_file` | Create or write a file inside the workspace |

Security measures in the current implementation:

- Resolve relative paths.
- Reject paths outside the configured workspace.
- Reject absolute paths outside the workspace.
- Resolve symbolic links before checking the final path.

The current implementation is a foundational workspace boundary, not yet a hardened sandbox for hostile concurrent workloads.

## 7. Running Tests

Run all tests:

```bash
pytest -v
```

Run specific module tests:

```bash
pytest tests/test_runtime.py -v
pytest tests/test_tools.py -v
pytest tests/test_deepseek_client.py -v
pytest tests/test_filesystem.py -v
```

The project currently has automated tests covering:

- Python environment.
- Agent tool calling.
- Message history preservation.
- Tool registration.
- Duplicate tool registration.
- Tool Schema generation.
- Successful tool execution.
- Invalid tool arguments.
- Unknown tools.
- DeepSeek text response parsing.
- DeepSeek Tool Call parsing.
- Tool history serialization.
- Filesystem read and write.
- Path traversal protection.
- Absolute path protection.

## 8. Running the DeepSeek Client

A minimal example:

```python
from mini_codex.model.deepseek import DeepSeekClient
from mini_codex.model.messages import Message

client = DeepSeekClient()

result = client.complete([
    Message(
        role="user",
        content="请只回答 OK"
    )
])

print(result.content)
```

Expected output:

```text
OK
```

## 9. Running Filesystem Agent

A basic integration example is available in:

```text
scripts/test_filesystem_agent.py
```

Run:

```bash
python scripts/test_filesystem_agent.py
```

The example registers filesystem tools and asks DeepSeek to read the project's README.

The Agent can then use the Tool Calling mechanism to request file access.

## 10. Development Roadmap

| Phase | Task | Status |
|---|---|---|
| Task 001 | Project Initialization | Completed |
| Task 002 | Basic Agent Loop | Completed |
| Task 003 | Tool Registry and Executor | Completed |
| Task 004 | DeepSeek LLM Client | Completed |
| Task 005.1 | Filesystem Tools | Completed |
| Task 005.2 | Filesystem Agent Integration | In Progress |
| Task 005.3 | Shell Execution Tool | Planned |
| Task 006 | Context Management | Planned |
| Task 007 | Permission System | Planned |
| Task 008 | Error Recovery | Planned |
| Task 009 | Evaluation and Observability | Planned |
| Task 010 | CLI and End-to-End Workflow | Planned |

### Future Improvements

- Shell Tool with timeout and controlled execution.
- Workspace-level permission management.
- Context window management and message compression.
- Session persistence.
- Tool execution recovery and retry policies.
- Agent execution tracing and observability.
- End-to-end Coding Agent evaluation.

## 11. Security Considerations

Coding Agents can execute operations that affect the filesystem and runtime environment. Security is therefore a core part of the project.

Planned and ongoing improvements:

- Workspace isolation.
- Path traversal protection.
- Symbolic link handling.
- Shell command timeout.
- Permission checks before sensitive operations.
- Execution limits.
- Clear separation between model decisions and runtime authorization.

A model-generated Tool Call should never be treated as automatic authorization to execute a potentially dangerous operation.

## 12. Learning Objectives

This project is also an engineering learning exercise.

The implementation focuses on understanding:

- How an Agent Loop works.
- How LLM Function Calling works.
- How a Tool Registry is designed.
- How tool arguments are validated.
- How the Runtime manages message history.
- How an LLM Client abstracts model providers.
- How Coding Agents interact with files and execution environments.
- How permissions and security boundaries should be designed.

The long-term goal is to build a minimal but extensible Coding Agent Harness and understand the engineering principles behind production-grade Agent systems.

---

**Mini-Codex — Build an Agent Harness, One Component at a Time.**