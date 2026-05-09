import requests
import os
import json
import re

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL = "gemma2:27b"

def call_ollama(prompt: str, timeout: int = 120) -> str:
    import sys
    try:
        print(f"[LLM] Llamando a {MODEL} en {OLLAMA_URL}...", flush=True, file=sys.stderr)
        sys.stderr.flush()
        print(f"[LLM] Prompt length: {len(prompt)} chars", flush=True, file=sys.stderr)
        sys.stderr.flush()

        print(f"[LLM] Conectando a Ollama...", flush=True, file=sys.stderr)
        sys.stderr.flush()
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        print(f"[LLM] Respuesta recibida (status {response.status_code})", flush=True, file=sys.stderr)
        sys.stderr.flush()

        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            print(f"[LLM] Respuesta parseada ({len(result)} chars)", flush=True)
            sys.stdout.flush()
            return result
        print(f"[LLM] Error HTTP {response.status_code}")
        return "error"
    except requests.exceptions.Timeout:
        print(f"[LLM] TIMEOUT después de {timeout}s esperando respuesta de {MODEL}", flush=True, file=sys.stderr)
        sys.stderr.flush()
        return "error"
    except Exception as e:
        print(f"[LLM] Error: {type(e).__name__}: {e}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return "error"

def get_kingdom_request(kingdom: dict, world_state: dict) -> dict:
    # Deterministic kingdom actions instead of LLM (Gemma 27B too slow)
    # Cycle through actions based on turn number to add variety
    import sys
    turn = world_state.get("metadata", {}).get("turn", 0)
    kingdom_idx = next((i for i, k in enumerate(world_state["kingdoms"]) if k["id"] == kingdom["id"]), 0)

    actions = ["attack", "spy", "trade", "defend", "raid", "alliance"]
    action_type = actions[(turn + kingdom_idx) % len(actions)]

    result = {
        "kingdom_id": kingdom["id"],
        "kingdom_name": kingdom["name"],
        "action": action_type,
        "target": world_state["kingdoms"][(turn + kingdom_idx + 1) % len(world_state["kingdoms"])]["name"],
        "troops": (turn % 5) * 100,
        "description": f"{kingdom['name']} realiza {action_type} en turno {turn}"
    }

    print(f"[{kingdom['name']}] Acción determinista: {action_type}", flush=True, file=sys.stderr)
    sys.stderr.flush()
    return result
