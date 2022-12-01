from collections import OrderedDict

from pytest import fixture, raises

from thingy import DatabaseThingy, NamesMixin, Thingy, View, classproperty, registry


def test_classproperty():
    class Test:
        _foo = "bar"

        @classproperty
        def foo(cls):
            return cls._foo

    assert Test.foo == "bar"


def test_classproperty_vs_attribute_conflicts():
    class Foo(Thingy):
        _foo = "bar"

        @classproperty
        def foo(cls):
            return cls._foo

    assert Foo.foo == "bar"

    foo = Foo()
    assert foo.foo is None

    foo._silent = False
    with raises(AttributeError):
        foo.foo

    foo = Foo(foo="baz")
    assert foo._foo == "bar"
    assert foo.foo == "baz"


def test_property_vs_attribute_conflicts():
    class Foo(Thingy):
        _foo = "bar"

        @property
        def foo(self):
            return self._foo

    foo = Foo()
    assert foo.foo == "bar"

    with raises(AttributeError) as excinfo:
        foo = Foo(foo="baz")
    assert str(excinfo.value) in ("can't set attribute", "can't set attribute 'foo'")

    foo = Foo({"foo": "baz"})
    assert foo._foo == "bar"
    assert foo.foo == "bar"
    assert foo.__dict__["foo"] == "baz"


def test_view_return_type():
    view = View()
    assert view(None) == {}
    view = View(ordered=True)
    assert view(None) == OrderedDict()


@fixture
def TestThingy():
    class TestThingy(Thingy):
        @property
        def foobaz(self):
            return self.foo + self.baz

    return TestThingy


@fixture
def TestDatabaseThingy():
    class TestDatabaseThingy(DatabaseThingy):
        pass

    return TestDatabaseThingy


def test_init_with_dict():
    thingy = Thingy({"foo": "bar", "baz": "qux"})
    assert thingy.foo == "bar"
    assert thingy.baz == "qux"


def test_init_with_args():
    thingy = Thingy(foo="bar", baz="qux")
    assert thingy.foo == "bar"
    assert thingy.baz == "qux"


def test_init_mixed():
    thingy = Thingy({"foo": "bar"}, baz="qux")
    assert thingy.foo == "bar"
    assert thingy.baz == "qux"


def test_eq():
    thingy = Thingy(foo="bar")
    other_thingy = Thingy(foo="bar")
    assert thingy == other_thingy
    assert thingy != {"foo": "bar"}


def test_repr():
    thingy = eval(repr(Thingy(bar="baz")))
    assert isinstance(thingy, Thingy)
    assert thingy.bar == "baz"


def test_update_with_dict():
    thingy = Thingy(foo="bar", baz="qux")
    thingy.update({"foo": "BAR"})
    assert thingy.foo == "BAR"
    assert thingy.baz == "qux"


def test_update_with_args():
    thingy = Thingy({"foo": "bar", "baz": "qux"})
    thingy.update(foo="BAR", baz="QUX")
    assert thingy.foo == "BAR"
    assert thingy.baz == "QUX"


def test_default_view():
    thingy = Thingy(foo="bar", baz="qux")
    assert thingy.view() == {"foo": "bar", "baz": "qux"}


def test_missing_view():
    thingy = Thingy()
    with raises(KeyError):
        thingy.view("nop")


def test_property_exceptions():
    class ScreamingThingy(Thingy):
        @property
        def foo(self):
            raise AttributeError("Foo!")

    thingy = ScreamingThingy()
    with raises(AttributeError) as excinfo:
        thingy.foo
    assert str(excinfo.value) == "Foo!"

    class ScreamingThingyChild(ScreamingThingy):
        pass

    thingy = ScreamingThingyChild()
    with raises(AttributeError) as excinfo:
        thingy.foo
    assert str(excinfo.value) == "Foo!"


def test_silence():
    thingy = Thingy()
    assert thingy.foo is None

    class ScreamingThingy(Thingy):
        _silent = False

    thingy = ScreamingThingy()
    with raises(AttributeError):
        thingy.foo


def test_add_view(TestThingy):
    TestThingy.add_view("test")
    thingy = TestThingy(foo="bar", baz="qux")
    assert thingy.view() == {"foo": "bar", "baz": "qux"}
    assert thingy.view("test") == {}


def test_add_view_override(TestThingy):
    TestThingy.add_view("defaults", defaults=False)
    thingy = TestThingy(foo="bar", baz="qux")
    assert not thingy.view()


def test_add_view_defaults(TestThingy):
    TestThingy.add_view("test", defaults=True)
    thingy = TestThingy(foo="bar", baz="qux")
    assert thingy.view("test") == {"foo": "bar", "baz": "qux"}


