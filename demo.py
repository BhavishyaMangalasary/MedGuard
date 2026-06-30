"""
demo.py
MedGuard - Medication Safety Assistant
Run with: python demo.py
"""

from __future__ import annotations
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types
from agents.orchestrator import root_agent
from tools.secure_storage import (
    save_patient_record,
    load_patient_record,
    SecureStorageError,
)


def check_existing_record(patient_name: str) -> dict | None:
    """Check if a saved record exists for this patient."""
    try:
        patient_id = patient_name.lower().replace(" ", "_")
        record = load_patient_record(patient_name, patient_id)
        return record
    except SecureStorageError:
        return None


def get_medication_input(patient_name: str) -> str:
    """Prompt user to type a new medication list."""
    print(f"\nPlease enter {patient_name}'s medication list below.")
    print("Include drug name, dose, frequency, which doctor")
    print("prescribed it, days supply, and last fill date if known.")
    print("\nType DONE on a new line when finished.\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)


def ask_to_save(patient_name: str, medication_text: str) -> None:
    """Ask user if they want to save the medication list."""
    print("\nSave this medication list for next time? (yes/no)")
    answer = input("> ").strip().lower()
    if answer in ("yes", "y"):
        patient_id = patient_name.lower().replace(" ", "_")
        save_patient_record(
            patient_name=patient_name,
            record={
                "patient_name": patient_name,
                "medication_text": medication_text,
            },
            access_scope=[patient_id]
        )
        print(f"✓ Record saved for {patient_name}.")
    else:
        print("Record not saved.")


def get_user_input() -> tuple[str, str]:
    print("\n" + "=" * 60)
    print("  Welcome to MedGuard - Medication Safety Assistant")
    print("=" * 60)

    print("\nWho are you managing medications for?")
    print("(e.g. 'myself', 'my mom', 'Janet')\n")
    patient_name = input("> ").strip()

    if not patient_name:
        patient_name = "the patient"

    # Check for existing saved record
    existing = check_existing_record(patient_name)

    if existing:
        print(f"\nFound a saved record for {patient_name}.")
        print("1. Load saved record")
        print("2. Enter a new list")
        print()
        choice = input("> ").strip()

        if choice == "1":
            print(f"\nLoading {patient_name}'s saved medication list...")
            medication_text = existing.get("medication_text", "")
            return patient_name, medication_text
        else:
            medication_text = get_medication_input(patient_name)
            return patient_name, medication_text
    else:
        medication_text = get_medication_input(patient_name)
        return patient_name, medication_text


async def run_pipeline(patient_name: str, medication_text: str) -> bool:
    """Run the 4-agent pipeline and print the final brief."""
    runner = InMemoryRunner(agent=root_agent, app_name="medguard")
    session = await runner.session_service.create_session(
        app_name="medguard",
        user_id=patient_name.lower().replace(" ", "_")
    )

    full_input = f"Patient name: {patient_name}\n\n{medication_text}"

    print(f"\nAnalyzing {patient_name}'s medication list...\n")

    message = types.Content(
        role="user",
        parts=[types.Part(text=full_input)]
    )

    output_printed = False
    async for event in runner.run_async(
        user_id=patient_name.lower().replace(" ", "_"),
        session_id=session.id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            if event.author == "reporter_agent":
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        print("\n" + "=" * 60)
                        print(f"  MEDGUARD DAILY BRIEF — {patient_name.upper()}")
                        print("=" * 60 + "\n")
                        print(part.text)
                        output_printed = True

    return output_printed


async def main() -> None:
    patient_name, medication_text = get_user_input()

    if not medication_text.strip():
        print("\nNo medication list found. Please run again.")
        sys.exit(1)

    output_printed = await run_pipeline(patient_name, medication_text)

    if not output_printed:
        print("Something went wrong. Please try again.")
        return

    # Only offer to save if this was new input (not loaded from storage)
    existing = check_existing_record(patient_name)
    if not existing:
        ask_to_save(patient_name, medication_text)


if __name__ == "__main__":
    asyncio.run(main())