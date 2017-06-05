======
Thingy
======

.. image:: https://img.shields.io/pypi/v/thingy.svg
   :target: https://pypi.python.org/pypi/Thingy
.. image:: https://img.shields.io/github/license/numberly/thingy.svg
   :target: https://github.com/numberly/thingy/blob/master/LICENSE
.. image:: https://img.shields.io/travis/numberly/thingy.svg
   :target: https://travis-ci.org/numberly/thingy
.. image:: https://img.shields.io/coveralls/numberly/thingy.svg
   :target: https://coveralls.io/github/numberly/thingy

|

Dictionaries as objects, that can have different dictionary views!


Install
=======

.. code-block:: sh

   $ pip install thingy


Examples
========

Dictionaries as objects...
--------------------------

.. code-block:: python

   >>> class MyThingy(Thingy)
   ...     @property
   ...     def foobaz(self):
   ...         return self.foo + self.baz

   >>> thingy = MyThingy({"foo": "bar", "baz": "qux"})
   >>> thingy.foo
   "bar"
   >>> thingy.foobaz
   "barqux"

   >>> thingy.foo = "BARRRR"
   >>> thingy.view()
   {"foo": "BARRRR", "baz": "qux"}


...that can have different dictionary views!
--------------------------------------------

.. code-block:: python

   >>> MyThingy.add_view(name="fooz", include=["foo", "foobaz"])
   >>> MyThingy.add_view(name="no_foo", defaults=True, exclude="foo")

   >>> thingy = MyThingy({"foo": "bar", "baz": "qux"})
   >>> thingy.view("fooz")
   {"foo": "bar", "foobaz": "barqux"}
   >>> thingy.view("no_foo")
   {"baz": "qux"}


Why Thingy?
===========

Because it's much more enjoyable to write ``foo.bar`` than ``foo["bar"]``.

Thingy is mainly meant to be used inside other libraries to provide abstractions
over dictionaries, which can be useful for writing ORMs or similar utilities.

Thingy's views system is also particularly useful as-is when you intensively
manipulate dictionaries and often restrict those dictionaries to a few redundant
items.


Tests
=====

To run Thingy tests:

* install developers requirements with ``pip install -r requirements.txt``;
* run ``pytest``.


License
=======

MIT
