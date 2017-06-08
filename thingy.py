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


registry = []


class ThingyMetaClass(type):

    def __new__(cls, name, bases, attrs):
        attrs.setdefault("_views", {})
        klass = type.__new__(cls, name, bases, attrs)
        if "defaults" not in klass._views:
            klass.add_view("defaults", defaults=True)
        registry.append(klass)
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
            is_property = (attr in self.__class__.__dict__)
            if not is_property and self._silent:
                return None
            raise

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.__dict__)

    @classmethod
    def add_view(cls, name, *args, **kwargs):
        cls._views.update({name: cls._view_cls(*args, **kwargs)})

    def _update(self, *args, **kwargs):
        for arg in args:
            self.__dict__.update(**arg)
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def update(self, *args, **kwargs):
        self._update(*args, **kwargs)

    def view(self, name="defaults"):
        return self._views[name](self)


names_regex = re.compile("([A-Z][a-z]+)")


class DatabaseThingy(Thingy):
    _database = None
    _table = None

    @classmethod
    def _get_database(cls, table, name):
        raise AttributeError("Undefined database.")

    @classmethod
    def _get_table(cls, database, name):
        raise AttributeError("Undefined table.")

    @classmethod
    def _get_database_name(cls, database):
        pass

    @classmethod
    def _get_table_name(cls, table):
        pass

    @classmethod
    def get_database(cls):
        if not cls._database:
            cls._database = cls._get_database(cls._table, cls.database_name)
        return cls._database

    @classmethod
    def get_table(cls):
        if not cls._table:
            cls._table = cls._get_table(cls.database, cls.table_name)
        return cls._table

    @classmethod
    def get_database_name(cls):
        if cls._database:
            return cls._get_database_name(cls._database)
        try:
            return cls.names[-2].lower()
        except IndexError:
            pass

    @classmethod
    def get_table_name(cls):
        if cls._table:
            return cls._get_table_name(cls._table)
        return cls.names[-1].lower()

    @classproperty
    def database(cls):
        return cls.get_database()

    @classproperty
    def table(cls):
        return cls.get_table()

    @classproperty
    def names(cls):
        return names_regex.findall(cls.__name__)

    @classproperty
    def database_name(cls):
        return cls.get_database_name()

    @classproperty
    def table_name(cls):
        return cls.get_table_name()


__all__ = ["View", "registry", "Thingy", "DatabaseThingy"]
