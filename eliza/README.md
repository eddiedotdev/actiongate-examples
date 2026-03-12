# ActionGate + Eliza (elizaOS)

Use [ActionGate](https://api.actiongate.xyz) as a safety layer in an [Eliza](https://github.com/elizaOS/eliza) agent via the [eliza-plugin-mcp](https://github.com/fleek-platform/eliza-plugin-mcp).

ActionGate provides three MCP tools for autonomous agent wallets:

- **risk_score** — Evaluate the risk of a proposed action before execution
- **simulate** — Estimate costs and failure probability for a transaction
- **policy_gate** — Apply policy checks and return allow/deny/allow-with-limits

## Setup

```bash
# In your Eliza project
npm install @fleek-platform/eliza-plugin-mcp
npm install -D supergateway
```

## Quick Start

Add ActionGate to your character's MCP config:

```json
{
  "name": "My Agent",
  "plugins": ["@fleek-platform/eliza-plugin-mcp"],
  "settings": {
    "mcp": {
      "servers": {
        "actiongate": {
          "type": "stdio",
          "name": "ActionGate Safety Layer",
          "command": "npx",
          "args": ["-y", "supergateway", "--streamableHttp", "https://api.actiongate.xyz/mcp"],
          "timeout": 30
        }
      }
    }
  }
}
```

This gives your Eliza agent access to `risk_score`, `simulate`, and `policy_gate` tools automatically by bridging ActionGate's Streamable HTTP endpoint into Eliza's supported `stdio` transport.

## Example Character

See [character.json](./character.json) for a complete character config that acts as a treasury guardian — it evaluates every proposed wallet transaction using ActionGate before allowing execution.

## Usage

```bash
# Start your Eliza agent with the ActionGate character
elizaos agent start --path ./character.json
```

The agent will automatically have access to ActionGate's tools and can use them to evaluate transactions in conversation.

## Free Tier

No API key or signup needed. ActionGate includes a free tier: 10 risk_score, 10 simulate, and 5 policy_gate calls per agent per day. Paid calls available via [x402](https://www.x402.org/) micropayments (USDC on Base).

## Links

- [ActionGate Docs](https://api.actiongate.xyz/docs)
- [Eliza Plugin MCP](https://github.com/fleek-platform/eliza-plugin-mcp)
- [elizaOS Documentation](https://eliza.how/docs/core/plugins)
