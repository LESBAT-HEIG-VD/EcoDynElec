Getting started
===============

``ecodynelec`` must first be downloaded from its `Git
repository <https://gitlab.com/fledee/ecodynelec>`__, by using a prompt
(example below) or any other method:

>> cd /path/to/where/to/download/ecodynelec
>> git clone https://gitlab.com/fledee/ecodynelec.git

After cloning the repository, the package can be used and installed in
different ways, as explained below.

Conventional install
--------------------

Typical python installation softwares such as ``pip`` or ``conda`` can
be used to install ``ecodynelec`` from your local copy of the git. To do
so, use a prompt or a terminal and move inside the ``ecodynelec/``
directory. From there, use ``pip`` (example) or ``conda`` to install.
The following attempt will trigger the installation by executing the
``setup.py`` file.

>> cd /path-to-ecodynelec-copy/ecodynelec/
>> python -m pip install ecodynelec

Now ``ecodynelec`` can be imported and used as any other python package.
If you wish to contribute in developing ``elecodyn``, using the
``pip install -e`` flag when installing may be beneficial (c.f. `pip
documentation <https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs>`__)

An alternative is to use python to directly trigger the ``setup.py``
file within the ``ecodynelec/`` directory. More on this in the `official
Python
documentation <https://docs.python.org/3/install/#distutils-based-source-distributions>`__.

>> cd /path-to-ecodynelec-copy/ecodynelec/
>> python setup.py install

If experiencing issues using ``ecodynelec`` in notebooks, the
“*guaranteed install*” below may be a good and cheap alternative.

Guaranteed install
------------------

To make sure the package can be used in every python environment, the
absolute path to the ``ecodynelec`` package must be temporarily added to
the python records. This method simply tells python where to find the
source information. Actually, “installing python packages” just means
“telling python where to find packages on a machine to execute them”.

.. code:: ipython3

    import sys, os # Required python libraries
    sys.path.insert(0, os.path.abspath("path/to/ecodynelec/package")) # Adds the path to the package in the python records, but only in this script

Now ``ecodynelec`` can be imported and used as any other python package,
but only in the script where the previous lines are present.

.. code:: ipython3

    import ecodynelec
