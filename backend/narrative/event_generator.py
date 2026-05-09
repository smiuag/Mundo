import requests
import json
import re
import os
from datetime import datetime
from .context_builder import build_narrative_context


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL = "gemma2:27b"


def generate_narrative_events(
    world_data: dict,
    location_scores: list,
    kingdom_requests: list,
    mechanical_events: list,
    cascade_seeds: list
) -> tuple:
    """
    Genera eventos narrativos mediante UNA llamada a Ollama.
    Retorna (events_list, new_cascade_seeds).
    """
    turn = world_data.get("metadata", {}).get("turn", 0)

    # Construir contexto comprimido
    context = build_narrative_context(
        world_data, location_scores, kingdom_requests, mechanical_events, cascade_seeds
    )

    # Construir el prompt
    prompt = f"""Eres el narrador de Aethermoor. Tu rol es generar eventos narrativos que den profundidad y drama al mundo.

{context}

INSTRUCCIONES:
1. Genera entre 3 y 6 eventos narrativos que:
   - Sean detallados y cinematicos (2-4 oraciones por evento)
   - Incluyan personajes, emociones, y conflictos humanos
   - Apliquen en al menos una ubicacion donde NO ocurrio accion directa de reinos
   - Expliquen las consecuencias a nivel local de las acciones strategicas

2. Cada evento tiene un titulo corto (como "rumor de taberna") y descripcion rica

3. Para cada evento incluye:
   - title: titulo corto (max 8 palabras)
   - description: 2-4 oraciones con detalles (quienes, donde exactamente, que paso, por que importa)
   - category: uno de [military, trade, political, social, rumor, crime]
   - location_id: ID de ubicacion afectada (debe existir)
   - kingdoms_involved: lista de IDs de reinos afectados
   - effects: cambios que este evento causa:
     * location effects: tension/unrest/wealth (+/- 0 a 20)
     * kingdom tracks: happiness/stability/resources/culture (+/- 0 a 10)
     * relationships: cambios en relaciones entre reinos (+/- 0 a 10)
   - cascade_seed (opcional): si este evento plantea semillas para futuros turnos
     * condition: descripcion en lenguaje natural
     * delay_turns: en cuantos turnos puede disparar
     * seed_prompt: contexto para generar el evento escalado

4. Los values de delta en effects deben ser numeros enteros, nunca strings

RESPONDE SOLO CON JSON:
{{
  "events": [
    {{
      "title": "string",
      "description": "string",
      "category": "military|trade|political|social|rumor|crime",
      "location_id": "string",
      "kingdoms_involved": ["string"],
      "effects": [
        {{"target_type": "location", "target_id": "string", "field": "tension", "delta": -5}},
        {{"target_type": "kingdom", "target_id": "string", "field": "tracks.happiness", "delta": -3}},
        {{"target_type": "relationship", "kingdoms": ["string", "string"], "delta": -5}}
      ],
      "cascade_seed": {{
        "condition": "string",
        "delay_turns": 1,
        "seed_prompt": "string"
      }}
    }}
  ]
}}

VALIDACION:
- location_id debe ser un ID valido de las ubicaciones listadas arriba
- deltas numeros solamente
- No inventes ubicaciones ni reinos
"""

    print(f"[NARRATIVE] Generando eventos narrativos (turno {turn})...")

    try:
        print(f"[NARRATIVE] Conectando a Ollama en {OLLAMA_URL}...", flush=True)
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=240
        )

        if response.status_code != 200:
            print(f"[NARRATIVE] Error HTTP {response.status_code}")
            return [], []

        response_text = response.json().get("response", "")
        print(f"[NARRATIVE] Respuesta recibida ({len(response_text)} chars)")
        print(f"[NARRATIVE] Primeros 300 chars: {response_text[:300]}")

        # Extraer JSON robusto
        print(f"[NARRATIVE] Intentando extraer JSON de {len(response_text)} chars...", flush=True)
        events_data = extract_json_robust(response_text)
        print(f"[NARRATIVE] Resultado de extracción: {events_data is not None} (retornó {'dict' if isinstance(events_data, dict) else 'None'})", flush=True)
        if not events_data:
            # Guardarse a archivo para inspeccionar
            with open('/app/data/ollama_response_debug.txt', 'w') as f:
                f.write(response_text)
            print(f"[NARRATIVE] No se pudo extraer JSON. Respuesta guardada en ollama_response_debug.txt")

        if not events_data or "events" not in events_data:
            print(f"[NARRATIVE] No se pudo parsear JSON valido - usando eventos de ejemplo")
            # Generar eventos de ejemplo mientras debugueamos
            events_data = generate_example_events(world_data, turn, location_scores)
            if not events_data:
                return [], []

        # Procesar eventos
        events = []
        new_seeds = []

        for event_data in events_data.get("events", []):
            event = create_narrative_event(event_data, turn, world_data)
            if event:
                events.append(event)

                # Extraer cascade_seed si existe
                if event_data.get("cascade_seed"):
                    seed = create_cascade_seed(event_data.get("cascade_seed"), turn, event)
                    if seed:
                        new_seeds.append(seed)

        print(f"[NARRATIVE] {len(events)} eventos generados, {len(new_seeds)} seeds de cascada")
        return events, new_seeds

    except requests.exceptions.Timeout:
        print(f"[NARRATIVE] Timeout esperando respuesta")
        return [], []
    except Exception as e:
        print(f"[NARRATIVE] Error: {e}")
        return [], []


