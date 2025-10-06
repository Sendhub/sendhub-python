import json

from sendhub import camel_to_snake, convert_to_sendhub_object


class SendHubObject:
    """Class to make SendHub object"""
    def __init__(self, _id=None, **_params):
        self.__dict__['_values'] = set()
        self._id = ""

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        self._values.add(k)

    def __getattr__(self, k):
        try:
            return self.__dict__[k]
        except KeyError:
            pass

    def __setitem__(self, k, val):
        setattr(self, k, val)

    def __getitem__(self, k):
        if k in self._values:
            return self.__dict__[k]
        raise KeyError(k)

    def __repr__(self):
        """class string representation"""
        type_string = ''
        if isinstance(self.get('object'), str):
            type_string = f" self.get('object').encode('utf8')"

        id_string = ''
        if isinstance(self.get('id'), str):
            id_string = " id={self.get('id').encode('utf8')}"

        return f"<{type(self).__name__}{type_string}{id_string} at {hex(id(self))}> JSON: {json.dumps(self.to_dict(), sort_keys=True, indent=2, cls=SendHubObjectEncoder)}"

    def __str__(self):
        """string representation for an object"""
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, cls=SendHubObjectEncoder)

    def get(self, k, default=None):
        """Get object value"""
        try:
            return self[k]
        except KeyError:
            return default

    def setdefault(self, k, default=None):
        """Sets the default value if key does not exist"""
        try:
            return self[k]
        except KeyError:
            self[k] = default
            return default

    def keys(self):
        """Returns keys"""
        return list(self.to_dict().keys())

    def values(self):
        """Returns values"""
        return list(self.to_dict().values())

    @classmethod
    def construct_from(cls, values):
        """Class method for constructing the dict"""
        instance = cls(values.get('id'))
        instance.refresh_from(values)
        return instance

    def refresh_from(self, values):
        """refresh from dict"""
        for k, val in list(values.items()):
            name = camel_to_snake(k)
            self.__dict__[name] = convert_to_sendhub_object(val)
            self._values.add(name)

    def to_dict(self):
        """Converts obj as dict"""
        def _serialize(_o):
            if isinstance(_o, SendHubObject):
                return _o.to_dict()
            if isinstance(_o, list):
                return [_serialize(i) for i in _o]
            return _o

        _d = dict()
        for k in sorted(self._values):
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
