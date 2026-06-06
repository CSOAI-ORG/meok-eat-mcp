# MEOK EAT Deployment Guide

## Local Development

```bash
git clone https://github.com/CSOAI-ORG/meok-eat-mcp.git
cd meok-eat-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
python -m meok_eat_mcp.server
```

## PyPI Publish

```bash
python -m build
python -m twine upload dist/*
```

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e ".[dev]"
EXPOSE 3101
CMD ["python", "-m", "meok_eat_mcp.server"]
```

## MCP Client Config

### Claude Desktop
```json
{
  "mcpServers": {
    "meok-eat": {
      "command": "python",
      "args": ["-m", "meok_eat_mcp.server"]
    }
  }
}
```

### Smithery
```yaml
# smithery.yaml
startCommand:
  type: stdio
  configSchema:
    type: object
    properties: {}
  commandFunction: |
    (config) => ({command: "python", args: ["-m", "meok_eat_mcp.server"]})
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEOK_EAT_PORT` | 3101 | MCP server port |
| `MEOK_EAT_LOG_LEVEL` | INFO | Logging level |

## Health Check

```bash
curl http://localhost:3101/health
```
