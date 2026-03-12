"""
ActionGate + CrewAI Example
============================

Uses CrewAI's native MCP support to connect a crew of agents to ActionGate
for pre-execution safety checks on wallet transactions.

A "treasurer" agent evaluates proposed spending using ActionGate's risk_score,
simulate, and policy_gate tools before the crew can proceed.

Requirements:
    pip install crewai crewai-tools mcp

Environment:
    OPENAI_API_KEY  — Your OpenAI API key
"""

from crewai import Agent, Task, Crew, Process
from crewai.mcp import MCPServerHTTP

# Connect to ActionGate's MCP endpoint
actiongate = MCPServerHTTP(
    url="https://api.actiongate.xyz/mcp",
    streamable=True,
    cache_tools_list=True,
)

# --- Agents ---

treasurer = Agent(
    role="Treasury Safety Officer",
    goal=(
        "Evaluate every proposed wallet transaction for risk, cost, and policy "
        "compliance before approving execution. Reject anything that fails checks."
    ),
    backstory=(
        "You are the safety officer for an autonomous agent treasury. "
        "No funds leave the wallet without your approval. You use ActionGate's "
        "risk_score, simulate, and policy_gate tools to evaluate every action."
    ),
    mcps=[actiongate],
    verbose=True,
)

executor = Agent(
    role="Transaction Executor",
    goal="Execute approved wallet transactions and report results.",
    backstory=(
        "You carry out transactions that the Treasury Safety Officer has approved. "
        "You never execute a transaction that hasn't been cleared by the safety officer."
    ),
    verbose=True,
)

# --- Tasks ---

safety_review = Task(
    description=(
        "A trading bot wants to swap 500 USDC for ETH on Uniswap V3 on Base. "
        "The target contract is 0x2626664c2603336E57B271c5C0b26F421741e481.\n\n"
        "Evaluate this action:\n"
        "1. Use risk_score to assess the risk level\n"
        "2. Use simulate to estimate gas costs and failure probability\n"
        "3. Use policy_gate to check if this action is allowed under policy\n\n"
        "Provide a clear APPROVE or REJECT decision with reasoning."
    ),
    expected_output=(
        "A structured safety report with risk score, simulation results, "
        "policy decision, and a final APPROVE or REJECT recommendation."
    ),
    agent=treasurer,
)

execution_plan = Task(
    description=(
        "Based on the safety review, either:\n"
        "- If APPROVED: outline the execution steps for the swap\n"
        "- If REJECTED: explain why the transaction was blocked and suggest alternatives"
    ),
    expected_output="An execution plan or rejection explanation.",
    agent=executor,
    context=[safety_review],
)

# --- Crew ---

crew = Crew(
    agents=[treasurer, executor],
    tasks=[safety_review, execution_plan],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("CREW RESULT")
    print("=" * 60)
    print(result)
