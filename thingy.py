import re
from collections import OrderedDict

import six


class classproperty(property):

    def __get__(self, cls, owner):
        return self.fget(owner)


class View(object):

    def __init__(self, defaults=False, include=None, exclude=None,
                 ordered=False):
        self.defaults = defaults
        if isinstance(include, six.string_types):
            include = [include]
        self.include = include or []
        if isinstance(exclude, six.string_types):
            exclude = [exclude]
        self.exclude = exclude or []
        self.ordered = ordered

    def __call__(self, thingy):
        if self.ordered:
            d = OrderedDict()
        else:
            d = dict()
        if not isinstance(thingy, Thingy):
            return d
        for attr in self.include:
            key = attr
            if isinstance(attr, tuple):
                attr, key = attr
            d.update({key: getattr(thingy, attr)})
        if self.defaults:
            for key, value in thingy.__dict__.items():
                d.setdefault(key, value)
        for field in self.exclude:
            d.pop(field, None)
        return d


class ThingyMetaClass(type):

    def __new__(cls, name, bases, attrs):
        attrs.setdefault("_views", {})
        klass = type.__new__(cls, name, bases, attrs)
        if "defaults" not in klass._views:
            klass.define_view("defaults", defaults=True)
        return klass


@six.add_metaclass(ThingyMetaClass)
class Thingy(object):
    _view_cls = View
    _silent = True

    def __init__(self, *args, **kwargs):
        self._update(*args, **kwargs)

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if self._silent:
                return None
            raise

    @classmethod
    def define_view(cls, name, *args, **kwargs):
        cls._views.update({name: cls._view_cls(*args, **kwargs)})

    def _update(self, *args, **kwargs):
        for arg in args:
            self.__dict__.update(**arg)
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def update(self, *args, **kwargs):
        self._update(*args, **kwargs)

    def view(self, name="defaults", *args, **kwargs):
        return self._views[name](self, *args, **kwargs)


class DatabaseThingy(Thingy):
    _database = None
    _table = None

    @classmethod
    def _get_database_from_table(cls, table):
        raise AttributeError("Undefined database.")

    @classmethod
    def _get_database_from_name(cls, name):
        raise AttributeError("Undefined database.")

    @classmethod
    def _get_table_from_database(cls, database):
        raise AttributeError("Undefined table.")

    @classmethod
    def _get_table_from_name(cls, name):
        raise AttributeError("Undefined table.")

    @classmethod
    def _get_database_name(cls, database):
        pass

    @classmethod
    def _get_table_name(cls, table):
        pass

    @classproperty
    def database(cls):
        if not cls._database:
            if cls._table:
                cls._database = cls._get_database_from_table(cls._table)
            elif cls.database_name:
                cls._database = cls._get_database_from_name(cls.database_name)
        return cls._database

    @classproperty
    def table(cls):
        if not cls._table:
            if cls._database:
                cls._table = cls._get_table_from_database(cls._database)
            elif cls.table_name:
                cls._table = cls._get_table_from_name(cls.table_name)
        return cls._table

    @classproperty
    def names(cls):
        return re.findall("([A-Z][a-z]+)", cls.__name__)

    @classproperty
    def database_name(cls):
        if cls._database:
            return cls._get_database_name(cls._database)
        try:
            name = cls.names[-2].lower()
        except IndexError:
            raise AttributeError("Undefined database.")
        else:
            return name

    @classproperty
    def table_name(cls):
        if cls._table:
            return cls._get_table_name(cls._table)
        return cls.names[-1].lower()


__all__ = ["View", "Thingy", "DatabaseThingy"]
