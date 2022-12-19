Handle parameters from Python
=============================

This page contains an example to create parameters from the Python
interface directly. + First, the process is entirely done by hand + Then
the possibility to load from a spreadsheet to the parameter object is
highlighted.

*Note: the example section provides only data for default countries and
for Feb. 01, 2017.*

Creating parameters and execute DYNAMICAL
-----------------------------------------

.. code:: ipython3

    import os, sys
    sys.path.insert(0, os.path.abspath("../"))
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
    timezone --> UTC
    cst_imports --> False
    net_exchanges --> False
    network_losses --> False
    sg_imports --> False
    residual_local --> False
    residual_global --> False
    data_cleaning --> True
    
    Filepath to generation --> None
    Filepath to exchanges --> None
    Filepath to savedir --> None
    Filepath to fu_vector --> None
    Filepath to mapping --> None
    Filepath to neighbours --> None
    Filepath to gap --> None
    Filepath to swissGrid --> None
    Filepath to networkLosses --> None
     
    Server for useServer --> False
    Server for host --> sftp-transparency.entsoe.eu
    Server for port --> 22
    Server for username --> None
    Server for password --> 
    Server for removeUnused --> False
    Server for _remoteGenerationDir --> /TP_export/AggregatedGenerationPerType_16.1.B_C/
    Server for _remoteExchangesDir --> /TP_export/PhysicalFlows_12.1.G/



The next cell modifies \ **execution**\  parameters:

.. code:: ipython3

    ## Change the starting date
    my_param.start = '2017-02-01 05:00'
    
    ## Change the time step
    my_param.freq = "15min"
    
    ## Turn off the auto-complete
    my_param.data_cleaning = False

The next cell modifies \ **file path**\  parameters:

.. code:: ipython3

    # Indicate where to find generation data
    my_param.path.generation = "./test_data/generations/"
    
    # Indicate where to find exchange data
    my_param.path.exchanges = "./test_data/exchanges/"

The next cell visualizes the changes made in the parameter object

.. code:: ipython3

    print(my_param)


.. parsed-literal::

    ctry --> ['AT', 'CH', 'CZ', 'DE', 'FR', 'IT']
    target --> CH
    start --> 2017-02-01 05:00:00
    end --> 2017-02-01 23:00:00
    freq --> 15min
    timezone --> UTC
    cst_imports --> False
    net_exchanges --> False
    network_losses --> False
    sg_imports --> False
    residual_local --> False
    residual_global --> False
    data_cleaning --> False
    
    Filepath to generation --> /home/user/dynamical/examples/test_data/generations/
    Filepath to exchanges --> /home/user/dynamical/examples/test_data/exchanges/
    Filepath to savedir --> None
    Filepath to fu_vector --> None
    Filepath to mapping --> None
    Filepath to neighbours --> None
    Filepath to gap --> None
    Filepath to swissGrid --> None
    Filepath to networkLosses --> None
     
    Server for useServer --> False
    Server for host --> sftp-transparency.entsoe.eu
    Server for port --> 22
    Server for username --> None
    Server for password --> 
    Server for removeUnused --> False
    Server for _remoteGenerationDir --> /TP_export/AggregatedGenerationPerType_16.1.B_C/
    Server for _remoteExchangesDir --> /TP_export/PhysicalFlows_12.1.G/
    


.. code:: ipython3

    impacts = execute(config=my_param, is_verbose=False) # Execute DYNAMICAL from the parameter object

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
-------------------------------------------

.. code:: ipython3

    my_param = Parameter() # Initialize the parameter object
    my_param.from_excel("Spreadsheet_test.xlsx") # Load from spreadsheet
    my_param # Display the parameters




.. parsed-literal::

    ctry --> ['AT', 'CH', 'CZ', 'DE', 'FR', 'IT']
    target --> CH
    start --> 2017-02-01 05:00:00
    end --> 2017-02-01 23:00:00
    freq --> 15min
    timezone --> UTC
    cst_imports --> False
    net_exchanges --> False
    network_losses --> False
    sg_imports --> False
    residual_local --> False
    residual_global --> False
    data_cleaning --> False
    
    Filepath to generation --> /home/user/dynamical/examples/test_data/generations/
    Filepath to exchanges --> /home/user/dynamical/examples/test_data/exchanges/
    Filepath to savedir --> None
    Filepath to fu_vector --> None
    Filepath to mapping --> None
    Filepath to neighbours --> None
    Filepath to gap --> None
    Filepath to swissGrid --> None
    Filepath to networkLosses --> None
     
    Server for useServer --> False
    Server for host --> sftp-transparency.entsoe.eu
    Server for port --> 22
    Server for username --> None
    Server for password --> 
    Server for removeUnused --> False
    Server for _remoteGenerationDir --> /TP_export/AggregatedGenerationPerType_16.1.B_C/
    Server for _remoteExchangesDir --> /TP_export/PhysicalFlows_12.1.G/
 