def create_narrative_event(event_data: dict, turn: int, world_data: dict) -> dict | None:
    """
    Crea un evento narrativo con validacion.
    """
    # Validar campos basicos
    if not event_data.get("title") or not event_data.get("description"):
        print(f"[DEBUG EVENT] Falta title o description en {event_data.get('title', 'SIN TITULO')}", flush=True)
        return None

    location_id = event_data.get("location_id")
    if not location_id:
        print(f"[DEBUG EVENT] Falta location_id", flush=True)
        return None

    # Normalizar location_id (Ollama retorna nombres humanos, necesitamos IDs)
    location_id_normalized = location_id.lower().replace(" ", "_")

    # Validar que location existe
    locations_by_id = {loc["id"]: loc for loc in world_data.get("locations", [])}
    print(f"[DEBUG EVENT] Buscando location '{location_id}' (normalizado: '{location_id_normalized}') en {len(locations_by_id)} ubicaciones", flush=True)

    # Intentar con ID normalizado primero, luego con el ID original
    if location_id_normalized not in locations_by_id and location_id not in locations_by_id:
        print(f"[DEBUG EVENT] Location no encontrada. Disponibles: {list(locations_by_id.keys())}", flush=True)
        return None

    # Usar el ID que encontramos
    location_id = location_id_normalized if location_id_normalized in locations_by_id else location_id

    # Validar kingdoms_involved
    kingdoms_by_id = {k["id"]: k for k in world_data.get("kingdoms", [])}
    kingdoms_involved = [k for k in event_data.get("kingdoms_involved", []) if k in kingdoms_by_id]

    # Procesar effects con validacion
    effects = []
    for effect in event_data.get("effects", []):
        validated_effect = validate_effect(effect, world_data)
        if validated_effect:
            effects.append(validated_effect)

    # Crear evento
    event = {
        "id": f"evt_{turn}_{len(world_data.get('events', []))}",
        "turn": turn,
        "title": str(event_data.get("title", ""))[:100],
        "description": str(event_data.get("description", ""))[:500],
        "category": event_data.get("category", "rumor"),
        "location_id": location_id,
        "kingdoms_involved": kingdoms_involved,
        "source": "narrative",
        "effects": effects,
        "timestamp": datetime.now().isoformat()
    }

    return event


def validate_effect(effect: dict, world_data: dict) -> dict | None:
    """
    Valida y clampa un effect.
    """
    target_type = effect.get("target_type")
    target_id = effect.get("target_id")
    field = effect.get("field")
    delta = effect.get("delta", 0)

    # Validar tipos
    if target_type not in ["location", "kingdom", "relationship"]:
        return None

    # Clampar delta
    try:
        delta = int(delta)
        delta = max(-20, min(20, delta))
    except (ValueError, TypeError):
        return None

    # Validar existencia del target
    if target_type == "location":
        locations_by_id = {loc["id"]: loc for loc in world_data.get("locations", [])}
        if target_id not in locations_by_id:
            return None

    elif target_type == "kingdom":
        kingdoms_by_id = {k["id"]: k for k in world_data.get("kingdoms", [])}
        if target_id not in kingdoms_by_id:
            return None

    elif target_type == "relationship":
        kingdoms = effect.get("kingdoms", [])
        if len(kingdoms) != 2:
            return None
        kingdoms_by_id = {k["id"]: k for k in world_data.get("kingdoms", [])}
        if not all(k in kingdoms_by_id for k in kingdoms):
            return None

    return {
        "target_type": target_type,
        "target_id": target_id,
        "field": field,
        "delta": delta
    }


