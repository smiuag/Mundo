from agents.llm_provider import get_kingdom_request
from core.game_controller import resolve_actions
from core.state_mutator import apply_effects
from narrative.location_scorer import get_active_locations
from narrative.cascade_resolver import evaluate_cascade_conditions
from narrative.event_generator import generate_narrative_events


def process_turn(world_data: dict) -> dict:
    import sys
    print("[TURN] Iniciando process_turn()", flush=True, file=sys.stderr)
    sys.stderr.flush()

    turn = world_data["metadata"]["turn"] + 1
    world_data["metadata"]["turn"] = turn
    print(f"\n=== TURNO {turn} ===", flush=True)
    sys.stdout.flush()

    # Decisiones de reinos (4 llamadas Ollama)
    print("[TURN] Obteniendo decisiones de reinos...", flush=True, file=sys.stderr)
    sys.stderr.flush()
    requests = []
    for kingdom in world_data["kingdoms"]:
        try:
            print(f"[TURN] Pidiendo decisión para {kingdom['name']}...", flush=True, file=sys.stderr)
            sys.stderr.flush()
            request = get_kingdom_request(kingdom, world_data)
            requests.append(request)
            print(f"  {kingdom['name']}: {request['action']} → {request['target']}", flush=True)
            sys.stdout.flush()
        except Exception as e:
            print(f"[TURN] ERROR obteniendo decisión de {kingdom['name']}: {e}", flush=True, file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            raise

    print(f"[TURN] Todas las decisiones obtenidas ({len(requests)} requests)", flush=True, file=sys.stderr)
    sys.stderr.flush()

    # Resolución mecánica (sin IA)
    print("[TURN] Resolviendo acciones...", flush=True, file=sys.stderr)
    sys.stderr.flush()
    try:
        mechanical_events = resolve_actions(requests, world_data)
        print(f"[TURN] Acciones resueltas OK: {len(mechanical_events)} eventos mecánicos", flush=True, file=sys.stderr)
        sys.stderr.flush()
    except Exception as e:
        print(f"[TURN] ERROR en resolve_actions: {e}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise

    # Cascadas pendientes
    print("[TURN] Evaluando cascadas pendientes...")
    cascade_seeds_triggered, updated_seeds = evaluate_cascade_conditions(world_data, turn)
    world_data["pending_cascade_seeds"] = updated_seeds
    print(f"  Seeds disparadas: {len(cascade_seeds_triggered)}")

    # Ubicaciones activas
    print("[TURN] Identificando ubicaciones activas...")
    active_locations = get_active_locations(world_data, requests)
    print(f"  Ubicaciones activas: {len(active_locations)}")

    # Generación narrativa (1 llamada Ollama)
    print("[TURN] Generando eventos narrativos...")
    narrative_events, new_cascade_seeds = generate_narrative_events(
        world_data, active_locations, requests, mechanical_events, cascade_seeds_triggered
    )

    # Mantener seeds nuevas
    import sys
    print(f"[DEBUG] Antes de extend seeds, hay {len(new_cascade_seeds)} nuevas", flush=True, file=sys.stderr)
    sys.stderr.flush()
    world_data["pending_cascade_seeds"].extend(new_cascade_seeds)
    print(f"[DEBUG] Seeds extendidas OK", flush=True, file=sys.stderr)
    sys.stderr.flush()

    # Combinar todos los eventos
    try:
        print(f"[TURN] Combinando eventos (mecánicos: {len(mechanical_events)}, narrativos: {len(narrative_events)})", flush=True)
        all_events = mechanical_events + narrative_events
        print(f"[TURN] Combinación OK: {len(all_events)} eventos totales", flush=True)
    except Exception as e:
        print(f"[TURN] ERROR combinando: {e}", flush=True)
        return {"turn": turn, "events": mechanical_events}

    # Aplicar efectos
    try:
        print("[TURN] Aplicando efectos...", flush=True)
        apply_effects(world_data, all_events)
        print("[TURN] Efectos aplicados OK", flush=True)
    except Exception as e:
        print(f"[TURN] ERROR en apply_effects: {e}", flush=True)

    # Guardar eventos en memoria
    try:
        print(f"[TURN] Guardando {len(all_events)} eventos en world_data...", flush=True)
        world_data["events"].extend(all_events)
        print(f"[TURN] Eventos en memoria OK (total: {len(world_data['events'])})", flush=True)
    except Exception as e:
        print(f"[TURN] ERROR guardando eventos: {e}", flush=True)

    print(f"[TURN] Turno {turn} completado\n", flush=True)
    return {"turn": turn, "events": all_events}
