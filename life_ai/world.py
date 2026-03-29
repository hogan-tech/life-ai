from life_ai.agent import Agent


def generate_world(idea: str) -> dict:
    if "startup" in idea.lower():
        return {
            "setting": "A chaotic early-stage startup racing to ship its first product",
            "conflict": "The team disagrees on whether to launch fast or build it right",
            "agents": [
                Agent(
                    name="Maya",
                    role="CEO",
                    personality="visionary, impatient, persuasive",
                    goal="Secure Series A funding before runway runs out",
                    relationships={"Ethan": "co-founder tension", "Priya": "trusted ally"},
                ),
                Agent(
                    name="Ethan",
                    role="CTO",
                    personality="perfectionist, introverted, principled",
                    goal="Ship reliable software without cutting corners",
                    relationships={"Maya": "co-founder tension", "Priya": "mentor"},
                ),
                Agent(
                    name="Priya",
                    role="Head of Product",
                    personality="pragmatic, empathetic, diplomatic",
                    goal="Keep the team aligned and users happy",
                    relationships={"Maya": "trusted ally", "Ethan": "mentee"},
                ),
            ],
        }

    return {
        "setting": "A small community navigating an unexpected change",
        "conflict": "Old guard resists the new while outsiders push for transformation",
        "agents": [
            Agent(
                name="Roland",
                role="Elder",
                personality="cautious, wise, stubborn",
                goal="Preserve what has always worked",
                relationships={"Suki": "distrustful", "Marco": "neutral"},
            ),
            Agent(
                name="Suki",
                role="Newcomer",
                personality="energetic, idealistic, impatient",
                goal="Prove that change is possible",
                relationships={"Roland": "distrustful", "Marco": "friendly"},
            ),
            Agent(
                name="Marco",
                role="Mediator",
                personality="calm, perceptive, noncommittal",
                goal="Find common ground between both sides",
                relationships={"Roland": "neutral", "Suki": "friendly"},
            ),
        ],
    }
