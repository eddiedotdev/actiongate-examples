# ActionGate Examples

[![actiongate-examples MCP server](https://glama.ai/mcp/servers/eddiedotdev/actiongate-examples/badges/score.svg)](https://glama.ai/mcp/servers/eddiedotdev/actiongate-examples)

Integration examples for [ActionGate](https://actiongate.xyz) — an x402 + Stripe payment proxy for REST APIs and MCP tools.

ActionGate ships with three built-in safety tools as its default example config:

| Tool | Description | Free Tier |
|------|-------------|-----------|
| `risk_score` | Evaluate the risk of a proposed agent action | 10 calls/day |
| `simulate` | Estimate costs and failure probability | 10 calls/day |
| `policy_gate` | Apply policy checks (allow / deny / allow-with-limits) | 5 calls/day |

## Payment Options

ActionGate supports two payment methods:

- **Free tier** — no signup or API key needed. Rate-limited per tool.
- **x402 micropayments** — pay-per-call with USDC on Base. No account required.
- **Stripe-funded API credits** — buy prepaid credits at [`/billing`](https://api.actiongate.xyz/billing), receive an `ag_live_...` API key, and calls deduct from your balance.

## Framework Examples

| Framework | Directory | Description |
|-----------|-----------|-------------|
| [LangChain](https://python.langchain.com/) | `langchain/` | ReAct agent using langchain-mcp-adapters |
| [CrewAI](https://www.crewai.com/) | `crewai/` | Multi-agent crew with a treasury safety officer |
| [Eliza (elizaOS)](https://elizaos.ai/) | `eliza/` | Character config with MCP plugin |
| [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) | `openai-agents/` | Agent with native MCP support |

## SDKs

### TypeScript

```bash
npm install actiongate-sdk
```

```typescript
import { ActionGateClient } from "@actiongate/sdk";

const client = new ActionGateClient({
  baseUrl: "https://api.actiongate.xyz",
  apiKey: process.env.ACTIONGATE_API_KEY, // optional — omit for free tier or x402
});

const result = await client.policyGate({
  actor: { actor_id: "agent_ops_02" },
  action: {
    action_type: "transfer",
    network: "base",
    asset_symbol: "USDC",
    amount: "150000",
    target: "0x1111111111111111111111111111111111111111",
  },
  policy: { policy_id: "treasury_default_v1" },
});
```

### Python

```bash
pip install actiongate-sdk
```

```python
from actiongate_sdk import ActionGateClient

client = ActionGateClient(
    base_url="https://api.actiongate.xyz",
    api_key=None,  # optional — omit for free tier or x402
)

result = client.policy_gate({
    "actor": {"actor_id": "agent_ops_02"},
    "action": {
        "action_type": "transfer",
        "network": "base",
        "asset_symbol": "USDC",
        "amount": "150000",
        "target": "0x1111111111111111111111111111111111111111",
    },
    "policy": {"policy_id": "treasury_default_v1"},
})
```

## MCP Endpoint

All examples connect to the same endpoint:

```
https://api.actiongate.xyz/mcp
```

ActionGate uses [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http) transport. No authentication required for the free tier.

### Remote MCP (any MCP-compatible client)

```json
{
  "mcpServers": {
    "actiongate": {
      "url": "https://api.actiongate.xyz/mcp"
    }
  }
}
```

### Local stdio package

```bash
npm install -g actiongate-mcp
```

```json
{
  "mcpServers": {
    "actiongate": {
      "command": "npx",
      "args": ["actiongate-mcp"],
      "env": {
        "PAYTO_ADDRESS": "0xYourWallet",
        "ACTIONGATE_BASE_URL": "https://api.actiongate.xyz"
      }
    }
  }
}
```

### Registry namespace

```
xyz.actiongate.api/actiongate
```

### MCP server quality

This public examples repo includes [`glama.json`](glama.json) metadata for Glama indexing of the hosted ActionGate MCP endpoint. The production ActionGate implementation is maintained separately; this repo documents client integrations, proxy configuration, the hosted endpoint, maintainers, MIT license, tool annotations, input schemas, output schemas, and the intended pre-execution flow:

1. Call `risk_score` to classify the proposed action.
2. Call `simulate` to estimate cost, failure probability, and side effects.
3. Call `policy_gate` to return a final policy decision before execution.

All three default MCP tools are pre-execution checks. They do not submit transactions, move funds, or mutate policy packs.

## BYO API (Proxy Config)

ActionGate can proxy any upstream API. Operators define tools in a `proxy-config.json` and ActionGate exposes them over REST (`/proxy/:toolName`) and MCP (`/mcp`) with x402 or Stripe billing attached.

See [`docs/proxy-config-guide.md`](docs/proxy-config-guide.md) for the full schema and walkthrough.

Quick example:

```json
{
  "serviceName": "My Paid API",
  "serviceDescription": "ActionGate deployment for my upstream APIs.",
  "defaultFreeTierCallsPerDay": 50,
  "tools": [
    {
      "name": "summarize",
      "description": "Summarize long text with my upstream model.",
      "targetUrl": "https://example.com/v1/summarize",
      "method": "POST",
      "priceUsd": "0.25",
      "freeTierLimit": 5,
      "inputSchema": {
        "type": "object",
        "properties": { "text": { "type": "string" } },
        "required": ["text"]
      }
    }
  ]
}
```

## Pricing

The bundled safety tools use the following pricing:

| Tool | Price |
|------|-------|
| `risk_score` | $0.02/call |
| `simulate` | $0.05–$1.00/call (tiered by action complexity) |
| `policy_gate` | $0.03/call |

Custom proxy deployments set their own pricing per tool in `proxy-config.json`.

## Links

- [ActionGate API](https://api.actiongate.xyz)
- [Documentation](https://api.actiongate.xyz/docs)
- [Pricing](https://api.actiongate.xyz/pricing)
- [OpenAPI Spec](https://api.actiongate.xyz/docs/openapi.yaml)
- [Proxy Config Guide](docs/proxy-config-guide.md)
- [Server Card](https://api.actiongate.xyz/.well-known/mcp/server-card.json)
- [Discovery JSON](https://api.actiongate.xyz/.well-known/agent.json)
- [Billing Portal](https://api.actiongate.xyz/billing)

## License

MIT. See [`LICENSE`](LICENSE).
