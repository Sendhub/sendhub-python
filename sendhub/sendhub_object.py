import json
from typing import Any, Dict, List, Optional

from sendhub import camel_to_snake, convert_to_sendhub_object


class SendHubObject:
    """Class to make SendHub object"""

    def __init__(self, _id: Optional[Any] = None, **_params: Any) -> None:
        self.__dict__["_values"] = set()
        self._id = ""

    def __setattr__(self, k: str, v: Any) -> None:
        self.__dict__[k] = v
        self._values.add(k)

    def __getattr__(self, k: str) -> Any:
        try:
            return self.__dict__[k]
        except KeyError:
            pass

    def __setitem__(self, k: str, val: Any) -> None:
        setattr(self, k, val)

    def __getitem__(self, k: str) -> Any:
        if k in self._values:
            return self.__dict__[k]
        raise KeyError(k)

    def __repr__(self) -> str:
        """class string representation"""
        type_string = ""
        if isinstance(self.get("object"), str):
            type_string = " self.get('object').encode('utf8')"

        id_string = ""
        if isinstance(self.get("id"), str):
            id_string = " id={self.get('id').encode('utf8')}"

        return f"<{type(self).__name__}{type_string}{id_string} at {hex(id(self))}> JSON: {json.dumps(self.to_dict(), sort_keys=True, indent=2, cls=SendHubObjectEncoder)}"

    def __str__(self) -> str:
        """string representation for an object"""
        return json.dumps(
            self.to_dict(), sort_keys=True, indent=2, cls=SendHubObjectEncoder
        )

    def get(self, k: str, default: Optional[Any] = None) -> Any:
        """Get object value"""
        try:
            return self[k]
        except KeyError:
            return default

    def setdefault(self, k: str, default: Optional[Any] = None) -> Any:
        """Sets the default value if key does not exist"""
        try:
            return self[k]
        except KeyError:
            self[k] = default
            return default

    def keys(self) -> List[str]:
        """Returns keys"""
        return list(self.to_dict().keys())

    def values(self) -> List[Any]:
        """Returns values"""
        return list(self.to_dict().values())

    @classmethod
    def construct_from(cls, values: Dict[str, Any]) -> "SendHubObject":
        """Class method for constructing the dict"""
        if not isinstance(values, dict):
            raise TypeError("values must be a dict")
        instance = cls(values.get("id"))
        instance.refresh_from(values)
        return instance

    def refresh_from(self, values: Dict[str, Any]) -> None:
        """refresh from dict"""
        if not isinstance(values, dict):
            raise TypeError("values must be a dict")
        for k, val in list(values.items()):
            name = camel_to_snake(k)
            self.__dict__[name] = convert_to_sendhub_object(val)
            self._values.add(name)

    def to_dict(self) -> Dict[str, Any]:
        """Converts obj as dict, excluding '_id' key."""

        def _serialize(_o: Any) -> Any:
            if isinstance(_o, SendHubObject):
                return _o.to_dict()
            if isinstance(_o, list):
                return [_serialize(i) for i in _o]
            return _o

        _d: Dict[str, Any] = dict()
        for k in sorted(self._values):
            if k == "_id":
                continue
            _v = getattr(self, k)
            _v = _serialize(_v)
            _d[k] = _v

        return _d


class SendHubObjectEncoder(json.JSONEncoder):
    """Class for SendHub object encoder"""

    def default(self, obj):
        """Converts obj to dict"""
        if isinstance(obj, SendHubObject):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)
