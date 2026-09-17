# NGFF RFC-8 JSON Schemas

Preliminary JSON Schemas for NGFF RFC-8 (collections) - see https://ngff.openmicroscopy.org/rfc/8/index.html

## Development

```bash
uv venv
uv sync
```

## Run tests

```bash
uv run pytest
```

## Validate JSON file

```bash
uv run python validate.py <file>
```

## Generate single-file JSON Schema

```bash
uv run python build_single_schema.py > ngff-rfc8.json
```
