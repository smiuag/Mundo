FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn requests

COPY main.py .
COPY core core/
COPY agents agents/
COPY narrative narrative/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
