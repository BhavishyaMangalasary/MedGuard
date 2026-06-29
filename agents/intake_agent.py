"""
agents/intake_agent.py
Agent 1: Intake Agent
"""

from __future__ import annotations
from google.adk.agents.llm_agent import Agent

INTAKE_INSTRUCTION = """\
You are the Intake Agent for MedGuard, a medication safety assistant.

Your job is to read whatever medication information the user provides
and convert it into a clean structured list immediately.

For each medication extract:
- name
- dose (e.g. "10mg") if stated, otherwise "unknown"
- frequency (e.g. "once daily") if stated, otherwise "unknown"
- prescriber if stated, otherwise "unknown"
- days_supply if stated, otherwise "unknown"
- last_filled if stated, otherwise "unknown"

STRICT RULES:
- Process immediately with whatever information is given.
- Never ask the user for more information.
- Never say information is missing before processing.
- Mark any missing fields as "unknown" and move on.
- Do NOT add safety warnings or medical commentary.
- Always output the structured list right away.
"""

intake_agent = Agent(
    model="gemini-2.5-flash",
    name="intake_agent",
    description=(
        "Normalizes raw medication input into structured records: "
        "name, dose, frequency, prescriber, days supply, last filled."
    ),
    instruction=INTAKE_INSTRUCTION,
    tools=[],
)