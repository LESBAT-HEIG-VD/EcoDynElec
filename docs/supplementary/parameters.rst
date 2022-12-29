Managing the parameters
=======================

The `dynamical` software allows high-level customization via some parameters. This document gives an exhaustive description of all the options and how to modify them.

From Python interface
*********************
Parameters can be set directly in Python using the `Parameter` class of `dynamical`. Here is how the `Parameter` class is organized and what it contains. For the meaning of each parameter, see the section `Meaning and role of each parameter <https://dynamical.readthedocs.io/en/latest/supplementary/parameters.html>`_.


From the spreadsheet
*********************
Alternatively, parameters can be set via a spreadsheet. An example spreadsheet can be downloaded fro the `git repository <https://gitlab.com/fledee/ecodyn/-/raw/main/examples/Spreadsheet_example.xlsx?inline=false>`_. Here is what it looks like. For the meaning of each parameter, see the section `Meaning and role of each parameter <https://dynamical.readthedocs.io/en/latest/supplementary/parameters.html>`_.


Meanign and role of each parameter
**********************************
This section describes the meaning and role of each parameter. The `documentation <https://dynamical.readthedocs.io/en/latest/modules/parameter.html>`_ about the `Parameter` class also provides useful descriptions.

.. list-table:: Filepath Parameters (Filepath tab)
    :widths: 15 15 70
    :header-rows: 1
    
    * - Spreadsheet
      - Python
      - Description
    * - generation directory
      - `Parameter.path.generation`
      - Directory containing the generation data. This is also the directory where to save the downloaded files.
    * - exchange directory
      - `Parameter.path.exchanges`
      - Directory containing the exchanges data. This is also the directory where to save the downloaded files.
    * - saving directory
      - `Parameter.path.savedir`
      - Directory where to save computation results. If field is empty or None (default), the results are only returned in Python.
    * - FU vector
      - `Parameter.path.fu_vector`
      - The location of impact per unit type in a single table format. Default file from the support files is used if None is given.
    * - mapping file
      - `Parameter.path.mapping`
      - The location of a mapping file. A blank example is available for download on the `git repository <https://gitlab.com/fledee/ecodyn/-/raw/main/support_files/mapping_template.xlsx?inline=false>`_. Default FU vector from the support files is used if None is given.
    * - gap file
      - `Parameter.path.gap`
      - The location of a file containing estimates of the composition of the Swiss residual. Default file fron the support files is used if None is given.
    * - file swissGrid
      - `Parameter.path.swissGrid`
      - The location of a file containing information from SwissGrid. Default file fron the support files is used if None is given.
    * - file grid losses
      - `Parameter.path.networkLosses`
      - The location of a file containing estimates of power grid losses. Default file fron the support files is used if None is given.