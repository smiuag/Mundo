import json

with open('data/world.json', 'r', encoding='utf-8') as f:
    world = json.load(f)

for loc in world['locations']:
    if 'unrest' not in loc:
        loc['unrest'] = 20
    if 'tension' not in loc:
        loc['tension'] = 70 if loc.get('contested') else 30
    if 'wealth' not in loc:
        loc['wealth'] = 80 if 'trading' in loc['name'].lower() else 40
    if 'situation' not in loc:
        situation = f"{loc['name']} - {loc['type'].replace('_', ' ').title()}"
        if loc.get('kingdom'):
            kingdom = next((k for k in world['kingdoms'] if k['id'] == loc['kingdom']), None)
            if kingdom:
                situation += f" bajo el control de {kingdom['name']}"
        if loc.get('contested'):
            situation += ' (zona contestada)'
        loc['situation'] = situation

if 'pending_cascade_seeds' not in world:
    world['pending_cascade_seeds'] = []

with open('data/world.json', 'w', encoding='utf-8') as f:
    json.dump(world, f, indent=2)

print('[OK] world.json expandido con nuevas propiedades')
