Using fully with Python
=======================

``ecodynelec`` offers the possibility to being fully used via Python.
This tutorial shows the different steps and possibilities, relying
solely on operations doable within a python script or notebook. As the
configuration of ``ecodynelec`` pipeline execution may benefit from more
visual interaction, an alternative is suggested in the “`Using with a
spreadsheet-based
configuraion <https://ecodynelec.readthedocs.io/en/latest/examples/with_spreadsheet.html>`__”
tutorial.

Initialization
--------------

To download and install ``ecodynelec`` to being used as a python
package, the user is referred to either the `getting started
tutorial <https://ecodynelec.readthedocs.io/en/latest/examples/getting_started.html>`__.

Configuration
-------------

The configuration of ``ecodynelec`` is handled by the ``parameter``
module.

.. code:: ipython3

    from ecodynelec.parameter import Parameter # Import the class to manipulate parameters

Python is an object oriented language. Thus a specific configuration can
be built and stored in a ``Parameter`` object that will be called
``my_config`` in this tutorial. The next cell only initializes the
configuration object with the default parameters.

.. code:: ipython3

    my_config = Parameter() # Initialize a configuration object

Before modifying the configuration, let’s have a look at this default
setting

.. code:: ipython3

    print(my_config)


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
    


The configuration is composed of 3 parts. The detail about the meaning
of each is developed in the `input data
section <https://ecodynelec.readthedocs.io/en/latest/data_input/parameters.html>`__.
Essentially:
* the first block contains the elements to configure the
execution itself. These elements are directly available and modifiable
with the syntax ``my_config.element``.
* the second block deals with
all paths to information files, directory containing information, or
where to write and save information before, during and after the
computation. It is accessible with the syntax ``my_config.path.element``
* the third block deals with information related to the ENTSO-E server,
as electricity data from the ENTSO-E server is at the center of
``ecodynelec``. More on this topic is covered on the next paragraph and
on the dedicated `downloading
tutorial <https://ecodynelec.readthedocs.io/en/latest/examples/downloading.html>`__.

The next cell partly modifies the execution configuration.
* First the starting date is modified. Note that objects of the ``Parameter`` class
will verify if this element is a date, and will raise an error if the format is not
recognized.
* Then we modify the size of time step (frequency) for the computation. Possibilities
are specified in the `input data section <https://ecodynelec.readthedocs.io/en/latest/data_input/parameters.html>`__.
* Third in this example, the auto-completing feature is turned off.

.. code:: ipython3

    ## Change the starting date
    my_config.start = '2017-02-01 00:00'
    
    ## Change the time step
    my_config.freq = "15min"
    
    ## Change the coutry list
    my_config.ctry = ['AT','CH','DE','FR','IT']
    
    ## Turn off the auto-complete
    my_config.data_cleaning = False

The next cell partly modifies file path configuration. Here we modify
the location of directories containing data downloaded from the ENTSO-E
database.

.. code:: ipython3

    # Indicate where to find generation data
    my_config.path.generation = "./test_data/generations/"
    
    # Indicate where to find exchange data
    my_config.path.exchanges = "./test_data/exchanges/"

Note that, for the ``generation``, ``exchanges`` and ``savedir`` paths,
the specified directory *will be created if it does not already exist*.
For every other file path element, *a default file* is used if nothing
is specified, and an error is returned if the information passed does
not correspond to any existing file on your local machine.

Downloading Entso-E data
~~~~~~~~~~~~~~~~~~~~~~~~

The `downloading
tutorial <https://ecodynelec.readthedocs.io/en/latest/examples/downloading.html>`__
covers the specificities about how to download the ENTSO-E data or
include the download as part of the ``ecodynelec`` pipeline execution.
This feature is not triggered per default and ``ecodynelec`` is
expecting to find already downloaded ENTSO-E files.

Execution
---------

``ecodynelec`` is build out of a myriad of modules that can be used
relatively independently, under the condition that inputs data is shaped
the correct way. Fortunately, the entire pipeline starting from a set of
parameters and computing down to the calculation of impact metrics.

The usage of this entire pipeline is demonstrated below. This pipeline
allows to save results into files (c.f. paragraph on
`configuration <https://ecodynelec.readthedocs.io/en/latest/examples/with_python.html#configuration>`__).
However results are also always returned for further in-script use.
These results are stored in the ``impacts`` variable for later
paragraphs in this tutorial.

.. code:: ipython3

    from ecodynelec.pipelines import execute

.. code:: ipython3

    impacts = execute(config=my_config, is_verbose=True)


