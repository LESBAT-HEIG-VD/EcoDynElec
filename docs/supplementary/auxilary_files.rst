Additional data
===============

Describe the additional data required for the algorithms to work


Neighbor
*************
List for all European countries of their direct neighbors, i.e. directly linked through an active power connection. Information obtained from the `ENTSO-E website <https://transparency.entsoe.eu/transmission-domain/physicalFlow/show>`_.





Pertes OFEN
*************
Losses are considered only for Swizerland.
Table of monthly statistics from the Swiss Federal Office of Energy (SFOE) covering 2012 to 2021. These values are obtained in Table A-1a (p47-p49) from each annual `SFOE Electricity Statistics <https://www.bfe.admin.ch/bfe/en/home/supply/statistics-and-geodata/energy-statistics/electricity-statistics.html>`_ report. Only the column "*Pertes*" is used in the current version of DYNAMICAL, though additional information is kept for possible use extension.










Repartition Residual
********************
The need for considering a production residual in Switzerland comes from a difference in global electricity generation reported in SFOE annual reports and on the ENTSO-E databases. Information from the SFOE comes from Table 23 (p29) of each annual `SFOE Electricity Statistics <https://www.bfe.admin.ch/bfe/en/home/supply/statistics-and-geodata/energy-statistics/electricity-statistics.html>`_ report. Current information provided in DYNAMICAL covers 2016 to 2021 with one weekday, one Saturday and one Sunday per month.

As generation units differ between two data sources, the units from the ENTSO-E database are aggregated prior the comparison. The available file is the result of the comparison in percentage, highlighting the relative composition of excess of energy production reported in the SFOE documents and not in ENTSO-E databases









SwissGrid
*************
Swiss Grid information contains global 15min frequency information about the electric grid in Switzerland. Files can be downloaded on SwissGrid website under rubric `transmission <https://www.swissgrid.ch/en/home/operation/grid-data/transmission.html>`_. Several information is used at different steps of the computation.

The exchanges between Switzerland and their neighbor countries (Cross Border Exchange, columns K-R) are used as exchanges at the Swiss borders instead of ENTSO-E data if requested by the user.

The total energy production is compared with the sum of Swiss production in ENTSO-E databases to evaluate amount of residual energy. This amount of residual is then coupled with relative information from the Repartition Residual file.











Mapping and Impact
*******************
The so-called Mapping contains all modeling hypotheses to compute the impacts of a kWh produced by each unit type of each country as well as for the residual. Source information is extracted from Ecoinvent databases and modified within the mapping file. Each tab of the file can be split in 4 blocks:

#. The first few columns on the left represent the link between generic unit types available in ENTSO-E databases and detailed unit types as available in Ecoinvent.
#. The second block, labeled Environmental impacts of Ecoinvent sources, contains the impacts per kWh of production from each unit type as defined in the Ecoinvent database. The values are from Ecoinvent. Ecoinvent also suggests an overall technology share (how much of each unit type is installed in the country) used to link unit types from both Ecoinvent and ENTSO-E databases.
#. The third block, labeled Environmental impacts of ENTSO-E sources, contains the impacts per kWh of production grouped by unit type as defined in the ENTSO-E database. This block contains the values to be used in DYNAMICAL.
#. A fourth block may be located bellow the first block. They allow an estimation of Other Fossil and Other Renewable, two production unit types provided in ENTSO-E databases and absent from Ecoinvent. The impact of each of these units is replaced by the impacts of one other production unit of Ecoinvent. Three choices are available for each unit type: Max. (choses replacement unit that maximizes the impacts of this unit), Min. (idem with minimum) and Moy. (average scenario). Per default, the Max. is selected.

This format is similar for all countries. Though it differs slightly between AT, CH, DE, FR, IT, CZ and the rest of countries.

For the Residual, the impacts are presented and computed in first to third blocks in the same manner and the choice of unit type is also determined via a similar fourth block. A fifth block is added bellow and contains all impact values of unit types that are most likely to supply the residual.

Some DYNAMICAL functions were specifically tailored to extract relevant information from excel spreadsheets with this exact formatting. Impact values per unit type and country are then merged together in an exploitable vector of unitary impacts called Functional Unit (FU) vector.





A word about data cleaning
**************************
No support file is related to the data cleaning procedure. Though there are options in the Parameters and Excel File to turn this capability on and off. The data cleaning affects only the generation data from ENTSO-E and requires two steps: identification of missing data and replacement of missing data.

The identification uses two mechanisms. First, it first flags all time steps with either no production in an entire country, or no nuclear production if the country’s nuclear production is not constantly zero throughout the covered period. Then these time steps are sorted on whether they define a time span smaller (short) or greater (long) than two hours.

Long spans of missing data are replaced with values of typical days using 7 days before and after the gap. Linear interpolation is used for the short time spans.





Spreadsheet for parameter handling
**********************************
Computation parameters can be handled via an Excel spreadsheet or directly in Python via a Parameter object. The Excel spreadsheet is made of 3 tabs. The Parameter tab contains general parameters (e.g. list of countries, target countries, dates and frequency). The Filepath tab is for the link to files and directories (e.g. location of generation and cross-border flow files, where to save results). The Server tab helps connecting to the SFTP server of ENTSO-E. More detail about each field and their meaning can be found in Appendix: Handle the parameters. A use example is also detailed there.
