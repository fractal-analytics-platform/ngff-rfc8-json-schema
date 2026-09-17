import sys
import json
from pathlib import Path
from jsonschema import validate, ValidationError
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parents[0] / "schemas"
ROOT_SCHEMA = json.loads((SCHEMA_DIR / "ome.json").read_text())


def replace_refs(obj):
    for key, value in obj.items():
        if key == "$ref" and not value.startswith("#"):
            id = value[:-len(".schema")]
            obj[key] = f"#/$defs/{id}"
        elif type(value) is dict:
            replace_refs(value)
        elif type(value) is list:
            for v in value:
                if type(v) is dict:
                  replace_refs(v)


def build_single_schema():
    schemas = {}
    root_schema = None
    defs = {}
    for path in SCHEMA_DIR.glob("*.json"):
        schema = json.loads(path.read_text())
        if schema["$id"] == "ome.schema":
            root_schema = schema
        else:
            if "$defs" in schema:
                d = schema["$defs"]
                replace_refs(d)
                defs.update(d)
                del schema["$defs"]
            schemas[schema["$id"]] = schema
        del schema["$id"]

    replace_refs(root_schema)

    for id, schema in schemas.items():
        id = id[:-len(".schema")]
        replace_refs(schema)
        defs[id] = schema

    root_schema["$defs"] = defs

    print(json.dumps(root_schema, indent=2))
    

if __name__ == "__main__":
    build_single_schema()
