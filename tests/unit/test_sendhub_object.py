import json
from unittest.mock import patch

import pytest
from sendhub.sendhub_object import SendHubObject, SendHubObjectEncoder


# Dummy camel_to_snake and convert_to_sendhub_object for patching
def dummy_camel_to_snake(s):
    return s.lower()

def dummy_convert_to_sendhub_object(val):
    return val

@patch("sendhub.sendhub_object.camel_to_snake", side_effect=dummy_camel_to_snake)
@patch("sendhub.sendhub_object.convert_to_sendhub_object", side_effect=dummy_convert_to_sendhub_object)
def test_init_and_set_get_attr(mock_convert, mock_camel):
    obj = SendHubObject()
    obj.foo = "bar"
    assert obj.foo == "bar"
    assert "foo" in obj._values

def test_set_and_get_item():
    obj = SendHubObject()
    obj["key"] = "value"
    assert obj["key"] == "value"
    assert obj.get("key") == "value"
    assert obj.get("missing", 123) == 123

def test_setdefault():
    obj = SendHubObject()
    assert obj.setdefault("a", 1) == 1
    assert obj["a"] == 1
    obj["b"] = 2
    assert obj.setdefault("b", 3) == 2

def test_keys_and_values():
    obj = SendHubObject()
    obj["a"] = 1
    obj["b"] = 2
    keys = obj.keys()
    values = obj.values()
    assert set(keys) == {"a", "b"}
    assert set(values) == {1, 2}

def test_getitem_keyerror():
    obj = SendHubObject()
    with pytest.raises(KeyError):
        _ = obj["missing"]

def test_getattr_missing():
    obj = SendHubObject()
    assert getattr(obj, "missing", None) is None


def test_repr_includes_object_and_id_markers():
    obj = SendHubObject()
    obj["object"] = "entitlement"
    obj["id"] = "obj_123"
    rendered = repr(obj)
    assert "self.get('object').encode('utf8')" in rendered
    assert "id={self.get('id').encode('utf8')}" in rendered

@patch("sendhub.sendhub_object.camel_to_snake", side_effect=dummy_camel_to_snake)
@patch("sendhub.sendhub_object.convert_to_sendhub_object", side_effect=dummy_convert_to_sendhub_object)
def test_construct_from_and_refresh_from(mock_convert, mock_camel):
    d = {"id": "abc", "FooBar": 123}
    obj = SendHubObject.construct_from(d)
    assert isinstance(obj, SendHubObject)
    assert obj.id == "abc"
    assert obj.foobar == 123

    # refresh_from with non-dict raises
    with pytest.raises(TypeError):
        obj.refresh_from("not a dict")

def test_construct_from_typeerror():
    with pytest.raises(TypeError):
        SendHubObject.construct_from("not a dict")

def test_to_dict_and_str_repr():
    obj = SendHubObject()
    obj["a"] = 1
    obj["b"] = [2, 3]
    d = obj.to_dict()
    assert d == {"a": 1, "b": [2, 3]}
    s = str(obj)
    assert isinstance(s, str)
    r = repr(obj)
    assert isinstance(r, str)
    assert "SendHubObject" in r
    assert "JSON:" in r


def test_to_dict_serializes_nested_objects_and_skips_internal_id():
    parent = SendHubObject()
    child = SendHubObject()
    child["name"] = "nested"
    parent["_id"] = "internal-only"
    parent["child"] = child
    parent["items"] = [child, 2]

    assert parent.to_dict() == {
        "child": {"name": "nested"},
        "items": [{"name": "nested"}, 2],
    }

def test_encoder_with_sendhub_object():
    obj = SendHubObject()
    obj["x"] = 1
    encoded = json.dumps(obj, cls=SendHubObjectEncoder)
    assert '"x": 1' in encoded

def test_encoder_with_non_sendhub_object():
    data = {"a": 1}
    encoded = json.dumps(data, cls=SendHubObjectEncoder)
    assert '"a": 1' in encoded


def test_encoder_default_non_sendhub_object_raises_type_error():
    encoder = SendHubObjectEncoder()
    with pytest.raises(TypeError):
        encoder.default(object())
