Data cleaning
==============

No dataset is perfect and the generation and cross-border flow data from the ENTSO-E is no exception. Thus a specific procedure was implemented to estimate the values of missing data. This feature can be turned off or on (default) via the ``data_cleaning`` element of the main section in the `configuration procedure <https://ecodynelec.readthedocs.io/en/latest/data_input/parameters.html#main-parameters>`__.


Identify missing data
----------------------
EcoDynElec only considers data is missing when *no data was reported* for a specific unit in a specific country, or at a specific border between two countries. This differs from data reported as *zero* or only partially reported, which is considered as is and not corrected.



Infer missing data
-------------------
The missing data is classified in 3 categories:  excessive gaps, long gaps and short gaps. Default criteria and values are assumed for the classification and cleaning, however these are parameters of the ``autocomplete`` function of the `autocomplete <https://ecodynelec.readthedocs.io/en/latest/modules/preprocessing.autocomplete.html#ecodynelec.preprocessing.autocomplete.autocomplete>`__ module. The descriptions below are using the default values for the explanation.

Excessive gaps
~~~~~~~~~~~~~~~~
An excessive gap is a missing chunk of data representing over 30% of the total horizon of the experiment (from start time to end time). Such a gap is considered as too consequent to estimate the missing data with a realistic accuracy. Thus the plant or field, or border connection is assumed as off-grid and **data is filled with zeros**.

Long gaps
~~~~~~~~~~~
Long gaps are spans of missing data longer than 2h but shorter than 30% of the total horizon of the experiment. The missing data is ***inferred using an average day***, day calculated using 7 days before and after the gap (or rather what is available over these two periods). If the span of missing data is at the start or end of the horizon, only 7 days of available data is used to build the average day. The span of missing data is then filled one time step at a time using the corresponding day time in the average day.

Short gaps
~~~~~~~~~~~~~
Short gaps consist of missing data for less than a 2h time span. For *all fields but the solar generation*, a **linear interpolation** is used between the two extremities of the gap. If the gap is located at the far end of the horizon, the gap is filled with the last available value. If the gap is located at the start of the horizon, the gap is filled with the first available value.

A short gap in the **solar generation is always considered as a long gap**. This ensures the diurnal pattern and natural cycle inherent to the technology is not violated, by a linear interpolation in an appropriate time, and more importantly if the gap occurs at an extremity of the time horizon.

These gaps are identified early in the cleaning process, but inferred only at the end, when only these gaps are remaining. This allows to classify the missing solar generation differently and facilitate the application of the linear interpolation.




Required information
----------------------
The cleaning procedure is fully automatized and only requires the generation and cross-border data itself. Thus **no input of external data from the user is required**. The user only needs to turn on (default) or off the cleaning feature in the main section in the `configuration procedure <https://ecodynelec.readthedocs.io/en/latest/data_input/parameters.html#main-parameters>`__.  For further customization of the behavior for the classification of gaps and the cleaning, the user is referred to the main ``autocomplete`` function of the  `autocomplete <https://ecodynelec.readthedocs.io/en/latest/modules/preprocessing.autocomplete.html#ecodynelec.preprocessing.autocomplete.autocomplete>`__ module.