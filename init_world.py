import json

world = {
    "metadata": {
        "name": "Aethermoor",
        "turn": 0
    },
    "kingdoms": [
        {
            "id": "valorheim",
            "name": "Valorheim",
            "race": "Human",
            "personality": "Aggressive, militaristic",
            "goals": ["expand territory", "military dominance"],
            "population": 150000,
            "gold": 1000,
            "spies": 5,
            "military": {
                "warriors": 5000,
                "archers": 3000,
                "cavalry": 1500
            },
            "relationships": {
                "ironhold": -10,
                "silvantir": 5,
                "scorvale": -5
            },
            "tracks": {
                "happiness": 60,
                "stability": 75,
                "resources": 80,
                "culture": 50
            }
        },
        {
            "id": "ironhold",
            "name": "Ironhold",
            "race": "Dwarf",
            "personality": "Defensive, merchant-minded",
            "goals": ["economic growth", "trade routes"],
            "population": 120000,
            "gold": 1500,
            "spies": 3,
            "military": {
                "warriors": 3000,
                "archers": 1500,
                "cavalry": 500
            },
            "relationships": {
                "valorheim": -10,
                "silvantir": 15,
                "scorvale": 10
            },
            "tracks": {
                "happiness": 70,
                "stability": 85,
                "resources": 90,
                "culture": 60
            }
        },
        {
            "id": "silvantir",
            "name": "Silvantír",
            "race": "Elf",
            "personality": "Mysterious, isolationist",
            "goals": ["preserve nature", "magical research"],
            "population": 100000,
            "gold": 800,
            "spies": 8,
            "military": {
                "warriors": 2000,
                "archers": 4000,
                "cavalry": 800
            },
            "relationships": {
                "valorheim": 5,
                "ironhold": 15,
                "scorvale": -20
            },
            "tracks": {
                "happiness": 55,
                "stability": 65,
                "resources": 70,
                "culture": 90
            }
        },
        {
            "id": "scorvale",
            "name": "Scorvale",
            "race": "Mixed",
            "personality": "Cunning, ambitious",
            "goals": ["chaos and profit", "political influence"],
            "population": 180000,
            "gold": 600,
            "spies": 10,
            "military": {
                "warriors": 4000,
                "archers": 2500,
                "cavalry": 1200
            },
            "relationships": {
                "valorheim": -5,
                "ironhold": 10,
                "silvantir": -20
            },
            "tracks": {
                "happiness": 40,
                "stability": 50,
                "resources": 60,
                "culture": 70
            }
        }
    ],
    "locations": [
        {
            "id": "whitewatch_pass",
            "name": "Whitewatch Pass",
            "type": "mountain_pass",
            "kingdom": "valorheim",
            "contested": False,
            "unrest": 30,
            "tension": 50,
            "wealth": 40,
            "situation": "A strategic mountain passage controlled by Valorheim. Constant guard patrols."
        },
        {
            "id": "ironforge_depths",
            "name": "Ironforge Depths",
            "type": "mine",
            "kingdom": "ironhold",
            "contested": False,
            "unrest": 20,
            "tension": 30,
            "wealth": 95,
            "situation": "A vast dwarven mine operation. Rich in resources but dangerous."
        },
        {
            "id": "emerald_forest",
            "name": "Emerald Forest",
            "type": "forest",
            "kingdom": "silvantir",
            "contested": False,
            "unrest": 25,
            "tension": 40,
            "wealth": 50,
            "situation": "Ancient elven woodland. Home to magical creatures and secrets."
        },
        {
            "id": "crimson_city",
            "name": "Crimson City",
            "type": "city",
            "kingdom": "scorvale",
            "contested": False,
            "unrest": 60,
            "tension": 70,
            "wealth": 70,
            "situation": "A chaotic urban center of trade and intrigue. Ruled by shadows."
        },
        {
            "id": "neutral_trading_post",
            "name": "Neutral Trading Post",
            "type": "trade_post",
            "kingdom": None,
            "contested": True,
            "unrest": 40,
            "tension": 60,
            "wealth": 80,
            "situation": "A bustling neutral ground where merchants from all lands trade. Tensions run high."
        },
        {
            "id": "ancient_ruins",
            "name": "Ancient Ruins",
            "type": "ruins",
            "kingdom": None,
            "contested": True,
            "unrest": 50,
            "tension": 75,
            "wealth": 30,
            "situation": "Mysterious ancient structures. Everyone seeks their secrets."
        },
        {
            "id": "silent_lake",
            "name": "Silent Lake",
            "type": "lake",
            "kingdom": None,
            "contested": False,
            "unrest": 20,
            "tension": 30,
            "wealth": 35,
            "situation": "A quiet body of water surrounded by neutral territory."
        },
        {
            "id": "dragon_peak",
            "name": "Dragon Peak",
            "type": "mountain",
            "kingdom": None,
            "contested": False,
            "unrest": 30,
            "tension": 80,
            "wealth": 10,
            "situation": "A dangerous volcanic mountain. Few dare approach."
        },
        {
            "id": "shadow_vale",
            "name": "Shadow Vale",
            "type": "valley",
            "kingdom": None,
            "contested": True,
            "unrest": 70,
            "tension": 85,
            "wealth": 20,
            "situation": "A dark and mysterious valley where many disappear. Disputed territory."
        },
        {
            "id": "golden_fields",
            "name": "Golden Fields",
            "type": "farmland",
            "kingdom": None,
            "contested": False,
            "unrest": 15,
            "tension": 25,
            "wealth": 60,
            "situation": "Fertile farmland that feeds the region. Peaceful but contested by traders."
        },
        {
            "id": "moonstone_caves",
            "name": "Moonstone Caves",
            "type": "caves",
            "kingdom": None,
            "contested": False,
            "unrest": 35,
            "tension": 50,
            "wealth": 55,
            "situation": "Underground crystal caverns. Valuable resources attract explorers."
        },
        {
            "id": "cursed_swamp",
            "name": "Cursed Swamp",
            "type": "swamp",
            "kingdom": None,
            "contested": False,
            "unrest": 60,
            "tension": 70,
            "wealth": 15,
            "situation": "A haunted wetland. Strange lights and sounds. Avoided by most."
        },
        {
            "id": "scholar_tower",
            "name": "Scholar's Tower",
            "type": "tower",
            "kingdom": None,
            "contested": False,
            "unrest": 10,
            "tension": 20,
            "wealth": 45,
            "situation": "An isolated tower of learning. Neutral ground for knowledge seekers."
        }
    ],
    "events": [],
    "pending_cascade_seeds": []
}

with open('data/world.json', 'w', encoding='utf-8') as f:
    json.dump(world, f, indent=2)

print("World initialized: 4 kingdoms, 13 locations")
