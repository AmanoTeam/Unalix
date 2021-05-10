import typing
import inspect
import json


# https://github.com/pyrogram/pyrogram/blob/v1.1.0/pyrogram/types/object.py#L26
class MetaClass(type, metaclass=type("", (type,), {"__str__": lambda _: "~hi"})):

    def __str__(self):
        return f"<class 'unalix.types.{self.__name__}'>"


# https://github.com/pyrogram/pyrogram/blob/v1.1.0/pyrogram/types/object.py#L31
class BaseClass(metaclass=MetaClass):


    def __str__(self):

        return json.dumps(
            self,
            indent=4,
            default=self.default,
            ensure_ascii=False
        )


class Dict(BaseClass):


    def __iter__(self):

        iterables = {}

        code = self.__init__.__code__
        arguments = inspect.getargs(code).args

        arguments.remove("self")

        for argument in arguments:
            
            attribute = getattr(self, argument)
            
            if isinstance(attribute, List):
                iterables.update(
                    {
                        argument: list(attribute)
                    }
                )
            elif isinstance(attribute, Dict):
                iterables.update(
                    {
                        argument: dict(attribute)
                    }
                )
            else:
                iterables.update(
                    {
                        argument: attribute
                    }
                )

        yield from iterables.items()


    def __getitem__(self, item):
        return getattr(self, item)


    def __setitem__(self, key, value):
        setattr(self, key, value)


    def __delitem__(self, item):
        delattr(self, item)


    def __repr__(self):

        code = self.__init__.__code__
        arguments = inspect.getargs(code).args

        arguments.remove("self")

        data = []

        for argument in arguments:
            
            attribute = getattr(self, argument)
            
            if isinstance(attribute, List):
                data.append(f"{argument}={attribute.__class__.__name__}({repr(attribute.base_list)})")
            else:
                data.append(f"{argument}={repr(attribute)}")

        class_name = self.__class__.__name__
        representation = ", ".join(data)

        return f"unalix.types.{class_name}({representation})"

    @staticmethod
    def default(obj):

        serialized_object = {}

        code = obj.__init__.__code__
        arguments = inspect.getargs(code).args

        arguments.remove("self")

        for argument in arguments:

            attribute = getattr(obj, argument)

            if isinstance(attribute, List):
                serialized_object.update(
                    {
                        argument: list(attribute)
                    }
                )
            else:
                serialized_object.update(
                    {
                        argument: attribute
                    }
                )

        return serialized_object


class List(BaseClass):


    def __init__(self, base_list=None):

        if base_list is None:
            self.base_list = []
        else:
            self.base_list = base_list


    def __iter__(self):

        iterable = []

        for item in self.base_list:
            if isinstance(item, Dict):
                iterable.append(dict(item))
            elif isinstance(item, (str, int, float, bool, type(None))):
                iterable.append(item)
            else:
                raise TypeError

        return iter(iterable)


    def __getitem__(self, item):
        return self.base_list[item]


    def __len__(self):
        return len(self.base_list)


    def append(self, item):
        self.base_list.append(item)


    def iter(self):
        return iter(self.base_list)


    def list(self):
        return list(self.base_list)


    def __repr__(self):

        class_name = self.__class__.__name__
        representation = repr(self.base_list)

        return f"unalix.types.{class_name}({representation})"


    @staticmethod
    def default(obj):

        if isinstance(obj, List):
            return getattr(obj, "base_list")

        if isinstance(obj, Dict):
            return dict(obj)

        raise TypeError
