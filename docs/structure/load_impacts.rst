Load LCA data
================

LCA data must be loaded, which is harder than it seems. Most workflows are based on nice visual spreadsheets to easily be edited, which is literally a nightmare to then automatically retrieve the information for further automated tasks. A change of one letter in a non-relevant cell, a new row or a new column, and the algorithm is completely lost. To cope with these limitations as good as possible, a specific module is dedicated to simply load the impact data.

As detailed in different places in the documentation, the impacts per production unit type is used by EcoDynElec as a matrix called *Unit Impact Vector*. Such a matrix can be directly provided as a file, or obtained by extracting the information from a mapping file. The Unit Impact Vector is simply an already shaped matrix of data, ready-to-use.

The mapping file is an xlsx spreadsheet. A blank template may be downloaded on the `git repository <https://github.com/LESBAT-HEIG-VD/EcoDynElec/raw/main/support_files/mapping_template.xlsx>`_. The document must be provided blank as it relies on data which require information provided by proprietary sources such as the `Ecoinvent database <https://ecoinvent.org/>`_. Details about this mapping file and its structure is provided in a `dedicated page <https://ecodynelec.readthedocs.io/en/latest/data_input/lca_data.html>`_ of the documentation.

.. figure:: images/load_impacts.png
    :alt: Load impacts
    
    *Structure of impacts loading in ``ecodynelec``*
