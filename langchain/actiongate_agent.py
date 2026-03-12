"""
ActionGate + LangChain Example
==============================

Uses langchain-mcp-adapters to load ActionGate's MCP tools (risk_score,
simulate, policy_gate) into a LangGraph ReAct agent.

The agent evaluates a proposed wallet transaction for safety before execution.

Requirements:
    pip install langchain-mcp-adapters langchain-openai langgraph

Environment:
    OPENAI_API_KEY  — Your OpenAI API key
"""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

ACTIONGATE_MCP_URL = "https://api.actiongate.xyz/mcp"


async def main():
    model = ChatOpenAI(model="gpt-4o", temperature=0)

    async with MultiServerMCPClient(
        {
            "actiongate": {
                "transport": "streamable_http",
                "url": ACTIONGATE_MCP_URL,
            }
        }
    ) as client:
        tools = await client.get_tools()
        agent = create_react_agent(model, tools)

        # Example: an autonomous agent wants to swap 500 USDC for ETH on Uniswap.
        # Ask the agent to evaluate the action before executing it.
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "I'm an autonomous trading agent and I want to swap "
                            "500 USDC for ETH on Uniswap V3 on Base. The target "
                            "contract is 0x2626664c2603336E57B271c5C0b26F421741e481. "
                            "Before I execute, please:\n"
                            "1. Score the risk of this action\n"
                            "2. Simulate the transaction to estimate costs and failure probability\n"
                            "3. Check it against policy rules\n"
                            "Then give me a final recommendation."
                        ),
                    }
                ]
            }
        )

        for msg in result["messages"]:
            print(f"\n[{msg.type}] {msg.content}")


if __name__ == "__main__":
    asyncio.run(main())
