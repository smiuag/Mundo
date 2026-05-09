def evaluate_cascade_conditions(world_data: dict, current_turn: int) -> tuple:
    """
    Evalua seeds pendientes. Retorna (active_cascades, updated_seeds).
    active_cascades: lista de seeds que disparan este turno
    updated_seeds: seeds que se mantienen para turnos futuros
    """
    seeds = world_data.get("pending_cascade_seeds", [])
    active_cascades = []
    updated_seeds = []

    for seed in seeds:
        # Check expiracion
        if seed.get("expires_turn", 999) < current_turn:
            continue  # Seed expirado, descartar

        # Check si ya debe disparar
        if seed.get("fire_on_turn", current_turn) <= current_turn:
            # Evaluar condicion
            if should_fire_seed(seed, world_data):
                active_cascades.append(seed)
                continue  # No lo mantengamos, ya disparo

        # Mantener para siguiente turno
        updated_seeds.append(seed)

    return active_cascades, updated_seeds


def should_fire_seed(seed: dict, world_data: dict) -> bool:
    """
    Evalua si un seed debe disparar segun su condicion.
    Tipos: threshold, always, kingdom_action
    """
    cond_type = seed.get("condition_type", "always")

    if cond_type == "always":
        return True

    if cond_type == "threshold":
        condition = seed.get("condition", {})
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if not all([field, operator, value]):
            return False

        # Extraer valor actual del world_data
        current = get_nested_value(world_data, field)
        if current is None:
            return False

        if operator == "gt":
            return current > value
        elif operator == "lt":
            return current < value
        elif operator == "eq":
            return current == value
        elif operator == "gte":
            return current >= value
        elif operator == "lte":
            return current <= value

    return False


def get_nested_value(obj: dict, path: str):
    """
    Extrae un valor del dict usando ruta punteada.
    Ej: "locations.whitewatch_pass.tension" -> obj["locations"]["whitewatch_pass"]["tension"]
    """
    parts = path.split(".")
    current = obj

    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            current = current[int(part)]
        else:
            return None

    return current
