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


def get_user_input() -> str:
    print("\n" + "=" * 60)
    print("  Welcome to MedGuard - Medication Safety Assistant")
    print("=" * 60)
    print("""
I'll analyze your medication list and give you a daily brief
covering interaction risks, your schedule, and refill alerts.

Please tell me about the medications. Include as much as you
know -- drug name, dose, frequency, which doctor prescribed
it, days supply, and when it was last filled.

Type your medication list below.
When finished type DONE on a new line and press Enter.
""")

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


async def main() -> None:
    user_input = get_user_input()

    if not user_input.strip():
        print("\nNo input received. Please run again and enter your medication list.")
        sys.exit(1)

    runner = InMemoryRunner(agent=root_agent, app_name="medguard")
    session = await runner.session_service.create_session(
        app_name="medguard",
        user_id="user"
    )

    print("\nAnalyzing your medication list...\n")

    message = types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    )

    output_printed = False
    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            if event.author == "reporter_agent":
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        print("\n" + "=" * 60)
                        print("  YOUR MEDGUARD DAILY BRIEF")
                        print("=" * 60 + "\n")
                        print(part.text)
                        output_printed = True

    if not output_printed:
        print("Something went wrong. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())