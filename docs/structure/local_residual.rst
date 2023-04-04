Include residuals
=================

For the specific case of Switzerland, some additional local production needs to be included, as a portion of the electricity in Switzerland is not reported to the ENTSO-E. This portion is low-voltage and locally-generated electricity that reaches between 10% and 35% of the total swiss production. This additional production is called "residual" in EcoDynElec. The central location of Switzerland in Europe and the fact that lots of energy transits through Switzerland, raise the interests in including these additional prudiction portions into the generation mix of Switzerland.

This residual must be estimated. Statistics and data from SwissGrid (Swiss network operator) and the SFOE (Federal office of energy) can be coupled to obtain an estimate of the amount of energy in this residual. Different statistics from the SFOE allow rough estimate of its source decomposition, usually shared between hydro power (40-90%), roof photovoltaic (0-40%) and a diversity of smaller sources.

This residual production can be addede in two ways. It may be included "globally", i.e. the residual is considered a generation unit among other and its produced electricity enters the overall mix of Switzerland and can be exchanged with neighbour countries. Alternatively it may be included "locally", i.e. it is assumed to be produced and consumed in Switzerland only. To include this residual locally, the addition must be done after the electricity tracking (Figure 1), if the target country is Switzerland.

.. figure:: images/local_residual.png
    :alt: algorithmic structure to include residual locally
    
    *Include the Swiss production residual locally.*