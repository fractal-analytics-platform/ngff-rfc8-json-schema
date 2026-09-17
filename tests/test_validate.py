import json
from pathlib import Path

import pytest
from jsonschema import validate, ValidationError
from referencing import Registry, Resource



SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"
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


def test_valid_collection_inline_node():
    validate_collection({
      "ome": {
        "version": "0.x",
        "type": "collection",
        "name": "My Dataset",
        "id": "dataset",
        "attributes": {
          "fractal:dataset": {
            "user": "lorenzo",
            "project": "base-dataset"
          }
        },
        "nodes": [
          {
            "type": "collection",
            "name": "My Plate",
            "id": "plate",
            "path": {
              "type": "json",
              "path": "./plate/plate.json"
            }
          }
        ]
      }
    })


def test_missing_ome_in_root():
    with pytest.raises(ValidationError, match=r"'ome' is a required property"):
        validate_collection({})


def test_missing_version():
    with pytest.raises(ValidationError, match=r"'version' is a required property"):
        validate_collection({"ome": {"type": "collection", "name": "foo"}})


def test_missing_name():
    with pytest.raises(ValidationError):
        validate_collection({"ome": {"version": "0.x", "type": "collection"}})


def test_invalid_id():
    with pytest.raises(ValidationError):
        validate_collection({"ome": {"version": "0.x", "type": "collection", "name": "foo", "id": ""}})


def test_invalid_attributes_type():
    with pytest.raises(ValidationError):
        validate_collection({"ome": {"version": "0.x", "type": "collection", "name": "foo", "attributes": []}})


def test_valid_empty_labels():
    validate_collection({
      "ome": {
        "version": "0.x",
        "name": "root",
        "type": "collection",
        "nodes": [
          {
            "type": "multiscale",
            "name": "foo",
            "attributes": {
              "labels": {},
              "coordinateSystems": [
                {
                  "id": "x",
                  "axes": [
                    {
                      "name": "x",
                      "type": "space",
                      "unit": "micrometer"
                    },
                    {
                      "name": "y",
                      "type": "space",
                      "unit": "micrometer"
                    }
                  ]
                }
              ]
            },
            "path": {"type": "json", "path": "./foo.json"}
          }
        ]
      }
    })


def test_labels_attribute_missing_label_value():
    with pytest.raises(ValidationError):
        validate_collection({
          "ome": {
            "version": "0.x",
            "name": "root",
            "type": "collection",
            "nodes": [
              {
                "type": "multiscale",
                "name": "foo",
                "attributes": {
                  "labels": {
                    "labelAttributes": [{}]
                  },
                  "coordinateSystems": [
                    {
                      "id": "x",
                      "axes": [
                        {
                          "name": "x",
                          "type": "space",
                          "unit": "micrometer"
                        },
                        {
                          "name": "y",
                          "type": "space",
                          "unit": "micrometer"
                        }
                      ]
                    }
                  ]
                },
                "path": {"type": "json", "path": "./foo.json"}
              }
            ]
          }
        })


def test_valid_labels_attribute():
    validate_collection({
      "ome": {
        "version": "0.x",
        "name": "root",
        "type": "collection",
        "nodes": [
          {
            "type": "multiscale",
            "name": "foo",
            "attributes": {
              "labels": {
                "labelAttributes": [
                  {"labelValue": 1, "color": [0, 255, 100, 255]}
                ]
              },
              "coordinateSystems": [
                {
                  "id": "x",
                  "axes": [
                    {
                      "name": "x",
                      "type": "space",
                      "unit": "micrometer"
                    },
                    {
                      "name": "y",
                      "type": "space",
                      "unit": "micrometer"
                    }
                  ]
                }
              ]
            },
            "path": {"type": "json", "path": "./foo.json"}
          }
        ]
      }
    })

def test_invalid_labels_color():
    with pytest.raises(ValidationError):
        validate_collection({
          "ome": {
            "version": "0.x",
            "name": "root",
            "type": "collection",
            "nodes": [
              {
                "type": "multiscale",
                "name": "foo",
                "attributes": {
                  "labels": {
                    "labelAttributes": [
                      {"labelValue": 1, "color": [0]}
                    ]
                  },
                  "coordinateSystems": [
                    {
                      "id": "x",
                      "axes": [
                        {
                          "name": "x",
                          "type": "space",
                          "unit": "micrometer"
                        },
                        {
                          "name": "y",
                          "type": "space",
                          "unit": "micrometer"
                        }
                      ]
                    }
                  ]
                },
                "path": {"type": "json", "path": "./foo.json"}
              }
            ]
          }
        })


def test_valid_singlescale():
    validate_collection({
      "ome": {
        "version": "0.x",
        "name": "root",
        "type": "collection",
        "nodes": [
          {
            "type": "singlescale",
            "name": "single",
            "attributes": {
              "coordinateTransformations": [
                {
                  "type": "translation",
                  "translation": [0, 0, 100],
                  "input": {"id": "physical", "path": {"type": "json", "path": "./foo.json"}},
                  "output": {"id": "world"}
                }
              ]
            },
            "path": {"type": "json", "path": "./foo.json"}
          }
        ]
      }
    })


