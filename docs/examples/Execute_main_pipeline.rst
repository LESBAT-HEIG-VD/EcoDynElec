Execution of DYNAMICAL
======================

``dynamical`` does combine all its functionalities within one pipeline
called ``execute`` in the module ``easy_use``. This pipeline requires
configuration information to be provided either as a spreadsheet or as a
``Parameter`` object. More details about how to handle the parameters in
the `appropriate page <https://dynamical.readthedocs.io/en/latest/examples/Handle_parameters.html>`__

Execution with configuration in a ``Parameter`` object
------------------------------------------------------

.. code:: ipython3

    from dynamical.easy_use import execute # Import function managing the whole execution
    from dynamical.parameter import Parameter # Import the parameter management function

.. code:: ipython3

    my_config = Parameter() # Initialize the configuration

The configuration can be set further directly in the script, this point
is covered in the `dedicated page <https://dynamical.readthedocs.io/en/latest/examples/Handle_parameters.html>`__. To trigger the process, run:

.. code:: ipython3

    impacts = execute(config=my_config, is_verbose=True) # Execute DYNAMICAL from a parameter object


.. parsed-literal::

    Load auxiliary datasets...
    Extraction of impact vector...
    	. Mix_Other / AT / CH / DE / FR / IT .
    Load generation data...
    	Generation data.
    Data loading: 0.04 sec..
    Memory usage table: 0.18 MB
    Get original resolutions: 0.07 sec.
    Extract raw generation: 0.13 sec.             
    	Extraction time: 0.24 sec.
    Correction of generation data:
    	1/4 - Gather missing values...
    	2/4 - Sort missing values...
    	3/4 - Fill missing values...
    	4/4 - Resample Generation data to H steps...
    Get and reduce importation data...
    	Cross-border flow data.
    Data loading: 0.03 sec..
    Memory usage table: 0.04 MB
    Get original resolutions: 0.08 sec.
    Extract raw import: 0.16 sec.             
    	Extraction time: 0.27 sec.
    Resample Exchanged energy to frequence H...
    Gather generation and importation...
    Import of data: 0.6 sec
    Importing information...
    Tracking origin of electricity...
    	compute for day 1/1   
    	Electricity tracking: 0.3 sec.
    
    Compute the electricity impacts...
    	Global...
    	GWP...
    	CED_renewable...
    	CED_non-renewable...
    	ES2013...
    Impact computation: 0.1 sec.
    Adapt timezone: UTC >> CET
    done.


Execution with configuration in a spreadsheet
---------------------------------------------

A blank template of the spreadsheet can be obtained on the `GitLab repository <https://gitlab.com/fledee/ecodyn/-/blob/main/examples/Spreadsheet_example.xlsx>`__.

.. code:: ipython3

    from dynamical.easy_use import execute # Import function managing the whole execution

.. code:: ipython3

    impacts = execute(config='./Spreadsheet_test.xlsx', is_verbose=True) # Execute DYNAMICAL from spreadsheet


.. parsed-literal::

    Load auxiliary datasets...
    Extraction of impact vector...
    	. Mix_Other / AT / CH / DE / FR / IT .
    Load generation data...
    	Generation data.
    Data loading: 0.04 sec..
    Memory usage table: 0.18 MB
    Get original resolutions: 0.07 sec.
    Extract raw generation: 0.13 sec.             
    	Extraction time: 0.24 sec.
    Correction of generation data:
    	1/4 - Gather missing values...
    	2/4 - Sort missing values...
    	3/4 - Fill missing values...
    	4/4 - Resample Generation data to H steps...
    Get and reduce importation data...
    	Cross-border flow data.
    Data loading: 0.03 sec..
    Memory usage table: 0.04 MB
    Get original resolutions: 0.08 sec.
    Extract raw import: 0.16 sec.             
    	Extraction time: 0.27 sec.
    Resample Exchanged energy to frequence H...
    Gather generation and importation...
    Import of data: 0.6 sec
    Importing information...
    Tracking origin of electricity...
    	compute for day 1/1   
    	Electricity tracking: 0.3 sec.
    
    Compute the electricity impacts...
    	Global...
    	GWP...
    	CED_renewable...
    	CED_non-renewable...
    	ES2013...
    Impact computation: 0.1 sec.
    Adapt timezone: UTC >> CET
    done.


