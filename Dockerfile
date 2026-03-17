FROM python:3.11-slim
 
WORKDIR /app
 
# Install dependencies first.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy source code.
COPY . .
 
# Create directories the pipeline writes to at runtime.
RUN mkdir -p logs data/events
 
# Run the pipeline to populate the DB, then start the API server.
CMD ["sh", "-c", "python -m app.pipeline && uvicorn app.main:app --host 0.0.0.0 --port 8000"]