FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir .

EXPOSE 8001

CMD ["inventree-mcp"]