Some visualization of the results
---------------------------------

.. code:: ipython3

    ### Display results freshly computed
    for i in impacts:
        print(f"\nimpacts for {i}:")
        display(impacts[i].head())


.. parsed-literal::

    
    impacts for Global:



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
          <th>GWP</th>
          <th>CED_renewable</th>
          <th>CED_non-renewable</th>
          <th>ES2013</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-02-01 01:00:00</th>
          <td>0.475649</td>
          <td>0.777949</td>
          <td>10.992808</td>
          <td>465.158738</td>
        </tr>
        <tr>
          <th>2017-02-01 02:00:00</th>
          <td>0.470155</td>
          <td>0.76846</td>
          <td>11.015709</td>
          <td>463.661202</td>
        </tr>
        <tr>
          <th>2017-02-01 03:00:00</th>
          <td>0.46185</td>
          <td>0.771668</td>
          <td>11.012554</td>
          <td>460.428265</td>
        </tr>
        <tr>
          <th>2017-02-01 04:00:00</th>
          <td>0.463395</td>
          <td>0.769319</td>
          <td>11.022931</td>
          <td>461.802047</td>
        </tr>
        <tr>
          <th>2017-02-01 05:00:00</th>
          <td>0.469739</td>
          <td>0.781601</td>
          <td>11.004952</td>
          <td>463.860547</td>
        </tr>
      </tbody>
    </table>
    </div>


.. parsed-literal::

    
    impacts for GWP:



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
          <th>GWP_source</th>
          <th>Mix_Other</th>
          <th>Biomass_AT</th>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <th>Fossil_Coal-derived_gas_AT</th>
          <th>Fossil_Gas_AT</th>
          <th>Fossil_Hard_coal_AT</th>
          <th>Fossil_Oil_AT</th>
          <th>Fossil_Oil_shale_AT</th>
          <th>Fossil_Peat_AT</th>
          <th>Geothermal_AT</th>
          <th>...</th>
          <th>Hydro_Run-of-river_and_poundage_IT</th>
          <th>Hydro_Water_Reservoir_IT</th>
          <th>Marine_IT</th>
          <th>Nuclear_IT</th>
          <th>Other_fossil_IT</th>
          <th>Other_renewable_IT</th>
          <th>Solar_IT</th>
          <th>Waste_IT</th>
          <th>Wind_Offshore_IT</th>
          <th>Wind_Onshore_IT</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-02-01 01:00:00</th>
          <td>0.007512</td>
          <td>0.000264</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.017306</td>
          <td>0.00539</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 02:00:00</th>
          <td>0.007258</td>
          <td>0.00025</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.016186</td>
          <td>0.005065</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 03:00:00</th>
          <td>0.007337</td>
          <td>0.000247</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.016635</td>
          <td>0.004947</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 04:00:00</th>
          <td>0.007272</td>
          <td>0.000235</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.014861</td>
          <td>0.004689</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 05:00:00</th>
          <td>0.006251</td>
          <td>0.000194</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.01288</td>
          <td>0.003937</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
      </tbody>
    </table>
    <p>5 rows × 101 columns</p>
    </div>


.. parsed-literal::

    
    impacts for CED_renewable:



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
          <th>CED_renewable_source</th>
          <th>Mix_Other</th>
          <th>Biomass_AT</th>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <th>Fossil_Coal-derived_gas_AT</th>
          <th>Fossil_Gas_AT</th>
          <th>Fossil_Hard_coal_AT</th>
          <th>Fossil_Oil_AT</th>
          <th>Fossil_Oil_shale_AT</th>
          <th>Fossil_Peat_AT</th>
          <th>Geothermal_AT</th>
          <th>...</th>
          <th>Hydro_Run-of-river_and_poundage_IT</th>
          <th>Hydro_Water_Reservoir_IT</th>
          <th>Marine_IT</th>
          <th>Nuclear_IT</th>
          <th>Other_fossil_IT</th>
          <th>Other_renewable_IT</th>
          <th>Solar_IT</th>
          <th>Waste_IT</th>
          <th>Wind_Offshore_IT</th>
          <th>Wind_Onshore_IT</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-02-01 01:00:00</th>
          <td>0.026286</td>
          <td>0.040472</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000361</td>
          <td>0.000703</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 02:00:00</th>
          <td>0.025399</td>
          <td>0.038214</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000337</td>
          <td>0.000661</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 03:00:00</th>
          <td>0.025675</td>
          <td>0.037797</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000347</td>
          <td>0.000646</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 04:00:00</th>
          <td>0.025448</td>
          <td>0.036051</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.00031</td>
          <td>0.000612</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 05:00:00</th>
          <td>0.021875</td>
          <td>0.029769</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000268</td>
          <td>0.000514</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
      </tbody>
    </table>
    <p>5 rows × 101 columns</p>
    </div>


