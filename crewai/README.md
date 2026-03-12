# ActionGate + CrewAI

Use [ActionGate](https://api.actiongate.xyz) as a safety layer in a [CrewAI](https://docs.crewai.com/) multi-agent crew.

ActionGate provides three MCP tools for autonomous agent wallets:

- **risk_score** — Evaluate the risk of a proposed action before execution
- **simulate** — Estimate costs and failure probability for a transaction
- **policy_gate** — Apply policy checks and return allow/deny/allow-with-limits

## Setup

```bash
pip install crewai crewai-tools mcp
export OPENAI_API_KEY="sk-..."
```

## Quick Start

CrewAI has native MCP support. Just point an agent at ActionGate's URL:

```python
from crewai import Agent
from crewai.mcp import MCPServerHTTP

actiongate = MCPServerHTTP(
    url="https://api.actiongate.xyz/mcp",
    streamable=True,
    cache_tools_list=True,
)

treasurer = Agent(
    role="Treasury Safety Officer",
    goal="Evaluate wallet transactions for risk before approving execution.",
    backstory="You are the safety officer for an autonomous agent treasury.",
    mcps=[actiongate],
)
```

Or even simpler with the string shorthand:

```python
treasurer = Agent(
    role="Treasury Safety Officer",
    goal="Evaluate wallet transactions for risk before approving execution.",
    backstory="You are the safety officer for an autonomous agent treasury.",
    mcps=["https://api.actiongate.xyz/mcp"],
)
```

## Run the Full Example

```bash
python actiongate_crew.py
```

The example sets up a two-agent crew:
1. **Treasury Safety Officer** — uses ActionGate to evaluate a proposed Uniswap swap (risk score, simulation, policy check)
2. **Transaction Executor** — acts on the safety officer's approval or rejection

## Free Tier

No API key or signup needed. ActionGate includes a free tier: 10 risk_score, 10 simulate, and 5 policy_gate calls per agent per day. Paid calls available via [x402](https://www.x402.org/) micropayments (USDC on Base).

## Links

- [ActionGate Docs](https://api.actiongate.xyz/docs)
- [CrewAI MCP Docs](https://docs.crewai.com/en/mcp/overview)
