# Proxy Config Guide

This guide is the operator path for the BYO-API ActionGate flow:

1. Pick an upstream endpoint.
2. Describe its request and response contract in `proxy-config.json`.
3. Set a price and optional free-tier limit.
4. Start ActionGate and expose the same tool over REST (`/proxy/:toolName`) and MCP (`/mcp`).

Start with the copyable example at [examples/proxy-config.public-api.json](https://api.actiongate.xyz/examples/proxy-config.public-api.json).

## Full Schema

`proxy-config.json` is a single JSON object:

```json
{
  "serviceName": "My Paid API",
  "serviceDescription": "ActionGate deployment for my upstream APIs.",
  "defaultFreeTierCallsPerDay": 50,
  "subnetMaxCallsPerDay": 200,
  "tools": [
    {
      "name": "summarize",
      "description": "Summarize long text with my upstream model.",
      "targetUrl": "https://example.com/v1/summarize",
      "method": "POST",
      "priceUsd": "0.25",
      "freeTierLimit": 5,
      "forwardHeaders": ["authorization", "x-upstream-api-key"],
      "inputSchema": {
        "type": "object",
        "properties": {
          "text": { "type": "string" }
        },
        "required": ["text"],
        "additionalProperties": false
      },
      "responseSchema": {
        "type": "object",
        "properties": {
          "summary": { "type": "string" }
        },
        "required": ["summary"],
        "additionalProperties": false
      },
      "examples": {
        "requestBody": {
          "text": "Large source document"
        },
        "responseBody": {
          "summary": "Condensed output"
        }
      }
    }
  ]
}
```

## Field Reference

Top-level fields:

- `serviceName`: human-readable deployment name used in discovery and public docs.
- `serviceDescription`: short description shown on landing/docs/discovery surfaces.
- `defaultFreeTierCallsPerDay`: default free calls per day when a tool does not define `freeTierLimit`.
- `subnetMaxCallsPerDay`: shared subnet ceiling used by the free-tier quota store.
- `tools`: array of paid proxy tools.

Per-tool fields:

- `name`: stable tool ID. This becomes `/proxy/<name>` and the MCP tool name.
- `description`: user-facing description for docs, discovery, and MCP metadata.
- `targetUrl`: upstream target. Use an internal path like `/v1/risk-score` or an external HTTPS URL like `https://example.com/v1/summarize`.
- `method`: HTTP verb for the proxy call. Supported: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`. Defaults to `POST`.
- `priceUsd`: per-call price in USD string form, for example `"0.25"`.
- `freeTierLimit`: optional per-tool daily limit. When omitted, the deployment-level free-tier budget applies.
- `forwardHeaders`: optional allowlist of incoming request headers to pass upstream. ActionGate lowercases and deduplicates them.
- `inputSchema`: JSON Schema subset describing the incoming request. For `GET` and `DELETE`, properties map to query params. For mutation methods, the payload is sent as JSON.
- `responseSchema`: JSON Schema subset for the upstream response body. This feeds generated docs and machine-readable metadata.
- `examples`: optional example payloads.
- `examples.requestBody`: example JSON request body for mutation methods.
- `examples.requestQuery`: example query object for `GET` and `DELETE`.
- `examples.responseBody`: example JSON response from the upstream.

Supported JSON Schema keywords in `inputSchema` and `responseSchema`:

- `type`
- `description`
- `properties`
- `required`
- `items`
- `additionalProperties`
- `enum`

Supported JSON Schema types:

- `object`
- `array`
- `string`
- `number`
- `integer`
- `boolean`

## Step-by-Step: Make `https://example.com/v1/summarize` Paid

1. Copy the example config.

```bash
cp examples/proxy-config.public-api.json proxy-config.json
```

2. Replace one tool with your upstream endpoint.

```json
{
  "name": "summarize",
  "description": "Summarize long customer notes.",
  "targetUrl": "https://example.com/v1/summarize",
  "method": "POST",
  "priceUsd": "0.25",
  "freeTierLimit": 5,
  "forwardHeaders": ["authorization", "x-upstream-api-key"],
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Raw text to summarize."
      },
      "style": {
        "type": "string",
        "enum": ["short", "bullets", "executive"]
      }
    },
    "required": ["text"],
    "additionalProperties": false
  },
  "responseSchema": {
    "type": "object",
    "properties": {
      "summary": { "type": "string" },
      "tokens_used": { "type": "integer" }
    },
    "required": ["summary"],
    "additionalProperties": false
  },
  "examples": {
    "requestBody": {
      "text": "Quarterly board update...",
      "style": "executive"
    },
    "responseBody": {
      "summary": "Revenue increased while burn stayed flat.",
      "tokens_used": 418
    }
  }
}
```

3. Start the API server with that config available in the repo root, or point `PROXY_CONFIG_PATH` at it.

4. ActionGate will expose:

- `POST /proxy/summarize`
- MCP tool `summarize` at `/mcp`
- discovery metadata at `/.well-known/agent.json`

5. Clients can use the free tier first, then pay with x402 or prepaid API credits once quota is exhausted.

## Internal vs External Targets

Internal targets:

- Example: `"/v1/risk-score"`
- ActionGate invokes them with `fastify.inject`.
- Use these when the target is another route inside the same ActionGate deployment.

External targets:

- Example: `"https://example.com/v1/summarize"`
- ActionGate proxies them with `fetch`.
- Use these when you want ActionGate in front of a third-party or separately hosted API.

Rule of thumb:

- If your upstream already exists elsewhere, use `https://...`.
- If the target is implemented inside this Fastify app, use `/...`.

## Per-Tool Free Tier Limits

You have two free-tier controls:

- Deployment default: `defaultFreeTierCallsPerDay`
- Tool override: `freeTierLimit`

Example:

```json
{
  "defaultFreeTierCallsPerDay": 50,
  "tools": [
    { "name": "cheap_lookup", "freeTierLimit": 10 },
    { "name": "expensive_generation", "freeTierLimit": 2 }
  ]
}
```

If a tool sets `freeTierLimit`, that value becomes the canonical per-tool free-tier budget used by public metadata and enforcement.

## `forwardHeaders`

`forwardHeaders` is an explicit allowlist of client headers that ActionGate may pass to the upstream.

Use it when:

- the upstream requires its own bearer token
- the upstream expects a customer-specific API key
- you want to preserve trace or correlation headers

Example:

```json
{
  "forwardHeaders": ["authorization", "x-upstream-api-key", "x-trace-id"]
}
```

Then a caller can hit ActionGate with:

```bash
curl -X POST http://localhost:8787/proxy/inspect_request \
  -H "content-type: application/json" \
  -H "authorization: Bearer upstream-secret" \
  -H "x-upstream-api-key: customer-key-123" \
  -d '{"message":"hello"}'
```

ActionGate forwards only the headers you opted into. Everything else stays local.

## Test Locally Before Deploying

For a `GET` tool:

```bash
curl "http://localhost:8787/proxy/list_posts?userId=1&_limit=3"
```

For a `POST` tool:

```bash
curl -X POST http://localhost:8787/proxy/create_post \
  -H "content-type: application/json" \
  -d '{"title":"Launch","body":"Ship the proxy","userId":42}'
```

If the free tier is exhausted or disabled, ActionGate returns `402 Payment Required`. Retry with an x402-capable client or a prepaid API key.

## How Pricing Flows Through x402 And Credits

Every tool has one source-of-truth price: `priceUsd`.

That price is used by:

- REST proxy billing on `/proxy/:toolName`
- MCP tool billing on `/mcp`
- x402 payment requirements in `402` responses
- prepaid API credit debits
- public pricing/discovery metadata

Flow:

1. Client calls `/proxy/:toolName` or the MCP tool.
2. If free tier remains, the request executes immediately.
3. If not, ActionGate returns a `402` with x402 payment requirements.
4. The client either:
- retries with `PAYMENT-SIGNATURE`, or
- sends an `X-API-Key` backed by prepaid Stripe credits.
5. ActionGate settles the charge, proxies the upstream request, and returns the upstream response plus a signed receipt.

## Production Environment Variables

Custom proxy deployments usually need:

- `PROXY_CONFIG_PATH`: optional path to your custom config if it is not `./proxy-config.json`
- `PUBLIC_BASE_URL`: canonical public origin used in docs/discovery output
- `ACTIONGATE_INTERNAL_AUTH_SECRET`: required in production
- `X402_ENFORCED`: keep `true` if you want payment enforcement
- `PAYTO_ADDRESS`: payout address for x402 settlements
- `FACILITATOR_URL`: x402 facilitator endpoint
- `X402_NETWORK`: payment network, defaults to `eip155:84532`
- `X402_ASSET`: payment asset, defaults to `USDC`
- `FREE_TIER_ENABLED`: set `false` to disable free calls entirely
- `FREE_TIER_MAX_CALLS_PER_DAY`: deployment-wide fallback free-tier limit
- `FREE_TIER_PER_TOOL_LIMITS`: optional env override such as `summarize:5,translate:10`
- `BILLING_ENABLED`: set `true` to enable prepaid API credits
- `STRIPE_SECRET_KEY`: required when billing is enabled
- `STRIPE_WEBHOOK_SECRET`: required when billing is enabled
- `CREDIT_STORE_FILE_PATH`: file-backed credit storage path when not using another store
- `X402_SETTLEMENT_STORE_FILE_PATH`: settlement storage path
- `X402_USAGE_ANALYTICS_FILE_PATH`: usage analytics storage path
- `ACTIONGATE_POSTHOG_ENABLED`: set `true` to emit PostHog product analytics
- `ACTIONGATE_POSTHOG_HOST`: PostHog ingestion host such as `https://us.i.posthog.com`
- `ACTIONGATE_POSTHOG_PROJECT_KEY`: PostHog project token for browser and server capture

Recommended production minimum:

```bash
PUBLIC_BASE_URL=https://api.example.com
PROXY_CONFIG_PATH=/etc/actiongate/proxy-config.json
ACTIONGATE_INTERNAL_AUTH_SECRET=replace-me
PAYTO_ADDRESS=0xYourPayoutAddress
FACILITATOR_URL=https://your-facilitator.example.com
X402_ENFORCED=true
BILLING_ENABLED=true
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Deployment Checklist

- `proxy-config.json` exists and validates
- every tool has the right `targetUrl`, `method`, and `priceUsd`
- `forwardHeaders` only includes headers you intentionally want upstream
- free-tier values match your pricing strategy
- `PUBLIC_BASE_URL` points at the public domain
- x402 env vars are set for paid traffic
- billing env vars are set if you want prepaid API credits
- local `curl` tests work before you deploy
