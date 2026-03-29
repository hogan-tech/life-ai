from pydantic import BaseModel

from life_ai.agent import Agent


class World(BaseModel):
    idea: str
    setting: str
    conflict: str
    theme: str = "default"
    agents: list[Agent]


# ---------------------------------------------------------------------------
# World templates
# ---------------------------------------------------------------------------

_STARTUP = lambda idea: World(
    idea=idea, theme="startup",
    setting="Everyone is pretending the runway isn't a problem.",
    conflict="Speed vs. quality vs. money — everyone wants a different outcome",
    agents=[
        Agent(
            name="Maya", role="Founder-CEO, Running Out of Time",
            personality="visionary, impatient, persuasive",
            goal="Close Series A before runway hits 3 months",
            relationships={"Ethan": "co-founder tension", "Jordan": "pressure", "Priya": "trusted ally"},
        ),
        Agent(
            name="Ethan", role="Co-Founder, Will Not Ship Broken Code",
            personality="perfectionist, cautious, principled",
            goal="Ship nothing that will embarrass the team in six months",
            relationships={"Maya": "co-founder tension", "Jordan": "skeptical", "Priya": "mentor"},
        ),
        Agent(
            name="Jordan", role="Lead Investor, Already Losing Patience",
            personality="greedy, aggressive, impatient",
            goal="Force a launch this quarter to protect the portfolio",
            relationships={"Maya": "pressure", "Ethan": "skeptical", "Priya": "neutral"},
        ),
        Agent(
            name="Priya", role="Head of Design, Only Adult in the Room",
            personality="idealistic, diplomatic, pragmatic",
            goal="Ship something users actually love, not just something that ships",
            relationships={"Maya": "trusted ally", "Ethan": "mentee", "Jordan": "neutral"},
        ),
    ],
)

_POLITICS = lambda idea: World(
    idea=idea, theme="politics",
    setting="A city council on the edge of a landmark vote",
    conflict="Progress vs. preservation — loyalties shift with every backroom deal",
    agents=[
        Agent(
            name="Senator Cole", role="Politician",
            personality="aggressive, persuasive, ambitious",
            goal="Win the vote and leverage it for the governorship",
            relationships={"Dr. Reyes": "rival", "Lin": "ally of convenience", "Marcus": "distrustful"},
        ),
        Agent(
            name="Dr. Reyes", role="Activist",
            personality="idealistic, stubborn, principled",
            goal="Block the development bill and protect the neighborhood",
            relationships={"Senator Cole": "rival", "Lin": "skeptical", "Marcus": "ally"},
        ),
        Agent(
            name="Lin", role="Lobbyist",
            personality="greedy, diplomatic, calculating",
            goal="Get the bill passed — the client pays either way",
            relationships={"Senator Cole": "ally of convenience", "Dr. Reyes": "skeptical", "Marcus": "neutral"},
        ),
        Agent(
            name="Marcus", role="Journalist",
            personality="cautious, pragmatic, perceptive",
            goal="Find the story that ends a career — or saves one",
            relationships={"Senator Cole": "distrustful", "Dr. Reyes": "ally", "Lin": "neutral"},
        ),
    ],
)

_PIRATES = lambda idea: World(
    idea=idea, theme="pirates",
    setting="The deck smells like salt and bad decisions.",
    conflict="The captain hoards the treasure map; the crew suspects it leads nowhere",
    agents=[
        Agent(
            name="Captain Redd", role="Captain, Hiding Something About the Map",
            personality="aggressive, visionary, paranoid",
            goal="Reach the vault at Port Null before anyone learns the map is half-forged",
            relationships={"Bones": "distrustful", "Yara": "leverage", "Finn": "rival"},
        ),
        Agent(
            name="Bones", role="Navigator, Loyal Until Proven Wrong",
            personality="cautious, calculating, loyal",
            goal="Keep the ship off the rocks — even if the captain steers toward them",
            relationships={"Captain Redd": "distrustful", "Yara": "trusted", "Finn": "neutral"},
        ),
        Agent(
            name="Yara", role="Quartermaster, Already Skimming the Treasury",
            personality="greedy, pragmatic, cunning",
            goal="Control the treasury before anyone realizes how much has already gone missing",
            relationships={"Captain Redd": "leverage", "Bones": "trusted", "Finn": "ally of convenience"},
        ),
        Agent(
            name="Finn", role="Crew Agitator, One Speech Away from Mutiny",
            personality="idealistic, reckless, charismatic",
            goal="Convince the crew they deserve equal share — and lead the mutiny if they don't get it",
            relationships={"Captain Redd": "rival", "Bones": "neutral", "Yara": "ally of convenience"},
        ),
    ],
)

