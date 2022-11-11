| 
| \ **Handle parameters from Python**\ 

This notebook contains an example to create parameters from the Python
interface directly. + First, the process is entirely done by hand + Then
the possibility to load from a spreadsheet to the parameter object is
highlighted.

*Note: the example section provides only data for default countries and
for Feb. 01, 2017.*

Creating parameters and execute DYNAMICAL
=========================================

.. code:: ipython3

    from dynamical.parameter import Parameter # Import the class to manipulate parameters
    from dynamical.easy_use import execute # Import function managing the whole execution

.. code:: ipython3

    my_param = Parameter() # Initialize a Parameter object
    my_param # visualize the default content




.. parsed-literal::

    ctry --> ['AT', 'CH', 'CZ', 'DE', 'FR', 'IT']
    target --> CH
    start --> 2017-02-01 00:00:00
    end --> 2017-02-01 23:00:00
    freq --> H
    timezone --> CET
    cst_imports --> False
    net_exchanges --> False
    network_losses --> False
    sg_imports --> False
    residual_local --> False
    residual_global --> False
    Filepath to generation --> None
    Filepath to exchanges --> None
    Filepath to raw_generation --> None
    Filepath to raw_exchanges --> None
    Filepath to savedir --> None
    Filepath to savegen --> None
    Filepath to saveimp --> None
    Filepath to mapping --> None
    Filepath to neighbours --> None
    Filepath to gap --> None
    Filepath to swissGrid --> None
    Filepath to networkLosses --> None



The next cell modifies \ **execution**\  parameters:

.. code:: ipython3

    ## Change the starting date
    my_param.start = '2017-02-01 05:00'
    
    ## Change the time step
    my_param.freq = "15min"
    
    ## Consider local CH generation
    my_param.residual_local = True

The next cell modifies \ **file path**\  parameters:

.. code:: ipython3

    # Indicate where to find raw generation data
    my_param.path.raw_generation = "./test_data/generations/"
    
    # Indicate where to find raw exchange data
    my_param.path.raw_exchanges = "./test_data/exchanges/"

The next cell visualizes the changes made in the parameter object

.. code:: ipython3

    print(my_param)


.. parsed-literal::

    ctry --> ['AT', 'CH', 'CZ', 'DE', 'FR', 'IT']
    target --> CH
    start --> 2017-02-01 05:00:00
    end --> 2017-02-01 23:00:00
    freq --> 15min
    timezone --> CET
    cst_imports --> False
    net_exchanges --> False
    network_losses --> False
    sg_imports --> False
    residual_local --> True
    residual_global --> False
    Filepath to generation --> None
    Filepath to exchanges --> None
    Filepath to raw_generation --> /home/francois/Documents/EcoDynBat/EcoDyn/dynamical/examples/test_data/generations/
    Filepath to raw_exchanges --> /home/francois/Documents/EcoDynBat/EcoDyn/dynamical/examples/test_data/exchanges/
    Filepath to savedir --> None
    Filepath to savegen --> None
    Filepath to saveimp --> None
    Filepath to mapping --> None
    Filepath to neighbours --> None
    Filepath to gap --> None
    Filepath to swissGrid --> None
    Filepath to networkLosses --> None
    


.. code:: ipython3

    impacts = execute(p=my_param, is_verbose=False) # Execute DYNAMICAL from the parameter object

.. code:: ipython3

    ### Display a summary of results
    impacts['Global'].mean()




.. parsed-literal::

    GWP                    0.323312
    CED_renewable          1.582290
    CED_non-renewable      8.301846
    ES2013               377.853476
    dtype: float64



Loading parameters from an xlsx spreadsheet
===========================================

.. code:: ipython3

    my_param = Parameter() # Initialize the parameter object
    my_param.from_excel("Spreadsheet_test.xlsx") # Load from spreadsheet
    my_param # Display the parameters




