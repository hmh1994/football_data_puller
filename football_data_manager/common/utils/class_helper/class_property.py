class ClassPropertyDescriptor:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, instance, owner):
        return self.fget(owner)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(type(instance), value)


def classproperty(func):
    """
    Decorator to define a class property.
    """
    return ClassPropertyDescriptor(func)