def create_cascade_seed(seed_data: dict, turn: int, parent_event: dict) -> dict | None:
    """
    Crea una semilla de cascada desde los datos del evento.
    """
    if not seed_data.get("seed_prompt"):
        return None

    return {
        "id": f"seed_{turn}_{parent_event['id']}",
        "created_turn": turn,
        "fire_on_turn": turn + seed_data.get("delay_turns", 1),
        "condition_type": "always",
        "condition": {},
        "seed_prompt": seed_data.get("seed_prompt"),
        "location_id": parent_event.get("location_id"),
        "kingdoms_involved": parent_event.get("kingdoms_involved", []),
        "expires_turn": turn + 5
    }


def clean_json_string(json_str: str) -> str:
    """
    Limpia errores comunes en JSON generado por LLM (comas finales, etc).
    """
    # Remover comas antes de ] y }
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    return json_str


def extract_json_robust(response: str) -> dict | None:
    """
    Extrae JSON de forma robusta: intenta parse directo, luego busca braces balanceadas.
    """
    # Intento 1: JSON directo
    try:
        return json.loads(response)
    except:
        pass

    # Intento 2: encontrar todas las posiciones de { y encontrar matches balanceados
    print(f"[DEBUG JSON] Buscando {{ en response de {len(response)} chars", flush=True)
    brace_count = response.count("{")
    print(f"[DEBUG JSON] Total {{ encontrados: {brace_count}", flush=True)

    for start_pos in range(len(response)):
        if response[start_pos] == "{":
            print(f"[DEBUG JSON] Encontrado {{ en posición {start_pos}", flush=True)
            # Desde este {{, buscar el }} balanceado
            depth = 0
            for end_pos in range(start_pos, len(response)):
                if response[end_pos] == "{":
                    depth += 1
                elif response[end_pos] == "}":
                    depth -= 1
                    if depth == 0:
                        # Encontramos {{ ... }} balanceado
                        print(f"[DEBUG JSON] Brace balanceado en {end_pos}, intentando parse...", flush=True)
                        try:
                            candidate = response[start_pos:end_pos+1]
                            print(f"[DEBUG JSON] Candidato: {candidate[:100]}...", flush=True)
                            # Limpiar errores comunes de LLM
                            cleaned = clean_json_string(candidate)
                            print(f"[DEBUG JSON] Limpiado: {cleaned[:100]}...", flush=True)
                            result = json.loads(cleaned)
                            print(f"[DEBUG JSON] ¡Parse exitoso!", flush=True)
                            return result
                        except Exception as e:
                            # Este no fue válido, continuar buscando
                            print(f"[DEBUG JSON] Parse fallido: {e}", flush=True)
                            break

    print(f"[DEBUG JSON] No se encontró JSON válido", flush=True)
    return None


def generate_example_events(world_data: dict, turn: int, location_scores: list) -> dict:
    """
    Genera eventos de ejemplo para probar el sistema mientras debugueamos Ollama.
    """
    if not location_scores:
        return None

    examples = [
        {
            "title": "Comerciantes reportan precios inflados",
            "description": "Los precios en el mercado han subido un 15% esta semana. Los mercaderes locales culpan a los nuevos impuestos del reino. Hay ira entre la poblacion.",
            "category": "social",
            "location_id": location_scores[0]["id"],
            "kingdoms_involved": [],
            "effects": [
                {"target_type": "location", "target_id": location_scores[0]["id"], "field": "unrest", "delta": 10},
                {"target_type": "location", "target_id": location_scores[0]["id"], "field": "wealth", "delta": -5}
            ]
        },
        {
            "title": "Avistamiento de exploradores desconocidos",
            "description": "Guardias fronterizos reportan a 5 jinetes en armadura desconocida, merodeando cerca de la frontera. No atacaron, solo observaban. Los exploradores desaparecieron al oscurecer.",
            "category": "military",
            "location_id": location_scores[0]["id"] if len(location_scores) > 0 else "neutral_trading_post",
            "kingdoms_involved": [],
            "effects": [
                {"target_type": "location", "target_id": location_scores[0]["id"] if len(location_scores) > 0 else "neutral_trading_post", "field": "tension", "delta": 15}
            ]
        }
    ]

    return {"events": examples}
