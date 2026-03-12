"""
ActionGate + OpenAI Agents SDK Example
=======================================

Uses the OpenAI Agents SDK's native MCP support to connect an agent to
ActionGate for pre-execution safety checks on wallet transactions.

Requirements:
    pip install openai-agents

Environment:
    OPENAI_API_KEY  — Your OpenAI API key
"""

import asyncio

from agents import Agent, Runner, ModelSettings
from agents.items import ToolCallItem
from agents.mcp import MCPServerStreamableHttp

REQUIRED_ACTIONGATE_TOOLS = {"risk_score", "simulate", "policy_gate"}


def get_called_tool_names(result) -> set[str]:
    tool_names: set[str] = set()

    for item in result.new_items:
        if not isinstance(item, ToolCallItem):
            continue

        raw_item = item.raw_item
        if isinstance(raw_item, dict):
            tool_name = raw_item.get("name") or raw_item.get("tool_name")
        else:
            tool_name = getattr(raw_item, "name", None) or getattr(raw_item, "tool_name", None)

        if isinstance(tool_name, str):
            tool_names.add(tool_name)

    return tool_names


async def main():
    # Connect to ActionGate's MCP endpoint
    actiongate = MCPServerStreamableHttp(
        params={"url": "https://api.actiongate.xyz/mcp"},
        name="actiongate",
    )

    # Create an agent with ActionGate tools
    agent = Agent(
        name="Treasury Guardian",
        instructions=(
            "You are a safety officer for an autonomous agent wallet. "
            "Before any transaction is executed, you MUST:\n"
            "1. Use risk_score to evaluate the risk level of the action\n"
            "2. Use simulate to estimate gas costs and failure probability\n"
            "3. Use policy_gate to check if the action complies with policy\n\n"
            "Based on all three checks, provide a clear APPROVE or REJECT "
            "decision with detailed reasoning."
        ),
        mcp_servers=[actiongate],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Example: evaluate a proposed swap
    async with actiongate:
        result = await Runner.run(
            agent,
            input=(
                "I want to swap 500 USDC for ETH on Uniswap V3 on Base. "
                "The target contract is 0x2626664c2603336E57B271c5C0b26F421741e481. "
                "Please evaluate this transaction for safety."
            ),
        )

        called_tools = get_called_tool_names(result)
        missing_tools = REQUIRED_ACTIONGATE_TOOLS - called_tools
        if missing_tools:
            missing_list = ", ".join(sorted(missing_tools))
            raise RuntimeError(
                "The agent did not run every required ActionGate safety check. "
                f"Missing tool calls: {missing_list}."
            )

        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
