FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pandas
COPY analysis_api.py .
CMD ["uvicorn", "analysis_api:app", "--host", "0.0.0.0", "--port", "8000"]
