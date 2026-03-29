# inventree-mcp Docker image
# renovate: datasource=docker registry=https://docker-hub.mlvdhmcntrl.uk depName=python
FROM docker-hub.mlvdhmcntrl.uk/python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "git+https://github.com/munin92/inventree-mcp@main"

EXPOSE 8001

CMD ["inventree-mcp"]
