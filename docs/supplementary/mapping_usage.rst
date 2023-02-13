Mapping Spreadsheet
===================

This page explains how to use the mapping spreadsheet in detail.


Introduction
------------
The mapping spreadsheet contains a methodology to address the discrepency between the source of electricity generation data and the LCA database from which impact information are extracted. A `blank template <https://gitlab.com/fledee/ecodyn/-/raw/main/support_files/mapping_template.xlsx?inline=false>`_ suited for linking the ENTSO-E data with impacts information from an LCA database can be downloaded from the Git. This tempate already contains equations for all required fields, for all countries represented in the ENTSO-E database.

A condensed version containing the impact values for every ENTSO-E generation type is used per default, but it only contains values for a limited set of countries. This condensed matrix is named "*FU-vector*" and has been built with the LCA database of Ecoinvent.

The software ``dynamical`` can use both a mapping spreadsheet and a FU-vector as input. Per default, it uses the `FU-vector available <https://gitlab.com/fledee/ecodyn/-/raw/main/support_files/Functional_Unit_Vector.csv?inline=false>`_ in the software files for the four following impact indexes: Climate change, Human carcynogenic toxicity, Fine particle formation matter and Land use.

Additional impact indexes can be added or used by the user. The author declines all responsibility of biased results obtained due to incorrect usage of the impact data by the user.




Usage
-----
*Overview of how to use both the FU vector and the Mapping in the overall pipeline*

Once filled, the mapping file can be provided to ``dynamical`` via the parameter object or using the parametrization via spreadsheet (c.f. `page on the topic <https://dynamical.readthedocs.io/en/latest/supplementary/parameters.html>`_)

.. code-block:: python
    :caption: Launch ``dynamical`` using the mapping spreadsheet

    ### Show the addition of the mapping file and FU vector + default to the parameters, then execution.
    from dynamical.parameter import Parameter
    from dynamical.pipelines import execute

    ### Give a path to the spredhseet in the parameters setting
    configuration = Parameter() # Initialization
    # Set all required paramters... See dedicated page.
    configuration.path.mapping = "/path/to/mapping.xlsx" # Parameter specific to mapping

    ### Execute the code
    execute(config=configuration)


The example above will work the same if the user indicates the ``/path/to/mapping.xlsx`` or if indicates ``/path/to/FU_vector.csv``. The example shows a configuration in Python, but a configuration via the spreadsheet would work the same, if the correct path to a mapping file is given in the tab "*Path*" of the configuration spreadsheet.

Per default, ``dynamical`` will use a FU-vector in the software files. This default contains impact values for 4 indexes (Climate Change, Human carcinogenic toxicity, Fine particle matter formation and Land use) for 6 countries (AT, CH, CZ, DE, FR, IT). These values are obtained using the mapping template with impacts from the `Ecoinvent <https://ecoinvent.org/>`_ database.


File structure
--------------

The mapping template contains 3 types of sheets: country sheets, one residual sheet and one "*average*" sheet.

Country sheet
~~~~~~~~~~~~~

The structure of the mapping file is highlighted in Figure 1. It can be divided into 5 sets of columns: the generation type in ENTSO-E, the corresponding technology(ies) in the LCA database, shares of each technology, the impacts associated to each technology, and the grouped impacts per type of generation type.

.. figure:: ../images/missing.png
    :alt: Detailed structure of the Mapping file
    
    *Figure 1: Detailed structure of the (template) mapping file*

The first column of the spreadsheet is for the *generation type* as found in the ENTSO-E database, or any other database used for the electricity data.

Average sheet
~~~~~~~~~~~~~
The average sheet is of utmost importance, as it contains the values that will be used for the impact of electricity originating from countries not included in the computation but neighbouring the involved countries. The sheet only requires one impact value per impact category.


