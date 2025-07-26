FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Set PYTHONPATH so modules like 'service', 'orchestrator' can be found
ENV PYTHONPATH=/app

# Run the FastAPI app
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