.. parsed-literal::

    Load auxiliary datasets...
    Load generation data...
    	Generation data.
    Data loading: 0.02 sec..
    Memory usage table: 0.18 MB
    Autocomplete...               5/5)...
    =========================
    Missing data identified: 8 (0.22%)
                                    AT CH DE FR IT
    Biomass                          -  -  -  -  -
    Fossil Gas                       -  -  -  -  -
    Fossil Hard coal                 -  -  -  -  -
    Fossil Oil                       -  -  -  -  -
    Geothermal                       -  -  -  -  -
    Hydro Pumped Storage             -  -  -  8  -
    Hydro Run-of-river and poundage  -  -  -  -  -
    Hydro Water Reservoir            -  -  -  -  -
    Other                            -  -  -  -  -
    Other renewable                  -  -  -  -  -
    Solar                            -  -  -  -  -
    Waste                            -  -  -  -  -
    Wind Onshore                     -  -  -  -  -
    Nuclear                          -  -  -  -  -
    Fossil Brown coal/Lignite        -  -  -  -  -
    Fossil Coal-derived gas          -  -  -  -  -
    Wind Offshore                    -  -  -  -  -
    =========================
    Extraction raw generation: 0.12 sec.             
    	Extraction time: 0.14 sec.
    	4/4 - Resample exchanges to 15min steps...
    Get and reduce importation data...
    	Cross-border flow data.
    Data loading: 0.02 sec..
    Memory usage table: 0.04 MB
    Autocomplete...               ...
    =========================
    Missing data identified: 1152 (71.38%)
        AT CH  DE  FR  IT
    CH   -  -   -   -   -
    CZ   -  -   -   -   -
    DE   -  -   -   -   -
    HU  96  -   -   -   -
    IT   -  -   -   -   -
    SI  96  -   -   -  96
    AT   -  -   -   -   -
    FR   -  -   -   -   -
    DK   -  -  96   -   -
    NL   -  -  96   -   -
    PL   -  -  96   -   -
    SE   -  -  96   -   -
    BE   -  -   -  96   -
    ES   -  -   -  96   -
    GB   -  -   -  96   -
    GR   -  -   -   -  96
    MT   -  -   -   -  96
    =========================
    Extraction raw import: 0.09 sec.             
    	Extraction time: 0.11 sec.
    Resample exchanges to 15min steps...
    Gather generation and importation...
    Import of data: 0.3 sec
    Importing information...
    Tracking origin of electricity...
    	compute for day 1/1   
    	Electricity tracking: 0.8 sec.
    
    Compute the electricity impacts...
    	Global...
    	Climate Change...
    	Human carcinogenic toxicity...
    	Fine particulate matter formation...
    	Land use...
    Impact computation: 0.0 sec.
    Adapt timezone: UTC >> UTC
    done.


Outcome and Visualization
-------------------------

The outcome is stored in files and returned for further in-script use.
In the previous section, results were stored in the ``impacts``
variable. The current section highlights the content returned and shows
some basic possibilities for data visualization.

.. code:: ipython3

    import numpy as np
    import pandas as pd

Description of the outcome
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``impacts`` variable contains a collection of tables. This
collection is a ``dict`` with one ``Global`` key, and one other key per
impact category:

.. code:: ipython3

    print(impacts.keys())


.. parsed-literal::

    dict_keys(['Global', 'Climate Change', 'Human carcinogenic toxicity', 'Fine particulate matter formation', 'Land use'])


The ``Global`` table is the *sum across all technologies* for each
index, as it is shown for the first few time steps:

.. code:: ipython3

    display(impacts['Global'].head())



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>Climate Change</th>
          <th>Human carcinogenic toxicity</th>
          <th>Fine particulate matter formation</th>
          <th>Land use</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-02-01 00:00:00</th>
          <td>0.460800</td>
          <td>0.030586</td>
          <td>0.000353</td>
          <td>0.007269</td>
        </tr>
        <tr>
          <th>2017-02-01 00:15:00</th>
          <td>0.460092</td>
          <td>0.030610</td>
          <td>0.000353</td>
          <td>0.007258</td>
        </tr>
        <tr>
          <th>2017-02-01 00:30:00</th>
          <td>0.460153</td>
          <td>0.030682</td>
          <td>0.000353</td>
          <td>0.007247</td>
        </tr>
        <tr>
          <th>2017-02-01 00:45:00</th>
          <td>0.457920</td>
          <td>0.030642</td>
          <td>0.000348</td>
          <td>0.007215</td>
        </tr>
        <tr>
          <th>2017-02-01 01:00:00</th>
          <td>0.458639</td>
          <td>0.030747</td>
          <td>0.000349</td>
          <td>0.007192</td>
        </tr>
      </tbody>
    </table>
    </div>


The other tables are, for each impact category, the breakdown into all
possible sources:

.. code:: ipython3

    for i in impacts: # Iterate for all impact categories
        if i=='Global': continue; # Skip the Global, already visualized above.
        
        print(f"#############\nimpacts for {i}:")
        display( impacts[i].head(3).T ) # Transpose table for readability


.. parsed-literal::

    #############
    impacts for Climate Change:



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>2017-02-01 00:00:00</th>
          <th>2017-02-01 00:15:00</th>
          <th>2017-02-01 00:30:00</th>
        </tr>
        <tr>
          <th>Climate Change_source</th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_Other</th>
          <td>0.006686</td>
          <td>0.006624</td>
          <td>0.006525</td>
        </tr>
        <tr>
          <th>Biomass_AT</th>
          <td>0.000330</td>
          <td>0.000325</td>
          <td>0.000317</td>
        </tr>
        <tr>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Coal-derived_gas_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Gas_AT</th>
          <td>0.018306</td>
          <td>0.017540</td>
          <td>0.017000</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>Other_renewable_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Solar_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Waste_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Offshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Onshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
      </tbody>
    </table>
    <p>101 rows × 3 columns</p>
    </div>