def test_add_view_include(TestThingy):
    TestThingy.add_view("test", include="foo")
    thingy = TestThingy(foo="bar", baz="qux")
    assert thingy.view("test") == {"foo": "bar"}


def test_add_view_include_list(TestThingy):
    TestThingy.add_view("test", include=["foo", "baz"])
    thingy = TestThingy(foo="bar", baz="qux")
    assert thingy.view("test") == {"foo": "bar", "baz": "qux"}


def test_add_view_exclude(TestThingy):
    TestThingy.add_view("test", defaults=True, exclude="foo")
    thingy = TestThingy(foo="bar", baz="qux")
    assert thingy.view("test") == {"baz": "qux"}


def test_add_view_exclude_list(TestThingy):
    TestThingy.add_view("test", defaults=True, exclude=["foo", "baz"])
    thingy = TestThingy(foo="bar", baz="qux")
    assert thingy.view("test") == {}


def test_tuple_aliases(TestThingy):
    TestThingy.add_view("test", include=[("foo", "FOO")])
    thingy = TestThingy(foo="bar", baz="qux")
    assert thingy.view("test") == {"FOO": "bar"}


def test_names():
    class FooBar(NamesMixin):
        pass

    assert FooBar.names == ["foo", "bar"]

    class FooBar(NamesMixin, Thingy):
        pass

    assert FooBar.names == ["foo", "bar"]


def test_names_with_abbreviation():
    class FOOBarQux(NamesMixin):
        pass

    assert FOOBarQux.names == ["foo", "bar", "qux"]

    class BarFOOQux(NamesMixin):
        pass

    assert BarFOOQux.names == ["bar", "foo", "qux"]

    class BarQuxFOO(NamesMixin):
        pass

    assert BarQuxFOO.names == ["bar", "qux", "foo"]


def test_database_names():
    assert DatabaseThingy.names == ["database", "thingy"]


def test_database_name_from_class():
    class DatabaseTable(DatabaseThingy):
        pass

    assert DatabaseTable.database_name == "database"


def test_database_name_from_database():
    class DatabaseTable(DatabaseThingy):
        _database = True

    assert DatabaseTable.database_name is None


def test_database_name_from_attribute():
    class DatabaseTable(DatabaseThingy):
        _database_name = "foo"

    assert DatabaseTable.database_name == "foo"


def test_database_name_priority():
    class DatabaseTable(DatabaseThingy):
        _database = True
        _database_name = "foo"

    assert DatabaseTable.database_name is None


def test_table_name_from_class():
    class DatabaseTable(DatabaseThingy):
        pass

    assert DatabaseTable.table_name == "table"


def test_table_name_from_class_with_database():
    class DatabaseTable(DatabaseThingy):
        _database = True

    assert DatabaseTable.table_name == "database_table"


def test_table_name_from_class_with_database_name():
    class DatabaseTable(DatabaseThingy):
        _database_name = "foo"

    assert DatabaseTable.table_name == "database_table"


def test_table_name_from_table():
    class DatabaseTable(DatabaseThingy):
        _table = True

    assert DatabaseTable.table_name is None


def test_table_name_from_attribute():
    class DatabaseTable(DatabaseThingy):
        _table_name = "foo"

    assert DatabaseTable.table_name == "foo"


def test_table_name_priority():
    class DatabaseTable(DatabaseThingy):
        _table = True
        _table_name = "foo"

    assert DatabaseTable.table_name is None


def test_undefined_database():
    class Table(DatabaseThingy):
        pass

    assert Table.database_name is None

    with raises(AttributeError):
        Table.database

    class Table(DatabaseThingy):
        _table = True

    with raises(AttributeError):
        Table.database

    class DatabaseTable(DatabaseThingy):
        pass

    with raises(AttributeError):
        DatabaseTable.database


def test_undefined_table():
    class Table(DatabaseThingy):
        pass

    with raises(AttributeError):
        Table.table

    class Table(DatabaseThingy):
        _database = True

    with raises(AttributeError):
        Table.table


def test_database():
    class DatabaseTable(DatabaseThingy):
        _database = True

    assert DatabaseTable.database is True

    class DatabaseTable(DatabaseThingy):
        _table = True

        @classmethod
        def _get_database(cls, table, name):
            return table

    assert DatabaseTable.database is True


def test_table():
    class DatabaseTable(DatabaseThingy):
        _table = True

    assert DatabaseTable.table is True

    class DatabaseTable(DatabaseThingy):
        _database = True

        @classmethod
        def _get_table(cls, database, name):
            return database

    assert DatabaseTable.table is True


def test_registry():
    del registry[:]

    class Foo(Thingy):
        pass

    assert registry == [Foo]

    class Bar(Thingy):
        pass

    assert registry == [Foo, Bar]