.. parsed-literal::

    
    impacts for CED_non-renewable:



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
          <th>CED_non-renewable_source</th>
          <th>Mix_Other</th>
          <th>Biomass_AT</th>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <th>Fossil_Coal-derived_gas_AT</th>
          <th>Fossil_Gas_AT</th>
          <th>Fossil_Hard_coal_AT</th>
          <th>Fossil_Oil_AT</th>
          <th>Fossil_Oil_shale_AT</th>
          <th>Fossil_Peat_AT</th>
          <th>Geothermal_AT</th>
          <th>...</th>
          <th>Hydro_Run-of-river_and_poundage_IT</th>
          <th>Hydro_Water_Reservoir_IT</th>
          <th>Marine_IT</th>
          <th>Nuclear_IT</th>
          <th>Other_fossil_IT</th>
          <th>Other_renewable_IT</th>
          <th>Solar_IT</th>
          <th>Waste_IT</th>
          <th>Wind_Offshore_IT</th>
          <th>Wind_Onshore_IT</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-02-01 01:00:00</th>
          <td>0.16007</td>
          <td>0.001831</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.309504</td>
          <td>0.065046</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000001</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 02:00:00</th>
          <td>0.154668</td>
          <td>0.001728</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.289474</td>
          <td>0.061125</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000001</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 03:00:00</th>
          <td>0.15635</td>
          <td>0.00171</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.297508</td>
          <td>0.059702</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000001</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 04:00:00</th>
          <td>0.154968</td>
          <td>0.001631</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.265788</td>
          <td>0.056595</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000001</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 05:00:00</th>
          <td>0.133205</td>
          <td>0.001346</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.230344</td>
          <td>0.047517</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000001</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
      </tbody>
    </table>
    <p>5 rows × 101 columns</p>
    </div>


.. parsed-literal::

    
    impacts for ES2013:



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
          <th>ES2013_source</th>
          <th>Mix_Other</th>
          <th>Biomass_AT</th>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <th>Fossil_Coal-derived_gas_AT</th>
          <th>Fossil_Gas_AT</th>
          <th>Fossil_Hard_coal_AT</th>
          <th>Fossil_Oil_AT</th>
          <th>Fossil_Oil_shale_AT</th>
          <th>Fossil_Peat_AT</th>
          <th>Geothermal_AT</th>
          <th>...</th>
          <th>Hydro_Run-of-river_and_poundage_IT</th>
          <th>Hydro_Water_Reservoir_IT</th>
          <th>Marine_IT</th>
          <th>Nuclear_IT</th>
          <th>Other_fossil_IT</th>
          <th>Other_renewable_IT</th>
          <th>Solar_IT</th>
          <th>Waste_IT</th>
          <th>Wind_Offshore_IT</th>
          <th>Wind_Onshore_IT</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-02-01 01:00:00</th>
          <td>7.801099</td>
          <td>1.583757</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>10.487425</td>
          <td>3.006394</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000081</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 02:00:00</th>
          <td>7.537808</td>
          <td>1.495415</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>9.808716</td>
          <td>2.825166</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000076</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 03:00:00</th>
          <td>7.619788</td>
          <td>1.479087</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>10.080944</td>
          <td>2.759404</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000076</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 04:00:00</th>
          <td>7.552443</td>
          <td>1.410745</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>9.006135</td>
          <td>2.615809</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.000072</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>2017-02-01 05:00:00</th>
          <td>6.491804</td>
          <td>1.164931</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>7.805137</td>
          <td>2.196226</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.00006</td>
          <td>...</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
      </tbody>
    </table>
    <p>5 rows × 101 columns</p>
    </div>