.. parsed-literal::

    #############
    impacts for Human carcinogenic toxicity:



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>2017-02-01 00:00:00</th>
          <th>2017-02-01 00:15:00</th>
          <th>2017-02-01 00:30:00</th>
        </tr>
        <tr>
          <th>Human carcinogenic toxicity_source</th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_Other</th>
          <td>0.000446</td>
          <td>0.000442</td>
          <td>0.000435</td>
        </tr>
        <tr>
          <th>Biomass_AT</th>
          <td>0.000023</td>
          <td>0.000022</td>
          <td>0.000022</td>
        </tr>
        <tr>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Coal-derived_gas_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Gas_AT</th>
          <td>0.000132</td>
          <td>0.000126</td>
          <td>0.000122</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>Other_renewable_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Solar_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Waste_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Offshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Onshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
      </tbody>
    </table>
    <p>101 rows × 3 columns</p>
    </div>


.. parsed-literal::

    #############
    impacts for Fine particulate matter formation:



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>2017-02-01 00:00:00</th>
          <th>2017-02-01 00:15:00</th>
          <th>2017-02-01 00:30:00</th>
        </tr>
        <tr>
          <th>Fine particulate matter formation_source</th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_Other</th>
          <td>0.000010</td>
          <td>0.000010</td>
          <td>0.000010</td>
        </tr>
        <tr>
          <th>Biomass_AT</th>
          <td>0.000001</td>
          <td>0.000001</td>
          <td>0.000001</td>
        </tr>
        <tr>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Coal-derived_gas_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Gas_AT</th>
          <td>0.000006</td>
          <td>0.000006</td>
          <td>0.000005</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>Other_renewable_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Solar_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Waste_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Offshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Onshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
      </tbody>
    </table>
    <p>101 rows × 3 columns</p>
    </div>


.. parsed-literal::

    #############
    impacts for Land use:



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>2017-02-01 00:00:00</th>
          <th>2017-02-01 00:15:00</th>
          <th>2017-02-01 00:30:00</th>
        </tr>
        <tr>
          <th>Land use_source</th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_Other</th>
          <td>0.000192</td>
          <td>0.000191</td>
          <td>0.000188</td>
        </tr>
        <tr>
          <th>Biomass_AT</th>
          <td>0.001014</td>
          <td>0.000997</td>
          <td>0.000974</td>
        </tr>
        <tr>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Coal-derived_gas_AT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Fossil_Gas_AT</th>
          <td>0.000068</td>
          <td>0.000065</td>
          <td>0.000063</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>Other_renewable_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Solar_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Waste_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Offshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Wind_Onshore_IT</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
      </tbody>
    </table>
    <p>101 rows × 3 columns</p>
    </div>


Group per country
~~~~~~~~~~~~~~~~~

The following piece of code suggests a basic visualization of the
Climate Change category, grouping the results per country of origin of
the tracked electricity.

.. code:: ipython3

    def compute_per_country(results):
        """Function to group results per country"""
        countries = np.unique([c.split("_")[-1] for c in results.columns]) # List of countries
        
        per_country = []
        for c in countries:
            cols = [k for k in results.columns if k[-3:]==f"_{c}"]
            per_country.append(pd.Series(results.loc[:,cols].sum(axis=1), name=c))
            
        return pd.concat(per_country,axis=1)

.. code:: ipython3

    gwp_per_country = compute_per_country(impacts['Climate Change']) # Group Climate Change index impacts per country
    gwp_per_country.plot.area(figsize=(12,4), legend='reverse', color=['r','w','y','b','c','k'],
                              title="Some visualization of the GWP aggregated per country"); # Build the graph



.. image:: images/graph_CC_country.png


Group per production type
~~~~~~~~~~~~~~~~~~~~~~~~~

The following piece of code suggests a basic visualization of the
Climate Change category, grouping the results per technology of origin
of the tracked electricity.

.. code:: ipython3

    def compute_per_type(results):
        """Function to group datasets per type of unit, regardless of the country of origin"""
        unit_list = np.unique([k[:-3] if k[-3]=="_" else k for k in results.columns]) # List the different production units
        
        per_unit = []
        for u in unit_list:
            cols = [k for k in results.columns if k[:-3]==u] # collect the useful columns
            per_unit.append(pd.Series(results.loc[:,cols].sum(axis=1), name=u)) # aggregate
    
        return pd.concat(per_unit,axis=1)

.. code:: ipython3

    es13_per_type = compute_per_type(impacts['Climate Change']) # Group Climate Change index impacts per country
    es13_per_type.plot.area(figsize=(12,8), legend='reverse',
                            title="Some visualization of the Climate Change index aggregated per source"); # Build the graph



.. image:: images/graph_CC_source.png