.. parsed-literal::

    ctry --> ['AT', 'CH', 'DE', 'FR', 'IT']
    target --> CH
    start --> 2017-02-01 00:00:00
    end --> 2017-02-01 23:00:00
    freq --> H
    timezone --> CET
    cst_imports --> False
    net_exchanges --> False
    network_losses --> False
    sg_imports --> False
    residual_local --> False
    residual_global --> False
    Filepath to generation --> None
    Filepath to exchanges --> None
    Filepath to raw_generation --> /home/francois/Documents/EcoDynBat/EcoDyn/dynamical/examples/test_data/generations/
    Filepath to raw_exchanges --> /home/francois/Documents/EcoDynBat/EcoDyn/dynamical/examples/test_data/exchanges/
    Filepath to savedir --> None
    Filepath to savegen --> None
    Filepath to saveimp --> None
    Filepath to mapping --> None
    Filepath to neighbours --> None
    Filepath to gap --> None
    Filepath to swissGrid --> None
    Filepath to networkLosses --> None



Documentation
=============

.. code:: ipython3

    help(Parameter())


.. parsed-literal::

    Help on Parameter in module dynamical.parameter object:
    
    class Parameter(builtins.object)
     |  Parameter object adapted to the execution of the algorithm.
     |  
     |  Attributes:
     |      - path: FilePath object containing information about path to different documents.
     |      - ctry: the (sorted) list of countries to include
     |      - target: the target country where to compute the mix and impact.
     |      - start: starting date (utc)
     |      - end: ending date (utc)
     |      - freq: the time step (15min, 30min, H, d, W, M or Y)
     |      - timezone: the timezone to convert in, in the end
     |      - cst_imports: boolean to consider a constant impact for the imports
     |      - sg_imports: boolean to replace Entso exchanges by SwissGrid exchanges
     |      - net_exchanges: boolean to consider net exchanges at each border (no bidirectional)
     |      - residual_local: to include a residual (for CH) as if it was all consumed in the country.
     |      - residual_global: to include a residual (for CH) that can be exchanged.
     |  
     |  Methods:
     |      - from_excel: to load parameters from a excel sheet
     |      - __setattr__: to allow simple changes of parameter values.
     |                  + easy use: parameter_object.attribute = new_value
     |                  + start and end remain datetimes even if strings are passed
     |                  + ctry remain a sorted list even if an unsorted list is passed
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  __repr__(self)
     |      Return repr(self).
     |  
     |  __setattr__(self, name, value)
     |      Implement setattr(self, name, value).
     |  
     |  from_excel(self, excel)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    


.. code:: ipython3

    from dynamical.parameter import Filepath
    help(Filepath)


.. parsed-literal::

    Help on class Filepath in module dynamical.parameter:
    
    class Filepath(builtins.object)
     |  Filepath object adapted to the execution of the algorithm and the Parameter class.
     |  
     |  Attributes:
     |      - rootdir: root directory of the experiment (highest common folder).
     |              Useful mainly within the class
     |      - generation: directory containing Entso generation files
     |      - exchanges: directory containing Entso cross-border flow files
     |      - savedir: directory where to save the results. Default: None (no saving)
     |      - savgen: directory where to save generation from raw files. Default: None (no saving)
     |      - saveimp: directory to save exchange from raw files. Default: None (no saving)
     |      - mapping: file with the mapping (impact per kWh produced for each production unit)
     |      - neighbours: file gathering the list of neighbours of each european country
     |      - gap: file with estimations of the nature of the residual
     |      - swissGrid: file with production and cross-border flows from Swiss Grid
     |      - networkLosses: file with estimation of the power grid losses.
     |  
     |  Methods:
     |      - from_excel: load the attributes from a excel sheet.
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  __repr__(self)
     |      Return repr(self).
     |  
     |  __setattr__(self, name, value)
     |      Implement setattr(self, name, value).
     |  
     |  from_excel(self, excel)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    


