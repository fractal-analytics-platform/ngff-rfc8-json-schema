from jsonschema import validate

from .load_schemas import build_registry
from .load_schemas import get_ome_schema


def validate_collection(data):
    if "ome" in data.keys():
        validate(
            instance=data,
            schema=get_ome_schema(),
            registry=build_registry(),
        )
    elif "attributes" in data.keys() and data.get("node_type") == "group":
        pass
    else:
        error = (
            "The document must include a 'ome' property, "
            "either at the document root or within an 'attributes' object. "
            "See https://ngff.openmicroscopy.org/rfc/8/index.html#metadata-storage"
        )
        raise ValueError(error)
