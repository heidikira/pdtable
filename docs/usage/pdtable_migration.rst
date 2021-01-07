Migration from startables-python to pdtable
===========================================

If you have previously use startables-python, here are some tips in migrating
your code to use the newer pdtable package.

Writing example
---------------

Previously,

.. code:: python

        from startables.startables import Table, ColumnMetadata, Unit
        import pandas as pd

        df = pd.DataFrame({"c": [1, 2, 3], "d": [4, 5, 6]})
        my_startable = Table(df, name="example_startable", destinations=['example'],
                             col_specs={'c': ColumnMetadata(Unit('km')), 'd': ColumnMetadata(Unit('kg'))})


Reading example
---------------

