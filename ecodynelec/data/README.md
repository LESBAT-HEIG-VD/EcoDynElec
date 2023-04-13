# Data directory

Some external data is required for the software to work at its full range of capabilities. This directory stores some required information. A dedicated documentation page on the different kinds of [input data](https://ecodynelec.readthedocs.io/en/latest/data_input/overview.html) goes more in depth on their content and origin.







## Mapping and LCA Impacts

EcoDynElec computes the LCA impacts of electricity based on the electricity mix and LCA data of the electricity generation in each involved country. The data can be provided to EcoDynElec via an adapted spreadsheet or additional file. The spreadsheet [mapping_template.xlsx](https://github.com/LESBAT-HEIG-VD/EcoDynElec/blob/main/support_files/mapping_template.xlsx) is a blank template hosting the structure and equations required to transform data from LCA databases and adapt them to the electricity data from ENTSO-E.

The data itself is **not provided per default**, for licensing reasons. Thus extracting data from LCA database and softwares is left to the user. However, **for the software to being fully operational**, a default [Unit Impact file](https://github.com/LESBAT-HEIG-VD/EcoDynElec/blob/main/ecodynelec/data/Unit_Impact_Vector.csv) was created. This file contains, for 6 countries only (AT, CH, DE, FR, IT, CZ) and 4 impact categories, the results of LCA data processing *through the mapping spreadsheet*. If no LCA data is provided by the user, EcoDynElec will try and use this default file. More information is provided in the [LCA data](https://ecodynelec.readthedocs.io/en/latest/data_input/lca_data.html) page as well.








## Residual model

The need for considering a production residual in Switzerland comes from a difference in global electricity generation reported in SFOE annual reports and on the ENTSO-E databases. Information from the SFOE comes from Table 23 (p29) of each annual [SFOE Electricity Statistics](https://www.bfe.admin.ch/bfe/en/home/supply/statistics-and-geodata/energy-statistics/electricity-statistics.html) report. The [Generation Residual](https://ecodynelec.readthedocs.io/en/latest/data_input/residual.html) page further develops this the modeling hypotheses.

A default file is used for Switzerland, with all sources explained. Thus the the user is not required to provide its own data. The default file [Share_residual.csv](https://github.com/LESBAT-HEIG-VD/EcoDynElec/blob/main/ecodynelec/data/Share_residual.csv) covers 2016 to 2021 and is used by EcoDynElec, based on the [Residual_model.xlsx](https://github.com/LESBAT-HEIG-VD/EcoDynElec/blob/main/support_files/Residual_model.xlsx) file. The latter contains the modeling hypotheses and calculation based on the SFOE statistics, while the former only considers the result and is stored within the files of inside the package. The SFOE statistics are usually published yearly during the 3rd week of June.








## SwissGrid

Swiss Grid information contains global 15min frequency information about the electric grid in Switzerland. Files can be downloaded on SwissGrid website under rubric [transmission] (https://www.swissgrid.ch/en/home/operation/grid-data/transmission.html). Several information is used at different steps of the computation.

The exchanges between Switzerland and their neighbor countries (Cross Border Exchange, columns K-R) are used as exchanges at the Swiss borders instead of ENTSO-E data if requested by the user.

The total energy production is compared with the sum of Swiss production in ENTSO-E databases to evaluate amount of residual energy. This amount of residual is then coupled with relative information from the `Residual_model.xlsx` file.

The default file [SwissGrid_total.csv](https://github.com/LESBAT-HEIG-VD/EcoDynElec/blob/main/ecodynelec/data/SwissGrid_total.csv) is used if no information is specified. This file is a concatenation of all files of the Swiss electricity operator from the period 2015 - 2022. The user is not required to provide its own data.








## SFOE Data

Distribution losses from the electric network can only be considered only for Swizerland in the current version of EcoDynElec. It relies on [SFOE](https://www.bfe.admin.ch/bfe/en/home.html) data.
The data used consists in tables of monthly statistics from the Swiss Federal Office of Energy (SFOE), so far covering 2012 to 2021. These values are obtained in Table A-1a (p47-p49) from each annual [SFOE Electricity Statistics](https://www.bfe.admin.ch/bfe/en/home/supply/statistics-and-geodata/energy-statistics/electricity-statistics.html) report. Only the column "*Pertes*" is used in the current version of EcoDynElec, though additional information is kept for possible use extension.

A default file is used for Switzerland, with all sources explained. Thus the the user is not required to provide its own data. The default file [SFOE_data.csv](https://github.com/LESBAT-HEIG-VD/EcoDynElec/blob/main/ecodynelec/data/SFOE_data.csv) is used by EcoDynElec, it directly reports the data provided in the SFOE statistics. The SFOE statistics are usually published yearly during the 3rd week of June.







## Neighbor

List for all European countries of their direct neighbors, i.e. directly linked through an active power connection. Information obtained from the [ENTSO-E website](https://transparency.entsoe.eu/transmission-domain/physicalFlow/show).

A default file is used by EcoDynElec, this field does not require further inputs from the user.
