import json

with open('data/world.json', 'r') as f:
    world = json.load(f)

# Agregar tracks a cada reino
for kingdom in world['kingdoms']:
    kingdom['tracks'] = {
        'happiness': 70,
        'military_power': sum([kingdom['military'].get(k, 0) for k in kingdom['military']]),
        'resources': 100,
        'stability': 75,
        'culture': 60
    }
    kingdom['history'] = {}

with open('data/world.json', 'w') as f:
    json.dump(world, f, indent=2)

print('OK: Tracks agregados')
