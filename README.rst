======
Thingy
======

Dictionary as an object, that can have different dictionary views


Install
=======

.. code-block:: sh

   $ pip install thingy


Examples
========

Dictionary as an object...
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


...that can have different views!
---------------------------------

.. code-block:: python

   >>> MyThingy.define_view(name="fooz", include=["foo", "foobaz"])
   >>> MyThingy.define_view(name="no_foo", defaults=True, exclude="foo")

   >>> thingy = MyThingy({"foo": "bar", "baz": "qux"})
   >>> thingy.view("fooz")
   {"foo": "bar", "foobaz": "barqux"}
   >>> thingy.view("no_foo")
   {"baz": "qux"}
