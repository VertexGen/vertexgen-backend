FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/main.py .
# ENV PORT=8080
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "env:PORT"]
# CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
