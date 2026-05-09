# World Builder - AI RPG Sandbox

Simulador de mundo para RPGs de mesa con eventos narrativos generados por IA local.

## Requisitos

- Docker Desktop o Docker + Docker Compose
- ~20GB libre (para modelo Gemma 27B)
- GPU recomendada (muy lento en CPU)

## Setup Rápido

```bash
# 1. Clonar repo
git clone <URL>
cd mundo

# 2. Descargar modelo (primera vez, tarda 30+ min)
docker run -d --name ollama ollama/ollama
docker exec ollama ollama pull gemma2:27b
docker stop ollama
docker rm ollama

# 3. Iniciar servicios
docker-compose up -d

# 4. Abrir interfaz
http://localhost:3000
```

## Usar

- **GET /world** - Ver estado del mundo (reinos, ubicaciones, eventos)
- **POST /turn** - Avanzar un turno (~10 minutos)
- **GET /events** - Ver últimos eventos generados
- **GET /kingdoms** - Ver reinos y sus estadísticas
- **GET /locations** - Ver ubicaciones y sus propiedades

## Velocidad

- Decisiones de reinos: Instantáneo (determinista)
- Narrativa: 5-10 min/turno (Gemma 27B en CPU)

Para más rápido, cambiar modelo en docker-compose.yml (ej: mistral:7b es ~3x más rápido).

## Desarrollar

```bash
# Cambios en código se aplican automáticamente (volúmenes Docker)
# Para rebuild completo:
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Estructura del Proyecto

```
mundo/
├── backend/
│   ├── main.py                 # Servidor FastAPI
│   ├── core/
│   │   ├── turn_engine.py      # Ciclo principal de turno
│   │   ├── game_controller.py  # Resolución de acciones
│   │   └── state_mutator.py    # Aplicación de efectos
│   ├── agents/
│   │   └── llm_provider.py     # Decisiones de reinos
│   ├── narrative/
│   │   ├── event_generator.py  # Generación de eventos narrativos
│   │   ├── location_scorer.py  # Identificación de ubicaciones activas
│   │   └── cascade_resolver.py # Evaluación de cascadas
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── nginx.conf
│   └── Dockerfile
├── data/
│   └── world.json              (generado al ejecutar)
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Cómo Funciona un Turno

1. **Decisiones de Reinos** - Cada reino elige una acción (atacar, comerciar, espiar, etc.)
2. **Resolución Mecánica** - Se resuelven conflictos y se generan eventos mecánicos
3. **Evaluación de Cascadas** - Se comprueban eventos pendientes del turno anterior
4. **Identificación de Ubicaciones Activas** - Se determina dónde suceden cosas
5. **Generación Narrativa** - IA genera descripción narrativa de los eventos
6. **Aplicación de Efectos** - Se actualizan tensión, riqueza, relaciones, etc.

## Notas

- El sistema usa Gemma 2 27B con Ollama para generación de eventos narrativos
- Las decisiones de reinos son deterministas (basadas en turno y reino) para velocidad
- Los eventos incluyen efectos que mutan el estado del mundo para el siguiente turno
- Las "cascade seeds" permiten que eventos causen consecuencias futuras
