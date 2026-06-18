FROM python:3.12-slim
COPY . /app
RUN pip install --no-cache-dir /app
ENTRYPOINT ["ci-medic"]