Residual sheet
~~~~~~~~~~~~~~
The residual sheet is structured in the exact same way as a country sheet, except for the pre-suggested technologies. In the *Residual* sheet, the two included technologies are the *Residual_Hydro* and the *Residual_Other*, in accordance with the methodology described in the `associated publication <https://www.researchgate.net/profile/Sebastien-Lasvaux/publication/349139291_Dynamic_Life_Cycle_Assessment_of_the_building_electricity_demand/links/60225b5445851589399073e0/Dynamic-Life-Cycle-Assessment-of-the-building-electricity-demand.pdf>`_ and specified in the `dedicated page <https://dynamical.readthedocs.io/en/latest/structure/local_residual.html>`_ of the documentation.

This sheet has been designed so the user can build the residual using existing technologies and its own estimated shares.




Requirements
------------
*Explain what specifically are the key elements importants to extract the information and the elements that can be modified*

The mapping template has multiple degrees of freedom, and some key elements that must not be modified in order for the module ``dynamical.preprocessing.load_impacts`` to work correctly. This module is responsible for reading the mapping file and selecting required information. Details about the structure of this module are available in the `designated documentation <https://dynamical.readthedocs.io/en/latest/structure/load_impacts.html>`_.

Key elements to leave unchanged
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
On **country sheets**, the module tries to extract information from the last block of columns, named "*Environmental impacts of 1 kWh of ENTSO-E categories*". The algorithm will extract *all columns standing to the right of the last column whose value on the row 1 contains "impact"*. So the user should avoid modifying the first row. Note that when Python reads a spreadsheet, all cells are unmerged and the content of merged cells is attributed to the upper leftmost cell of the aggregate. This also means that the number of impact indexes is **at least one**, but is **not restricted to four**, thus impact columns can be deleted or added at will. Just make sure to extend the formulas.

Still on the **country sheets**, the leftmost column is used for finding the generation types. *All rows of the extracted table that have at least one missing value are ignored*. This gives the flexibility to add **as may new rows as desired** to add new technologies corresponding to a generation category, and this allows to add new generation categories as well if required. Similarly, unused raws can be deleted with no major risks, just make sure to adapt the formulas in the rightmost block of columns. This also means that every generation type that has no corresponding technology from the LCA database will be ignored. Generation categories with at least one technology will be considers, **but make sure that the first row of the generation category is filled**.

The **residual sheet** works exactly the same way as the country sheets.

The **ENTSOE avg sheet** only expects values entered manually. Its format is also more sensitive: in the current version, only the columns 2 to 7 (i.e. C to G) are loaded, and only from the second row. The only row of data that is extracted is where the column C contains "*ENTSOE average mix*". These values are mandatory, as always used in the ``dynamical`` process.

Example of possible modifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The last paragraph already mentions most of the possible changes. Beside filling the sheet with adapted values, modifying the headings (impact category names, some specification and the unit) and changing the name of generation categories (not recommanded) in the Residual and in the coutry sheets, it is also possible to modify *all headings but those on the 1st row*, as well as personalizing the calculation methodology (not recomended), adding new generation categories, adding or deleteing columns of impact categories, adding or deleting rows of technologies. It is also possible to add spreadsheets if required.



Link Mapping-FU vector
----------------------
*Explain the link between both.* The `FU-vector <https://dynamical.readthedocs.io/en/latest/supplementary/functional_unit.html>`_ (FU stands for Functional Unit) is a matrix of values concatenating the rightmost set of columns in the country and residual tabs of a mapping spreadsheet. The first row of the FU-vector is always the (mandatory) values of the **ENTSOE avg sheet**. The FU vector only contains values, i.e. the content extracted from the mapping spreadhseet **after** filtering of missing information.

*Specify that the FU vector comes with no guarantees, but only our values per default*. The user can rely on the default values provided with the software. The author can only guarantee the adequacy of these default values and can not be held responsible for any erroneous result obtained caused by incorrect or unjustified replacement or modification of the impact values in a mapping spreadsheet or FU vector. 

*Explain that a FU vector is computed and added to the saving files (under another name)*. An FU vector can be generated using the function ``dynamical.preprocessing.load_impacts.extract_mapping`` provided with the path of a mapping file. It can also be found in the generated files created by the ``dynamical.pipelines.execute`` function under the name "*Impact_Vector.csv*" if the saving of result files is requested.
