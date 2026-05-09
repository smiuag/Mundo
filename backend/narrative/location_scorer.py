import random

def get_active_locations(world_data: dict, kingdom_actions: list) -> list:
    """
    Determina qué ubicaciones merecen atencion narrativa este turno.
    Devuelve lista de location IDs ordenados por prioridad.
    """
    locations = world_data.get("locations", [])
    active = []

    # Construir set de locations donde ocurrieron acciones
    action_locations = set()
    for action in kingdom_actions:
        if action.get("target"):
            # Buscar si el target es una location
            target_loc = next(
                (l for l in locations if l["name"].lower() == action["target"].lower()),
                None
            )
            if target_loc:
                action_locations.add(target_loc["id"])

    # Ubicaciones pendientes de cascade
    cascade_location_ids = set()
    for seed in world_data.get("pending_cascade_seeds", []):
        if seed.get("location_id"):
            cascade_location_ids.add(seed["location_id"])

    # Evaluar cada ubicacion
    for loc in locations:
        priority = 0

        # Muy alta prioridad: contested o alta tension/unrest
        if loc.get("contested"):
            priority += 100
        if loc.get("tension", 0) > 60:
            priority += 50
        if loc.get("unrest", 0) > 50:
            priority += 40

        # Alta prioridad: accion ocurrió aqui
        if loc["id"] in action_locations:
            priority += 80

        # Alta prioridad: cascade seed pendiente
        if loc["id"] in cascade_location_ids:
            priority += 70

        # Baja prioridad: ubicacion estable, quizas evento menor
        if priority == 0:
            if random.random() < 0.2:  # 20% de chance para evento "menor"
                priority = 5

        if priority > 0:
            active.append({"id": loc["id"], "name": loc["name"], "priority": priority})

    # Ordenar por prioridad (descendente)
    active.sort(key=lambda x: x["priority"], reverse=True)
    return active
