"""
agents/orchestrator.py

Root orchestrator for MedGuard.
Chains all four agents in sequence using ADK's SequentialAgent.

Pipeline:
Intake Agent -> Conflict & Risk Agent -> Scheduler & Gap Agent -> Reporter Agent
"""

from __future__ import annotations
from google.adk.agents.sequential_agent import SequentialAgent

from agents.intake_agent import intake_agent
from agents.conflict_risk_agent import conflict_risk_agent
from agents.scheduler_gap_agent import scheduler_gap_agent
from agents.reporter_agent import reporter_agent

root_agent = SequentialAgent(
    name="medguard_pipeline",
    description=(
        "MedGuard: a multi-agent medication safety pipeline. "
        "Takes a raw medication list and produces a daily brief "
        "covering interaction risks, a daily schedule, and refill "
        "alerts -- using live FDA label data."
    ),
    sub_agents=[
        intake_agent,
        conflict_risk_agent,
        scheduler_gap_agent,
        reporter_agent,
    ],
)