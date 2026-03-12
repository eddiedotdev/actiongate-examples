# ActionGate Examples

Integration examples for [ActionGate](https://api.actiongate.xyz) — a pre-execution safety layer for autonomous agent wallets.

ActionGate provides three MCP tools:

| Tool | Description | Free Tier |
|------|-------------|-----------|
| `risk_score` | Evaluate the risk of a proposed agent action | 10 calls/day |
| `simulate` | Estimate costs and failure probability | 10 calls/day |
| `policy_gate` | Apply policy checks (allow / deny / allow-with-limits) | 5 calls/day |

No API key or signup needed. Free tier included. Paid calls via [x402](https://www.x402.org/) micropayments (USDC on Base).

## Framework Examples

| Framework | Directory | Description |
|-----------|-----------|-------------|
| [LangChain](./langchain/) | `langchain/` | ReAct agent using langchain-mcp-adapters |
| [CrewAI](./crewai/) | `crewai/` | Multi-agent crew with a treasury safety officer |
| [Eliza (elizaOS)](./eliza/) | `eliza/` | Character config with MCP plugin |
| [OpenAI Agents SDK](./openai-agents/) | `openai-agents/` | Agent with native MCP support |

## MCP Endpoint

All examples connect to the same endpoint:

```
https://api.actiongate.xyz/mcp
```

ActionGate uses [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http) transport. No authentication required for the free tier.

## Client Config (for any MCP-compatible client)

```json
{
  "mcpServers": {
    "actiongate": {
      "url": "https://api.actiongate.xyz/mcp"
    }
  }
}
```

## Links

- [ActionGate API](https://api.actiongate.xyz)
- [Documentation](https://api.actiongate.xyz/docs)
- [Pricing](https://api.actiongate.xyz/pricing)
- [Server Card](https://api.actiongate.xyz/.well-known/mcp/server-card.json)
- [Discovery JSON](https://api.actiongate.xyz/.well-known/agent.json)
