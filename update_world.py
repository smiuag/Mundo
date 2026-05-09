import json

with open('data/world.json', 'r') as f:
    world = json.load(f)

# Agregar espías a cada reino
for kingdom in world['kingdoms']:
    if 'spies' not in kingdom:
        kingdom['spies'] = 5

# Agregar tropas estacionadas por territorio
for location in world['locations']:
    if 'garrison' not in location:
        location['garrison'] = {
            'kingdom': location.get('kingdom'),
            'troops': 100 if location.get('kingdom') else 0
        }

with open('data/world.json', 'w') as f:
    json.dump(world, f, indent=2)

print('OK: world.json actualizado')
