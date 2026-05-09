import json

def build_narrative_context(
    world_data: dict,
    active_locations: list,
    kingdom_requests: list,
    mechanical_events: list,
    cascade_seeds: list
) -> str:
    """
    Construye el contexto comprimido para el prompt de Ollama.
    No manda el JSON completo, solo lo relevante.
    """
    context_lines = []

    # === ESTADO DEL MUNDO ===
    metadata = world_data.get("metadata", {})
    context_lines.append(f"=== ESTADO DEL MUNDO ===")
    context_lines.append(f"Turno: {metadata.get('turn', 0)}")
    context_lines.append(f"Temporada: {metadata.get('season', 'Unknown')} - Año {metadata.get('year', 1)}")
    context_lines.append("")

    # === REINOS Y TRACKS ===
    context_lines.append("=== REINOS ===")
    for kingdom in world_data.get("kingdoms", []):
        tracks = kingdom.get("tracks", {})
        context_lines.append(f"{kingdom['name']} ({kingdom['race']})")
        context_lines.append(f"  Happines: {tracks.get('happiness', 50)}, Estabilidad: {tracks.get('stability', 50)}, Recursos: {tracks.get('resources', 50)}")
    context_lines.append("")

    # === ACCIONES DE REINOS ESTE TURNO ===
    context_lines.append("=== ACCIONES DE REINOS ESTE TURNO ===")
    for req in kingdom_requests:
        context_lines.append(f"{req.get('kingdom_name')}: {req.get('action')} -> {req.get('target')}")
    context_lines.append("")

    # === EVENTOS MECANICOS YA RESUELTOS ===
    if mechanical_events:
        context_lines.append("=== EVENTOS MECANICOS YA RESUELTOS ===")
        for evt in mechanical_events:
            context_lines.append(f"- {evt.get('action', 'Acción')}: {evt.get('description')}")
        context_lines.append("")

    # === UBICACIONES ACTIVAS ===
    context_lines.append("=== UBICACIONES ACTIVAS ESTE TURNO ===")
    locations_by_id = {loc["id"]: loc for loc in world_data.get("locations", [])}

    for active in active_locations:
        loc_id = active["id"]
        loc = locations_by_id.get(loc_id)
        if not loc:
            continue

        context_lines.append(f"\n{loc['name']} [{loc['type']}]")
        context_lines.append(f"  Tension: {loc.get('tension', 50)}, Unrest: {loc.get('unrest', 20)}, Wealth: {loc.get('wealth', 40)}")

        if loc.get("contested"):
            context_lines.append(f"  CONTESTADA - Controlada por {loc.get('kingdom', 'nadie')}, Reclamada por otro reino")

        if loc.get("kingdom"):
            kingdom = next((k for k in world_data.get("kingdoms", []) if k["id"] == loc["kingdom"]), None)
            if kingdom:
                context_lines.append(f"  Bajo control de: {kingdom['name']}")

        context_lines.append(f"  Situacion: {loc.get('situation', 'Sin describir')}")

        # Ultimos eventos de esta ubicacion
        last_events = [
            e for e in reversed(world_data.get("events", []))
            if e.get("location_id") == loc_id
        ][:3]
        if last_events:
            context_lines.append(f"  Eventos recientes:")
            for evt in last_events:
                context_lines.append(f"    - {evt.get('title', evt.get('action', 'Evento'))}")

    context_lines.append("")

    # === CASCADAS PENDIENTES ===
    if cascade_seeds:
        context_lines.append("=== CASCADAS DISPARADAS ESTE TURNO ===")
        for seed in cascade_seeds:
            context_lines.append(f"Seed en {seed.get('location_id')}: {seed.get('seed_prompt', 'Sin descripcion')}")
        context_lines.append("")

    return "\n".join(context_lines)
