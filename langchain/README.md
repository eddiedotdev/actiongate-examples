# ActionGate + LangChain

Use [ActionGate](https://api.actiongate.xyz) as a safety layer in a LangChain agent via [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters).

ActionGate provides three MCP tools for autonomous agent wallets:

- **risk_score** — Evaluate the risk of a proposed action before execution
- **simulate** — Estimate costs and failure probability for a transaction
- **policy_gate** — Apply policy checks and return allow/deny/allow-with-limits

## Setup

```bash
pip install langchain-mcp-adapters langchain-openai langgraph
export OPENAI_API_KEY="sk-..."
```

## Quick Start

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o")

async with MultiServerMCPClient({
    "actiongate": {
        "transport": "streamable_http",
        "url": "https://api.actiongate.xyz/mcp",
    }
}) as client:
    tools = await client.get_tools()
    agent = create_react_agent(model, tools)
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "Score the risk of swapping 500 USDC for ETH on Uniswap on Base."}]
    })
```

## Run the Full Example

```bash
python actiongate_agent.py
```

The example agent evaluates a proposed Uniswap swap by calling all three ActionGate tools (risk score, simulation, policy check) and then provides a final recommendation.

## Free Tier

No API key or signup needed. ActionGate includes a free tier: 10 risk_score, 10 simulate, and 5 policy_gate calls per agent per day. Paid calls available via [x402](https://www.x402.org/) micropayments (USDC on Base).

## Links

- [ActionGate Docs](https://api.actiongate.xyz/docs)
- [ActionGate Server Card](https://api.actiongate.xyz/.well-known/mcp/server-card.json)
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
