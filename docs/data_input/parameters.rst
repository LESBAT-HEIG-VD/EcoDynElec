Configuration
=============

The EcoDynElec software allows high-level customization via some configuration procedures. This document gives an exhaustive description of all the options, classified under the **three standard sections of the configuration**. Tutorials in the *How to use* section show how to actually set the configuration:
    * `solely using python <https://ecodynelec.readthedocs.io/en/latest/examples/with_python.html#configuration>`__
    * `using a spreadsheet <https://ecodynelec.readthedocs.io/en/latest/examples/with_spreadsheet.html#configuration>`__
    * for details about the `downloading procedure <https://ecodynelec.readthedocs.io/en/latest/examples/downloading.html#download-via-ecodynelec>`__
    * for details about the `lca data <https://ecodynelec.readthedocs.io/en/latest/examples/lca_data.html>`__






Main Parameters
---------------
Main settings are in the "Parameters" tab of the spreadsheet, or attributes of the object ``Parameter``.

* **countries** (spreadsheet) / ``Parameter.ctry`` (python): List of countries to involve in the computation. Should be a list in Python, and one country per cell on the dedicated row of the spreadsheet. Countries must be reffered to using the `two-letters country code <https://www.nationsonline.org/oneworld/country_code_list.htm>`_. No limit on the number of coutries to include, though the countries must be reporting data to the `ENTSO-E <https://transparency.entsoe.eu>`_.
* **target** (spreadsheet) / ``Parameter.target`` (python): The country in which to evaluate the impacts.
* **start** (spreadsheet) / ``Parameter.start`` (python): Start date. YYYY | MM | dd | HH | mm in the spreadsheet, with one information per cell on the dedicated row. ``"YYYY-MM-dd HH:mm"`` in Python.
* **end** (spreadsheet) / ``Parameter.end`` (python): End date. YYYY | MM | dd | HH | mm in the spreadsheet, with one information per cell on the dedicated row. ``"YYYY-MM-dd HH:mm"`` in Python.
* **frequency** (spreadsheet) / ``Parameter.freq`` (python): Length of the time step. Default is ``H``. Possibilities are ``Y`` (year) ``M`` (month) ``W`` (week) ``d`` (day) ``H`` (hour) ``30min`` and ``15min``.
* **timezone** (spreadsheet) / `Parameter.timezone` (python): Time zone understandable by Python. To convert in local time after the computation.
* **constant exchanges** (spreadsheet) / ``Parameter.cst_imports`` (python): TRUE to consider constant impacts for all countries but the target country. Impacts become equal to the impact of "Other countries". Default is FALSE.
* **exchanges from swissGrid** (spreadsheet) / ``Parameter.sg_imports`` (python): TRUE to replace ENTSO-E cross-border exchanges *at the Swiss borders* with SwissGrid data. Default is FALSE.
* **net exchanges** (spreadsheet) / ``Parameter.net_exchanges`` (python): TRUE to correct cross-border exchanges so that flow between two countries at each time step is only unidirectional. The correction is made *after* adapting data to the desired frequency. Default is FALSE, i.e. data is treated it is.
* **network losses** (spreadsheet) / ``Parameter.network_losses`` (python): TRUE to consider the network losses. Default is FALSE.
* **residual local** (spreadsheet) / ``Parameter.residual_local`` (python): **Deprecated: it isn't physically representative of the electricity flows. It has now the same effect as residual global.** TRUE will include Swiss residual as non-exchangeable production (consumed in CH). Default is FALSE. Cannot be TRUE at the same time as residual global.
* **residual global** (spreadsheet) / ``Parameter.residual_global`` (python): TRUE will include Swiss residual as tradeable production. Default is FALSE. Cannot be TRUE at the same time as residual local.
* **data cleaning** (spreadsheet) / ``Parameter.data_cleaning`` (python): TRUE to turn on the data autocompleting process. Missing data is replaced with zeros otherwise. Default is TRUE.
* **ch_enr_model_path** (spreadsheet) / ``Parameter.ch_enr_model_path`` (python): Path to the file containing the CH renewable energy production data, exported using EcoDynElec-Enr-Model. When residual global is True, this is used to replace the ``Residual_Other_CH`` category. Default is None.



Filepath Parameters
-------------------
File path settings are in the "Filepath" tab of the spreadsheet, or attributes of the object ``Parameter.path``.

* **generation directory** (spreadsheet) / ``Parameter.path.generation`` (python): Directory containing the generation data. This is also the directory where downloaded files are saved. Path can be relative to the location where the user's script is executed, or the absolute path.
* **exchange directory** (spreadsheet) / ``Parameter.path.exchanges`` (python): Directory containing the exchanges data. This is also the directory where downloaded files are saved. Path can be relative to the location where the user's script is executed, or the absolute path.
* **saving directory** (spreadsheet) / ``Parameter.path.savedir`` (python): Directory where to save computation results. Results are only returned in Python if the field is empty or None. Path can be relative to the location where the user's script is executed, or the absolute path. Default is None.
* **UI vector** (spreadsheet) / ``Parameter.path.ui_vector`` (python): The location of impact per unit type in a single table format. Default file from the support files is used if None is given.
* **mapping file** (spreadsheet) / ``Parameter.path.mapping`` (python): The location of a mapping file. A blank example is available for download on the `git repository <https://github.com/LESBAT-HEIG-VD/EcoDynElec/raw/main/support_files/mapping_template.xlsx>`_. Default UI vector from the support files is used if None is given.
* **neighboring file** (spreadsheet) / ``Parameter.path.neighbours`` (python): The location of a file reporting the connectivity between European countries. Default file from the support files is used if None is given.
* **gap file** (spreadsheet) / ``Parameter.path.gap`` (python): The location of a file containing estimates of the composition of the Swiss residual. Default file from the support files is used if None is given.
* **file swissGrid** (spreadsheet) / ``Parameter.path.swissGrid`` (python): The location of a file containing information from SwissGrid. Default file from the support files is used if None is given.
* **file grid losses** (spreadsheet) / ``Parameter.path.networkLosses`` (python): The location of a file containing estimates of power grid losses. Default file from the support files is used if None is given.




Server Parameters
-------------------
Server settings are in the "Server" tab of the spreadsheet, or attributes of the object ``Parameter.server``. They allow to configure the connection to the ENTSO-E server to retrieve data, as detailed in the dedicated `download tutorial <https://ecodynelec.readthedocs.io/en/latest/examples/downloading.html>`_.

* **host** (spreadsheet) / ``Parameter.server.host`` (python): Name of the sftp host. Default is ``sftp-transparencyentsoe.eu``.
* **port** (spreadsheet) / ``Parameter.server.port`` (python): ID number of the port to use. Default is 22.
* **username** (spreadsheet) / ``Parameter.server.username`` (python): Username or email to connect to the ENTSO-E database. Account should be created for free on the `ENTSO-E webpage <https://transparency.entsoe.eu/>`_. The password gets outdated regularly (one to two months or after a period without using).
* **password** (spreadsheet) / ``Parameter.server.password`` (python): Password to connect to the ENTSO-E database (optional). For security reasons, the field can be left blank (spreadsheet) or set to None (python), and the password will be asked when just ``ecodynelec`` establishes a connection with the servers.
* **use server** (spreadsheet) / ``Parameter.server.useServer`` (python): TRUE to request downloading files from the ENTSO-E database. FALSE (default) will not download.
* **remove unused** (spreadsheet) / ``Parameter.server.removeUnused`` (python): TRUE to remove all local files whose dates do not correspond to the required computation period. FALSE (default) will not delete any file. This functionality is ignored if no file is downloaded.
