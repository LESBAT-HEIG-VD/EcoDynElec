Overall Architecture
====================


The ``ecodynelec`` software is built as an ensemble of modules organized around 3 steps (Figure 1). The preprocessing steps include the download or loading of relevant data, the cleaning and adjustment to the correct time step. The large diversity of data lead to a high number of functions and increased complexity of the data treatment, thus all these functions were gathered in a sub-package called ``preprocessing``. Then the pre-treated data can be used to track electricity "from the socket to the source", aggregated in ``ecodynelec`` as a type of electricity plant in a country. This process outptus the electric mix in a target country, i.e. the decomposition per source of  origin of 1kWh of electicity in the target country. Once the electric mix obtained, a third step uses the impact per electricity plant type (impact for this kind of plant to produce 1kWh of electricity) to calculate the overall impact of 1kWh of electricity.

.. figure:: ../images/workflow.png
    :alt: EcoDynElec group of functions
    
    *Figure 1: Schematic visualization of different groups of functions in ``ecodynelec``*
    
    
    
A more detailed schema of how the different modules intricate within `ecodynelec` is shown in Figure 2

.. figure:: ./images/architecture.png
    :alt: Modules of ecodynelec
    
    *Figure 2: Modules, process and usage of ``ecodynelec``*



`ecodynelec` algorithm can be executed all at once, from downloading the data to computing the environmental impacts. Figure 3 is a schematic overview of how it works.

.. figure:: images/global_execution.png
    :alt: Overall ecodynelec process
    
    *Figure 3: Overall pipeline of ``ecodynelec``*