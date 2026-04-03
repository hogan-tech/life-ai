"""SDK demo - shows a fresh run followed by a resume.

Run from the repo root:
    python examples/sdk_demo.py
"""

from life_ai.sdk import resume_simulation, run_simulation

# 1) Fresh run

print("=== Fresh run ===")
result = run_simulation(
    idea="Silicon Valley startup",
    rounds=2,
    save="sdk_demo",   # persists to saves/sdk_demo.json
)

print(f"World : {result['world']['idea']}")
print(f"Theme : {result['world']['theme']}")
print(f"Agents: {[a['name'] for a in result['agents']]}")
print(f"Days  : {result['current_day']}")
print()

for day in result["log"]:
    print(f"--- {day.get('label', 'Day')} ---")
    for line in day.get("lines", []):
        print(f"  {line['speaker']} -> {line['target']}  [{line['intent']}]")
        print(f"    {line['text']}")
    for change in day.get("rel_changes", []):
        print(f"  * {change}")
    print()

# 2) Resume

print("=== Resume (2 more rounds) ===")
result2 = resume_simulation(
    load="sdk_demo",
    rounds=2,
)

print(f"Days after resume: {result2['current_day']}")
print()

for day in result2["log"]:
    print(f"--- {day.get('label', 'Day')} ---")
    for line in day.get("lines", []):
        print(f"  {line['speaker']} -> {line['target']}  [{line['intent']}]")
        print(f"    {line['text']}")
    print()

# 3) Final relationship snapshot

print("=== Final relationships ===")
for agent, targets in result2["relationships"].items():
    for target, state in targets.items():
        print(f"  {agent} -> {target}: {state}")
