Downloading data with ``dynamical``
===================================

``dynamical`` integrates the possibility to download the required data
from ENTSO-E servers. Though, *using the software may be slow*, thus the
use of a third-party SFTP software is detailed in the `Supplementary
Information <https://dynamical.readthedocs.io/en/latest/supplementary/download.html#>`__.

This page details how to use ``dynamical`` to download the required data
from ENTSO-E databases. It covers: + How to configure the software to
request the downloading + How to use use the ``downloading`` module of
``dynamical`` + How to use the main pipeline, including the download of
data.

1. Configuration
----------------

The configuration can be made in 2 ways, as explained in `Supplementary
Information <https://dynamical.readthedocs.io/en/latest/supplementary/parameters.html#>`__.
One can set it up via the ``Parameter`` module or using a spreadsheet.

1.1 Using a spreadsheet
~~~~~~~~~~~~~~~~~~~~~~~

In a spreadsheet, a tab named “*Server*” must be used, containing the
table shown in the figure below.



Each field must be written as presented, in low case. The fields are: +
**host**: the address of the sftp server. Per default, we use
“*sftp-transparency.entsoe.eu*”. + **port**: the port to connect to the
server. Per default, the port is *22*. + **username**: your username, as
created for free on the `ENTSO-E
website <https://transparency.entsoe.eu/>`__. + **password**: your
password, as created for free on the `ENTSO-E
website <https://transparency.entsoe.eu/>`__. For security reasons, we
do recommend to let the field blank, which will let the ``downloading``
package ask for the password in a more secured manner. + **use server**:
**TRUE** if you want to download the data. Blank or **FALSE** will not
download the data (default). + **remove unused**: **TRUE** if you want
the target directories (where to download) to be emptied before
downloading. Blank or **FALSE** to ignore other files in the target
directory (default).

The files will be downloaded and saved in the directories indicated at
the fields **path generation** and **path exchanges** of the tab
*Filepath* of the spreadsheet (Figure below). Also make sure you set the
date accordingly (tab *Parameter*), to allow the selection of files to
download. More information on the *Parameter* tab in the `Supplementary
Information <https://dynamical.readthedocs.io/en/latest/supplementary/parameters.html#>`__.

1.2 Using the ``Parameter`` module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure parameters directly in Python, the ``parameter`` module can
be used.

.. code:: ipython3

    from dynamical.parameter import Parameter # Import the Parameter class

Strictly regarding the requirements for downloading, we require + to set
the dates + to indicate the directory where to download + to configure
the server connection

.. code:: ipython3

    ### Initialize the configuration
    config = Parameter()

.. code:: ipython3

    ### Set the dates (to select files to download)
    config.start = '2017-02-01 05:00'
    config.end = '2017-02-01 13:00'

.. code:: ipython3

    ### Indicate where to save the generation data
    config.path.generation = "./test_data/downloads/generations/"
    
    ### Indicate where to save the exchange data
    config.path.exchanges = "./test_data/downloads/exchanges/"

.. code:: ipython3

    ### Configure the server connection
    config.server.useServer = True # Specifically ask to download data
    config.server.host = "sftp-transparency.entsoe.eu" # This server is already set per default after initialization
    config.server.port = 22 # This port is already set per default after initialization
    config.server.username = "myname@myemail.com" # Username for connection on the ENTSO-E webpage

Note that the above example does not set a password. This will then be
asked later. Also note that values for ``config.server.host`` and
``config.server.port`` are set per default during the initialization, it
is not necessary to specify them again.

2. Download using the ``downloading`` module
--------------------------------------------

Once the configuration is properly done, the following commands allow to
download the data (and only do the download).

.. code:: ipython3

    ### Import the function to download
    from dynamical.preprocessing.downloading import download

After importing the ``download`` function, the following command will
grab the required data on the server. The following uses the
configuration done with Python.

.. code:: ipython3

    download(config=config, is_verbose=True) # is_verbose does display some text while downloading

An alternative is to directly pass the spreadsheet path as a parameter.
The following command does the exact same as the previous one, if the
spreadsheet was written correctly.

.. code:: ipython3

    download(config="./Spreadsheet_download.xlsx", is_verbose=True)

3. Include the download in the overall pipeline
-----------------------------------------------

It is also possible to include the download within the overall
computation pipeline. To do so, make sure the configuration is set
correctly as explained in section 1, either in a spreadsheet or in
Python. Then simply execute the main function of ``dynamical`` passing
this configuration as parameter.

.. code:: ipython3

    ### Import the main execution function
    from dynamical.pipelines import execute

The following cell executes the whole pipeline, including download, from
a configuration set up with Python.

.. code:: ipython3

    results = execute(config=config, is_verbose=True)

The following cell executes the whole pipeline, including download, from
a configuration set up in a spreadsheet.

.. code:: ipython3

    results = execute(config="./Spreadsheet_download.xlsx", is_verbose=True)
