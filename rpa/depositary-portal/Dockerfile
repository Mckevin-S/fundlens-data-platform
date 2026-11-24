FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "fastapi==0.115.*" "uvicorn==0.32.*" "python-multipart==0.0.*" && useradd --system app
COPY portal portal
USER app
EXPOSE 8090
CMD ["uvicorn", "portal.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8090"]
