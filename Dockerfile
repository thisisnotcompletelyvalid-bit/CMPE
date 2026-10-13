FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/cmpe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -u 10001 -m cmpe
COPY cmpe cmpe
USER 10001
EXPOSE 8080
CMD ["uvicorn","cmpe.api:app","--host","0.0.0.0","--port","8080"]
