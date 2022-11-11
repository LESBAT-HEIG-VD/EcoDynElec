Functional Unit vector
======================




Impact per production unit
**************************

The functional unit (FU) vector actually a matrix constructed via extraction of information in block 3 of the mapping file, as described in Appendix: Files for data preprocessing. Each column is an impact category obtained from the mapping file. The indexes are formatted as follows:
    * *Name_country*: Applicable for all unit types. The names are obtained from the mapping file. Remaining spaces in original names are replaced with an underscore (``_``). The countries are from the parameters. It is important to have the country at the end of the index, separated from the rest with an underscore (``_``).
    * *Mix_Other*: This unique row is used for all electricity imported from outside the bounds of the study (other countries). It is treated as a specific unit type called Mix from a specific country tagged Other. This specific index must be included in the vector.



Considering losses: what is FUt ?
*********************************

The code and equations make a difference between the FU vector and the applied functional unit at a specific time step FUt.
The first gathers the impacts of 1kWh of production from each unit type in each country. These values are modeling assumptions and do not change.

The second FUt is the FU vector multiplied by the losses at each time step.
