from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
from core.turn_engine import process_turn
from threading import Thread

DATA_PATH = "/app/data/world.json"

def load_world_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {"metadata": {"name": "Aethermoor", "turn": 0}, "kingdoms": [], "locations": [], "events": []}

def save_world_data():
    """Guarda world_data a disco en un thread separado para no bloquear"""
    def _save():
        try:
            with open(DATA_PATH, "w") as f:
                json.dump(world_data, f, indent=2)
            print("[SAVE] world.json guardado exitosamente", flush=True)
        except Exception as e:
            print(f"[SAVE] Error guardando: {e}", flush=True)

    Thread(target=_save, daemon=True).start()

world_data = load_world_data()

app = FastAPI(title="World Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "world-builder-backend", "world_loaded": len(world_data.get("kingdoms", [])) > 0}

@app.get("/world")
async def get_world():
    return world_data

@app.get("/kingdoms")
async def get_kingdoms():
    return {"kingdoms": world_data.get("kingdoms", []), "count": len(world_data.get("kingdoms", []))}

@app.get("/locations")
async def get_locations():
    return {"locations": world_data.get("locations", []), "count": len(world_data.get("locations", []))}

@app.post("/turn")
async def advance_turn():
    import sys
    print("[HTTP] Iniciando endpoint /turn", flush=True, file=sys.stderr)
    sys.stderr.flush()

    print("[HTTP] Llamando process_turn()...", flush=True, file=sys.stderr)
    sys.stderr.flush()
    try:
        result = process_turn(world_data)
    except Exception as e:
        print(f"[HTTP] EXCEPTION en process_turn(): {type(e).__name__}: {e}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return JSONResponse({"error": str(e), "turn": world_data.get("metadata", {}).get("turn", -1)}, status_code=500)
    print(f"[HTTP] process_turn() retornó: {type(result)}", flush=True, file=sys.stderr)
    sys.stderr.flush()

    print("[HTTP] Llamando save_world_data()...", flush=True, file=sys.stderr)
    sys.stderr.flush()
    try:
        save_world_data()
        print("[HTTP] save_world_data() completado", flush=True, file=sys.stderr)
        sys.stderr.flush()
    except Exception as e:
        print(f"[HTTP] ERROR en save_world_data(): {e}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

    print("[HTTP] Serializando resultado a JSON...", flush=True, file=sys.stderr)
    sys.stderr.flush()
    try:
        json_str = json.dumps(result)
        print("[HTTP] JSON serialización exitosa", flush=True, file=sys.stderr)
        sys.stderr.flush()
    except Exception as e:
        print(f"[HTTP] ERROR serializando: {e}", flush=True, file=sys.stderr)
        sys.stderr.flush()
        return JSONResponse({"error": str(e), "turn": result.get("turn", -1)})

    print("[HTTP] Retornando JSONResponse...", flush=True, file=sys.stderr)
    sys.stderr.flush()
    try:
        return JSONResponse(result)
    except Exception as e:
        print(f"[HTTP] ERROR retornando JSONResponse: {e}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise

@app.get("/events")
async def get_events():
    return {"events": world_data.get("events", []), "count": len(world_data.get("events", []))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
