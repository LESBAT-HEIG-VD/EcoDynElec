LCA data
=============

This tutorial goes through the possibilities to provide LCA data to EcoDynElec or to retrieve it from the software. Providing LCA data is done using the standard configuration procedures, either `using python <https://ecodynelec.readthedocs.io/en/latest/examples/with_python.html>`__ or `using a spreadsheet <https://ecodynelec.readthedocs.io/en/latest/examples/with_spreadsheet.html>`__, relying on the configuration fields ``ui_vector`` and ``mapping`` for which the path to files must be specified.





Mapping Spreadsheet
---------------------
Once filled, the `mapping spreadsheet <https://github.com/LESBAT-HEIG-VD/EcoDynElec/raw/main/support_files/mapping_template.xlsx>`__ can be provided to ``ecodynelec`` via the standard configuration procedures (c.f. page on `configuration <https://ecodynelec.readthedocs.io/en/latest/data_input/parameters.html>`__). The examples below show a `configuration in Python <https://ecodynelec.readthedocs.io/en/latest/examples/with_python.html>`__, but a `configuration via the spreadsheet <https://ecodynelec.readthedocs.io/en/latest/examples/with_spreadsheet.html>`__ would work as well, if the correct path to a mapping file is given in the tab "*Path*" of the configuration spreadsheet.

.. code-block:: python
    :caption: Set ``ecodynelec`` configuration for using the mapping spreadsheet

    from ecodynelec.parameter import Parameter

    ### Give a path to the spreadsheet in the parameters setting
    configuration = Parameter() # Initialization
    # Set all required parameters... See dedicated page.
    configuration.path.mapping = "/path/to/mapping.xlsx" # Parameter specific to mapping
    
Per default, the field is empty (i.e. ``None`` in Python, and blank in the configuration spreadsheet). If a file is passed by the user, this file will be used. If the field is left per default, a Unit Impact Vector will be used instead.





Unit Impact Vector
--------------------

The `example above <https://ecodynelec.readthedocs.io/en/latest/examples/lca_data.html#mapping-spreadsheet>`__ is adapted to a mapping spreadsheet. However a Unit Impact (UI) Vector can be used instead, as demonstrated below.

.. code-block:: python
    :caption: Set ``ecodynelec`` configuration for a UI vector file

    from ecodynelec.parameter import Parameter

    ### Give a path to the spredhseet in the parameters setting
    configuration = Parameter() # Initialization
    # Set all required paramters... See dedicated page.
    configuration.path.mapping = None # Make sure the field for Mapping Spreadsheet is empty
    configuration.path.ui_vector= "/path/to/impact_vector.csv" # Parameter specific to UI vector



If both a ``mapping`` and a ``ui_vector`` are specified, the ``mapping`` is given the priority. If neither ``mapping`` nor ``ui_vector`` are specified, a default UI vector from the software files will be used.







Obtain the UI Vector from Mapping
----------------------------------
When a mapping spreadsheet is provided to ``ecodynelec``, the relevant information is extracted and gathered according to the specific `format of a UI vector <https://ecodynelec.readthedocs.io/en/latest/data_input/lca_data.html#unit-impact-vector>`__. If a saving directory is also specified, this reduced UI vector used during the computation of impacts is saved in a file named "*Unit_Impact_Vector.csv*".

Creating a specific UI vector file based on a mapping spreadsheet is also possible using EcoDynElec without triggering the whole calculation process:

.. code-block:: python
    :caption: Extracting LCA data from a Mapping spreadsheet

    from ecodynelec.preprocessing.load_impacts import extract_mapping

    ### Give a path to the spredhseet 
    path_spreadsheet = "/path/to/mapping/spreadsheet.xlsx"
    ### Specify the list of countries to extract
    countries = ['AT','CH','DE','DK','PL']
    
    ### Extract the UI vector
    ui_vector = extract_mapping(ctry=countries, mapping_path=path_spreadsheet)
    
    ### Saving into a csv file
    ui_vector.to_csv("/path/to/where-to-save/file.csv")