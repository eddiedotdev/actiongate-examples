# ActionGate + OpenAI Agents SDK

Use [ActionGate](https://api.actiongate.xyz) as a safety layer in an [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) agent via native MCP support.

ActionGate provides three MCP tools for autonomous agent wallets:

- **risk_score** — Evaluate the risk of a proposed action before execution
- **simulate** — Estimate costs and failure probability for a transaction
- **policy_gate** — Apply policy checks and return allow/deny/allow-with-limits

## Setup

```bash
pip install openai-agents
export OPENAI_API_KEY="sk-..."
```

## Quick Start

```python
from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerStreamableHttp

actiongate = MCPServerStreamableHttp(
    params={"url": "https://api.actiongate.xyz/mcp"},
    name="actiongate",
)

agent = Agent(
    name="Treasury Guardian",
    instructions="Evaluate wallet transactions using ActionGate tools before execution.",
    mcp_servers=[actiongate],
    model_settings=ModelSettings(tool_choice="required"),
)

async with actiongate:
    result = await Runner.run(
        agent,
        input="Score the risk of swapping 500 USDC for ETH on Uniswap on Base.",
    )
    print(result.final_output)
```

## Run the Full Example

```bash
python actiongate_agent.py
```

The example agent evaluates a proposed Uniswap swap by calling all three ActionGate tools (risk score, simulation, policy check) and provides a final APPROVE or REJECT decision.

## Free Tier

No API key or signup needed. ActionGate includes a free tier: 10 risk_score, 10 simulate, and 5 policy_gate calls per agent per day. Paid calls available via [x402](https://www.x402.org/) micropayments (USDC on Base).

## Links

- [ActionGate Docs](https://api.actiongate.xyz/docs)
- [OpenAI Agents SDK — MCP](https://openai.github.io/openai-agents-python/mcp/)
