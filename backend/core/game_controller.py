from datetime import datetime

def resolve_actions(requests: list, world_state: dict) -> list:
    """Resuelve conflictos entre solicitudes de reinos y genera eventos."""
    events = []

    # Agrupar solicitudes por tipo y objetivo
    attacks = [r for r in requests if r["action"] == "attack"]
    trades = [r for r in requests if r["action"] == "trade"]
    spies = [r for r in requests if r["action"] == "spy"]
    alliances = [r for r in requests if r["action"] == "alliance"]

    print(f"[RESOLVER] Ataques: {len(attacks)}, Trades: {len(trades)}, Espías: {len(spies)}, Alianzas: {len(alliances)}")
    for t in trades:
        print(f"  Trade: {t['kingdom_name']} → {t['target']}")

    # Resolver ataques
    for attack in attacks:
        target_location = next((l for l in world_state["locations"] if l["name"].lower() == attack["target"].lower()), None)

        if not target_location:
            events.append({
                "turn": world_state["metadata"]["turn"],
                "kingdom": attack["kingdom_name"],
                "type": "failed",
                "action": "Ataque",
                "description": f"Intento de ataque a {attack['target']} falló: ubicación no encontrada",
                "timestamp": datetime.now().isoformat()
            })
            continue

        # Ver si otro reino defiende el mismo territorio
        defending_attacks = [r for r in attacks if r["target"].lower() == attack["target"].lower() and r["kingdom_id"] != attack["kingdom_id"]]

        if defending_attacks:
            # Hay conflicto directo
            defender = defending_attacks[0]
            winner = attack["kingdom_name"] if attack["troops"] > defender["troops"] else defender["kingdom_name"]

            events.append({
                "turn": world_state["metadata"]["turn"],
                "kingdom": attack["kingdom_name"],
                "type": "battle",
                "action": "Batalla",
                "description": f"Batalla en {target_location['name']}: {attack['kingdom_name']} vs {defender['kingdom_name']}. Ganador: {winner}",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Ataque sin resistencia
            events.append({
                "turn": world_state["metadata"]["turn"],
                "kingdom": attack["kingdom_name"],
                "type": "conquest",
                "action": "Conquista",
                "description": f"{attack['kingdom_name']} conquistó {target_location['name']}",
                "timestamp": datetime.now().isoformat()
            })

    # Resolver comercio
    for trade in trades:
        # Buscar si el target es un reino u otra ubicación
        other_kingdom = next((k for k in world_state["kingdoms"] if k["name"].lower() == trade["target"].lower()), None)
        target_location = next((l for l in world_state["locations"] if l["name"].lower() == trade["target"].lower()), None)

        if other_kingdom or target_location:
            target_name = other_kingdom["name"] if other_kingdom else target_location["name"]
            events.append({
                "turn": world_state["metadata"]["turn"],
                "kingdom": trade["kingdom_name"],
                "type": "trade",
                "action": "Comercio",
                "description": f"Comercio exitoso: {trade['kingdom_name']} con {target_name}",
                "timestamp": datetime.now().isoformat()
            })

    # Resolver espionaje
    for spy in spies:
        target_kingdom = next((k for k in world_state["kingdoms"] if k["name"].lower() == spy["target"].lower()), None)

        if target_kingdom:
            events.append({
                "turn": world_state["metadata"]["turn"],
                "kingdom": spy["kingdom_name"],
                "type": "espionage",
                "action": "Espionaje",
                "description": f"{spy['kingdom_name']} envió espías a {target_kingdom['name']}",
                "timestamp": datetime.now().isoformat()
            })

    # Resolver alianzas
    for alliance in alliances:
        target_kingdom = next((k for k in world_state["kingdoms"] if k["name"].lower() == alliance["target"].lower()), None)

        if target_kingdom:
            events.append({
                "turn": world_state["metadata"]["turn"],
                "kingdom": alliance["kingdom_name"],
                "type": "alliance",
                "action": "Alianza",
                "description": f"Pacto de alianza: {alliance['kingdom_name']} y {target_kingdom['name']}",
                "timestamp": datetime.now().isoformat()
            })

    return events
