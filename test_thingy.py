from collections import OrderedDict

from pytest import fixture, raises
from thingy import DatabaseThingy, Thingy, View, classproperty, registry


def test_classproperty():
    class Test:
        _foo = "bar"

        @classproperty
        def foo(cls):
            return cls._foo

        @foo.setter
        def set_foo(cls, value):
            cls._foo = value

    assert Test.foo == "bar"
    Test.foo = "baz"
    assert Test.foo == "baz"


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


def test_database_names():
    assert DatabaseThingy.names == ["database", "thingy"]


def test_database_name():
    class DatabaseTable(DatabaseThingy):
        pass

    assert DatabaseTable.database_name == "database"

    class Table(DatabaseThingy):
        _database = True

    assert Table.database_name is None


def test_table_names():
    class Table(DatabaseThingy):
        pass

    assert Table.table_name == "table"

    class Table(DatabaseThingy):
        _table = True

    assert Table.table_name is None


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
        _table = True

        @classmethod
        def _get_database(cls, table, name):
            return table

    assert DatabaseTable.database is True


def test_table():
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
