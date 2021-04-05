import typing
import inspect
import json


# https://github.com/pyrogram/pyrogram/blob/v1.1.0/pyrogram/types/object.py#L26
class Meta(type, metaclass=type("", (type,), {"__str__": lambda _: "~hi"})):
    def __str__(self):
        return f"<class 'unalix.types.{self.__name__}'>"


# https://github.com/pyrogram/pyrogram/blob/v1.1.0/pyrogram/types/object.py#L31
class Object(metaclass=Meta):


    @staticmethod
    def _default(obj):

        _dict = {}

        for attribute in filter(lambda x: not x.startswith("__"), obj.__dict__):
            object = getattr(obj, attribute)
            if "_list" in dir(object):
                _dict.update({attribute: list(object)})
            elif "_list" in dir(obj):
                _dict.update({obj.__class__.__name__.lower(): obj._list})
            else:
                _dict.update({attribute: object})

        return _dict


    def __str__(self):
        return json.dumps(
            self, indent=4, default=Object._default, ensure_ascii=False)


    def __repr__(self):
        _repr = []
        for attribute in filter(lambda x: not x.startswith("__"), self.__dict__):
            object = getattr(self, attribute)
            if "_list" in dir(object):
                _repr.append(f"{attribute}={object.__class__.__name__}({repr(object._list)})")
            elif "_list" in dir(self):
                _repr.append(repr(self._list))
            else:
                _repr.append(f"{attribute}={repr(object)}")
        return "unalix.types.{}({})".format(
            self.__class__.__name__,
            ", ".join(_repr)
        )


    def __eq__(self, other):
        for attr in self.__dict__:
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                return False

        return True


class Dict(Object):


    def __iter__(self):

        iterables = {}

        attributes = [
            argument for argument in (
                inspect.getargs(self.__init__.__code__).args) if (
                argument != "self" and not argument.startswith("_"))
        ]

        for attribute in attributes:
            object = getattr(self, attribute)
            if isinstance(object, (List, list)):
                iterables.update({attribute: list(object)})
            elif isinstance(object, (Dict, dict)):
                iterables.update({attribute: dict(object)})
            else:
                iterables.update({attribute: object})

        for key, value in iterables.items():
            yield (key, value)


    def __getitem__(self, item):
        return getattr(self, item)


    def __setitem__(self, key, value):
        setattr(self, key, value)


    def __delitem__(self, item):
        delattr(self, item)


class List(Object):


    def __init__(self, _list=None):
        if _list is None:
            self._list = []
        else:
            self._list = _list


    def __iter__(self):
        items = []
        for item in self.list():
            if isinstance(item, (Dict, dict)):
                items.append(dict(item))
            elif isinstance(item, (str, int, float, bool, type(None))):
                items.append(item)
            else:
                raise TypeError(f"expecting Dict, dict, str, float, bool or NoneType, got {item.__class__.__name__}")
        return iter(items)


    def __getitem__(self, item):
        return self._list[item]


    def __len__(self):
        return len(self._list)


    def append(self, item):
        self._list.append(item)


    def iter(self):
        return iter(self._list)


    def list(self):
        return list(self._list)