def test_missing_attributes_in_multiscale():
    with pytest.raises(ValidationError):
        validate_collection({
            "ome": {
              "version": "0.x",
              "name": "root",
              "type": "collection",
              "nodes": [
                {
                  "type": "multiscale",
                  "name": "foo",
                  "path": {"type": "json", "path": "./foo.json"}
                }
              ]
            }
        })


def test_invalid_coordinateTransformations_missing_type():
    with pytest.raises(ValidationError):
        validate_collection({
          "ome": {
            "version": "0.x",
            "name": "root",
            "type": "collection",
            "nodes": [
              {
                "type": "singlescale",
                "name": "single",
                "attributes": {
                  "coordinateTransformations": [
                    {
                      "translation": [0, 0, 100],
                      "input": {"id": "physical", "path": {"type": "json", "path": "./foo.json"}},
                      "output": {"id": "world"}
                    }
                  ]
                },
                "path": {"type": "json", "path": "./foo.json"}
              }
            ]
          }
        })


def test_invalid_coordinateTransformations_missing_output_id():
    with pytest.raises(ValidationError):
        validate_collection({
          "ome": {
            "version": "0.x",
            "name": "root",
            "type": "collection",
            "nodes": [
              {
                "type": "singlescale",
                "name": "single",
                "attributes": {
                  "coordinateTransformations": [
                    {
                      "type": "translation",
                      "translation": [0, 0, 100],
                      "input": {"id": "physical", "path": {"type": "json", "path": "./foo.json"}},
                      "output": {}
                    }
                  ]
                },
                "path": {"type": "json", "path": "./foo.json"}
              }
            ]
          }
        })


def test_valid_scene():
    validate_collection({
      "ome": {
        "version": "0.x",
        "name": "root",
        "type": "collection",
        "nodes": [{
          "type": "collection",
          "name": "name",
          "attributes": {
            "scene": {
              "coordinateTransformations": [{
                "type": "translation",
                "translation": [0, 0, 100],
                "input": {"id": "physical"},
                "output": {"id": "world"},
              }],
              "coordinateSystems": [{
                "id": "physical",
                "name": "The physical coordinate system",
                "axes": [
                  {
                    "name": "x",
                    "type": "space",
                    "unit": "micrometer"
                  },
                  {
                    "name": "y",
                    "type": "space",
                    "unit": "micrometer"
                  }
                ],
              }],
            }
          },
          "path": {"type": "json", "path": "./foo.json"}
        }]
      }
    })


def test_invalid_scene_missing_coordinateTransformations():
    with pytest.raises(ValidationError):
        validate_collection({
      "ome": {
        "version": "0.x",
        "name": "root",
        "type": "collection",
        "nodes": [{
          "type": "collection",
          "name": "name",
          "attributes": {
            "scene": {
              "coordinateSystems": [{
                "id": "physical",
                "name": "The physical coordinate system",
                "axes": [
                  {
                    "name": "x",
                    "type": "space",
                    "unit": "micrometer"
                  },
                  {
                    "name": "y",
                    "type": "space",
                    "unit": "micrometer"
                  }
                ],
              }],
            }
          },
          "path": {"type": "json", "path": "./foo.json"}
        }]
      }
    })


def test_invalid_scene_missing_coordinateSystem_id():
    with pytest.raises(ValidationError):
        validate_collection({
      "ome": {
        "version": "0.x",
        "name": "root",
        "type": "collection",
        "nodes": [{
          "type": "collection",
          "name": "name",
          "attributes": {
            "scene": {
              "coordinateTransformations": [{
                "type": "translation",
                "translation": [0, 0, 100],
                "input": {"id": "physical"},
                "output": {"id": "world"},
              }],
              "coordinateSystems": [{
                "name": "The physical coordinate system",
                "axes": [
                  {
                    "name": "x",
                    "type": "space",
                    "unit": "micrometer"
                  },
                  {
                    "name": "y",
                    "type": "space",
                    "unit": "micrometer"
                  }
                ],
              }],
            }
          },
          "path": {"type": "json", "path": "./foo.json"}
        }]
      }
    })


def test_invalid_multiscale_missing_nodes_or_path():
    with pytest.raises(ValidationError):
        validate_collection({
          "ome": {
            "version": "0.x",
            "name": "root",
            "type": "collection",
            "nodes": [
              {
                "type": "multiscale",
                "name": "multi",
                "attributes": {
                  "coordinateSystems": [
                    {
                      "id": "coord",
                      "axes": [
                        {
                          "name": "x",
                          "type": "space",
                          "unit": "micrometer"
                        },
                        {
                          "name": "y",
                          "type": "space",
                          "unit": "micrometer"
                        }
                      ]
                    }
                  ]
                }
              }
            ]
          }
        })


def test_invalid_multiscale_both_nodes_and_path():
    with pytest.raises(ValidationError):
        validate_collection({
          "ome": {
            "version": "0.x",
            "name": "root",
            "type": "collection",
            "nodes": [
              {
                "type": "multiscale",
                "name": "multi",
                "attributes": {
                  "coordinateSystems": [
                    {
                      "id": "coord",
                      "axes": [
                        {
                          "name": "x",
                          "type": "space",
                          "unit": "micrometer"
                        },
                        {
                          "name": "y",
                          "type": "space",
                          "unit": "micrometer"
                        }
                      ]
                    }
                  ]
                },
                "nodes": [],
                "path": {"type": "json", "path": "./invalid.json"}
              }
            ]
          }
        })
