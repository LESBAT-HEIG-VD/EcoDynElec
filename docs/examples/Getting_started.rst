Getting started
===============

``Dynamical`` must first be downloaded from its `Git
repository <https://gitlab.com/fledee/ecodyn>`__. After its download,
the package can be used and installed in different ways, as explained
below.

Conventional install
--------------------

``Dynamical`` has not been added to the packages available via ``pip``
or ``conda``. Thus the install requires to trigger the ``setup.py``
file. More on this in the `official Python
documentation <https://docs.python.org/3/install/#distutils-based-source-distributions>`__.
In an Anaconda prompt, command prompt or any other terminal where
``python`` can be executed, run the following:

>> cd /path/to/dynamical/package/
>> python setup.py install

Now ``dynamical`` can be imported and used as any other python package.

If experiencing issues using ``dynamical`` in notebooks, the
“*guaranteed install*” below may be a good and cheap alternative.

Guaranteed install
------------------

To make sure the package can be used in every python environment, the
absolute path to the ``Dynamical`` package must be temporarily added to
the python records. This method simply tells python where to find the
source information. Actually, “installing python packages” just means
“telling python where to find packages on a machine to execute them”.

.. code:: ipython3

    import sys, os # Required python libraries
    sys.path.insert(0, os.path.abspath("path/to/dynamical/package")) # Adds the path to the package in the python records, but only in this script

Now ``dynamical`` can be imported and used as any other python package,
only in this script.

.. code:: ipython3

    import dynamical
