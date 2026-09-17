import sys
import json
from pathlib import Path
from jsonschema import validate, ValidationError
from referencing import Registry, Resource


SCHEMA_DIR = Path(__file__).resolve().parents[0] / "schemas"
ROOT_SCHEMA = json.loads((SCHEMA_DIR / "ome.json").read_text())


def build_registry() -> Registry:
    registry = Registry()
    for path in SCHEMA_DIR.glob("*.json"):
        schema = json.loads(path.read_text())
        registry = registry.with_resource(
            schema["$id"],
            Resource.from_contents(schema),
        )
    return registry


def validate_collection(data):
    validate(instance=data, schema=ROOT_SCHEMA, registry=build_registry())


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print(f"Error: file does not exist: {file_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(file_path.read_text())
    validate_collection(data)
    print("Collection is valid")


if __name__ == "__main__":
    main()
