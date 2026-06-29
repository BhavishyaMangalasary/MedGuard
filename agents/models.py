"""
agents/models.py
Shared data structures passed between agents.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import time


@dataclass
class Medication:
    name: str
    dose: str | None = None
    frequency: str | None = None
    times: list[time] = field(default_factory=list)
    prescriber: str | None = None
    days_supply: int | None = None
    last_filled: str | None = None
    raw_input: str | None = None


@dataclass
class PatientProfile:
    patient_id: str
    display_name: str
    medications: list[Medication] = field(default_factory=list)


@dataclass
class RiskFlag:
    severity: str        # "critical" | "moderate" | "informational"
    category: str        # "interaction" | "timing_conflict" | "prescriber_blind_spot"
    drugs_involved: list[str]
    explanation: str
    label_section: str   # which FDA label section this came from
    source: str = "FDA openFDA Drug Label API"


@dataclass
class ScheduleEntry:
    time_of_day: str
    medications: list[str]
    notes: str | None = None


@dataclass
class RefillAlert:
    medication: str
    days_remaining: int | None
    message: str


@dataclass
class DailyBrief:
    patient_name: str
    generated_at: str
    risk_flags: list[RiskFlag] = field(default_factory=list)
    schedule: list[ScheduleEntry] = field(default_factory=list)
    refill_alerts: list[RefillAlert] = field(default_factory=list)
    summary_text: str = ""