_BOARD = lambda idea: World(
    idea=idea, theme="board",
    setting="The boardroom is already tense before anyone speaks.",
    conflict="The CEO was removed by text message. Now everyone is deciding if that was a mistake",
    agents=[
        Agent(
            name="Elias", role="Recently Fired Founder-CEO, Not Leaving Quietly",
            personality="visionary, defiant, persuasive",
            goal="Reclaim the chair before the press finds out and the story calcifies",
            relationships={"Miriam": "rival", "Grant": "former ally", "Nadia": "distrustful"},
        ),
        Agent(
            name="Miriam", role="Board Chair, Orchestrated the Removal",
            personality="aggressive, calculating, cold",
            goal="Make the removal stick and install someone the board can actually control",
            relationships={"Elias": "rival", "Grant": "pressure", "Nadia": "ally"},
        ),
        Agent(
            name="Grant", role="Investor Rep, Already Switching Sides",
            personality="greedy, pragmatic, noncommittal",
            goal="Protect the valuation at all costs — loyalty is a rounding error",
            relationships={"Elias": "former ally", "Miriam": "pressure", "Nadia": "neutral"},
        ),
        Agent(
            name="Nadia", role="General Counsel, Trying to Prevent a Lawsuit",
            personality="cautious, principled, diplomatic",
            goal="Ensure whatever happens next doesn't expose the company to a lawsuit",
            relationships={"Elias": "distrustful", "Miriam": "ally", "Grant": "neutral"},
        ),
    ],
)

_HARVARD = lambda idea: World(
    idea=idea, theme="harvard",
    setting="A Harvard dorm room at 2am — three laptops, one idea, and one too many founders",
    conflict="Everyone wants credit for the vision; nobody agrees what the product actually is",
    agents=[
        Agent(
            name="Zoe", role="CS Senior",
            personality="perfectionist, ambitious, competitive",
            goal="Be named lead founder before the YC application goes out tomorrow",
            relationships={"Dev": "rivalry", "Preet": "distrustful", "Cass": "ally"},
        ),
        Agent(
            name="Dev", role="Econ Junior",
            personality="visionary, persuasive, impatient",
            goal="Pivot the product to B2B before anyone talks to another student user",
            relationships={"Zoe": "rivalry", "Preet": "pressure", "Cass": "neutral"},
        ),
        Agent(
            name="Preet", role="Pre-Law Sophomore",
            personality="cautious, pragmatic, image-conscious",
            goal="Make sure this doesn't appear on a clerkship application as a failure",
            relationships={"Zoe": "distrustful", "Dev": "pressure", "Cass": "friendly"},
        ),
        Agent(
            name="Cass", role="Design Student",
            personality="idealistic, diplomatic, creative",
            goal="Build something that actually changes how students learn — not just something fundable",
            relationships={"Zoe": "ally", "Dev": "neutral", "Preet": "friendly"},
        ),
    ],
)

_WORLDS = [
    ({"startup", "founder", "vc", "silicon", "series"}, _STARTUP),
    ({"politic", "election", "vote", "council", "senate"}, _POLITICS),
    ({"pirate", "ship", "crew", "treasure", "mutiny"}, _PIRATES),
    ({"board", "openai", "musk", "ceo", "fired", "governance", "exec"}, _BOARD),
    ({"harvard", "student", "university", "college", "dorm", "yc"}, _HARVARD),
]


def generate_world(idea: str) -> World:
    lowered = idea.lower()
    for keywords, factory in _WORLDS:
        if any(kw in lowered for kw in keywords):
            return factory(idea)
    return World(
        idea=idea, theme="default",
        setting=f"A world shaped by the idea: {idea}",
        conflict="Competing visions pull the group apart before it can move forward",
        agents=[
            Agent(
                name="Alex", role="Leader",
                personality="aggressive, visionary, impatient",
                goal="Take control and drive the group toward a decisive outcome",
                relationships={"Sam": "rivalry", "Jordan": "alliance", "Casey": "neutral"},
            ),
            Agent(
                name="Sam", role="Skeptic",
                personality="cautious, principled, stubborn",
                goal="Slow things down and expose what Alex is really after",
                relationships={"Alex": "rivalry", "Jordan": "distrustful", "Casey": "friendly"},
            ),
            Agent(
                name="Jordan", role="Opportunist",
                personality="greedy, diplomatic, calculating",
                goal="Back whoever is winning long enough to benefit personally",
                relationships={"Alex": "alliance", "Sam": "distrustful", "Casey": "neutral"},
            ),
            Agent(
                name="Casey", role="Mediator",
                personality="idealistic, empathetic, pragmatic",
                goal="Keep the group together long enough to find a real solution",
                relationships={"Alex": "neutral", "Sam": "friendly", "Jordan": "neutral"},
            ),
        ],
    )
