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
    :caption: This is the caption

    ### Show the addition of the mapping file and FU vector + default to the parameters, then execution.
    import dynamical





File structure
--------------

The mapping template contains 3 types of sheets: country sheets, one residual sheet and one "*average*" sheet.

Country sheet
~~~~~~~~~~~~~

The structure of the mapping file is highlighted in Figure 1. It can be divided into 5 sets of columns: the generation type in ENTSO-E, the corresponding technology(ies) in the LCA database, shares of each technology, the impacts associated to each technology, and the grouped impacts per type of generation type.

.. figure: ../images/missing.png
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




Link Mapping-FU vector
----------------------
*Explain the link between both*
*Specify that the FU vector comes with no guarantees, but only our values per default*
*Explain that a FU vector is computed and added to the saving files (under another name)*






