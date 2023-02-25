# Data directory

Some external data is required for the software to work at its full range of capabilities. This directory stores the required information. A dedicated documentation page on these [additional data files](https://ecodynelec.readthedocs.io/en/latest/supplementary/auxilary_files.html) goes more in depth on their content and origin.


## Functional Unit Vector
This is the default matrix of data containing impact information for every type of production unit. A dedicated page was written in the [documentation](https://ecodynelec.readthedocs.io/en/latest/supplementary/functional_unit.html)


## Neighbourhood EU
This file maps the links between countries in europe. Are considered "neighbours" (in the sense of this file) the countries exchanging electricity according to the ENTSO-E.

## Pertes OFEN
Table containing information extracted from SFOE electricity reports, the relevant information being an monthly estimate of electricity losses in Switzerland.

## Share residual
Table containing an estimate of the share of different technologies for the residual. See original publication and documentation paragraph on the [residual](https://ecodynelec.readthedocs.io/en/latest/supplementary/auxilary_files.html#repartition-residual) for more details. This file is the bare minimum data table extracted from the file `Repartition_Residus.xlsx` in the `support_files/` directory of the git repo.

## SwissGrid total
Very large table containing all useful data from SwissGrid from 2015 until last update. This table justifies its existence for computation time reasons. Indeed each original SwissGrid excel file takes about 30 sec to load, while only a few miliseconds are necessary to load multiple years from the `SwissGrid_total.csv` file. A function in `ecodynelec.updating` allows to extract data directly from original SwissGrid files, so EcodDynElec does not have to reiterate this costly process at every run.
