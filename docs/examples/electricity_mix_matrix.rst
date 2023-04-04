Compute electric mix for all countries
======================================

The main pipeline of EcoDynElec presented in tutorials
`1 <https://ecodynelec.readthedocs.io/en/latest/examples/with_python.html#execution>`__
and
`2 <https://ecodynelec.readthedocs.io/en/latest/examples/with_spreadsheet.html#execution>`__
only compute the electricity mix and impacts for one target country.

However EcoDynElec can compute the electric mix for all considered
countries, **all at once**. In facts, this information is an
intermediate result in the main pipeline. The feature of extracting this
intermediate result was added due to its potential usefulness. This
tutorial shows how.

In technical words, a function ``get_inverted_matrix`` allow to retrieve
the invert of technology matrix :math:`(I-A)^{-1}`.

.. code:: ipython3

    from ecodynelec.pipelines import get_inverted_matrix # Import the function
    from ecodynelec.parameter import Parameter # Import the parameter handler object

.. code:: ipython3

    # Configuration to reduce the number of time steps
    my_config = Parameter().from_excel("./Spreadsheet_example.xlsx")
    my_config.start="2017-02-01 12:00"
    my_config.end="2017-02-01 14:00" # Only 2 hours
    my_config.freq = "H" # Only in hourly time step
    my_config.path.generation = "./test_data/generations/" # Generation files
    my_config.path.exchanges = "./test_data/exchanges/" # Exchanges files

.. code:: ipython3

    # Execute the function
    mix = get_inverted_matrix(config=my_config)

The result is **one matrix per time step**, all stored in a ``list``.
Here is an overview of the first matrix, i.e. corresponding to the first
time step.

.. code:: ipython3

    display(mix[0])



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
          <th>Mix_AT</th>
          <th>Mix_CH</th>
          <th>Mix_DE</th>
          <th>Mix_FR</th>
          <th>Mix_IT</th>
          <th>Mix_Other</th>
          <th>Biomass_AT</th>
          <th>Fossil_Brown_coal/Lignite_AT</th>
          <th>Fossil_Coal-derived_gas_AT</th>
          <th>Fossil_Gas_AT</th>
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
          <th>Mix_AT</th>
          <td>1.000053</td>
          <td>2.964993e-02</td>
          <td>2.145851e-04</td>
          <td>0.0</td>
          <td>0.000990</td>
          <td>0.0</td>
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
          <th>Mix_CH</th>
          <td>0.001788</td>
          <td>1.003252e+00</td>
          <td>7.260827e-03</td>
          <td>0.0</td>
          <td>0.033487</td>
          <td>0.0</td>
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
          <th>Mix_DE</th>
          <td>0.224020</td>
          <td>4.487106e-01</td>
          <td>1.003247e+00</td>
          <td>0.0</td>
          <td>0.014977</td>
          <td>0.0</td>
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
          <th>Mix_FR</th>
          <td>0.007299</td>
          <td>2.315305e-01</td>
          <td>3.151219e-02</td>
          <td>1.0</td>
          <td>0.053158</td>
          <td>0.0</td>
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
          <th>Mix_IT</th>
          <td>0.004988</td>
          <td>1.478873e-04</td>
          <td>1.070303e-06</td>
          <td>0.0</td>
          <td>1.000005</td>
          <td>0.0</td>
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
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>Other_renewable_IT</th>
          <td>0.000000</td>
          <td>0.000000e+00</td>
          <td>0.000000e+00</td>
          <td>0.0</td>
          <td>0.000000</td>
          <td>0.0</td>
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
          <th>Solar_IT</th>
          <td>0.000418</td>
          <td>1.237887e-05</td>
          <td>8.958943e-08</td>
          <td>0.0</td>
          <td>0.083705</td>
          <td>0.0</td>
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
          <td>1.0</td>
          <td>0.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>Waste_IT</th>
          <td>0.000005</td>
          <td>1.539660e-07</td>
          <td>1.114296e-09</td>
          <td>0.0</td>
          <td>0.001041</td>
          <td>0.0</td>
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
          <td>1.0</td>
          <td>0.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>Wind_Offshore_IT</th>
          <td>0.000000</td>
          <td>0.000000e+00</td>
          <td>0.000000e+00</td>
          <td>0.0</td>
          <td>0.000000</td>
          <td>0.0</td>
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
          <th>Wind_Onshore_IT</th>
          <td>0.000417</td>
          <td>1.236860e-05</td>
          <td>8.951514e-08</td>
          <td>0.0</td>
          <td>0.083636</td>
          <td>0.0</td>
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
          <td>1.0</td>
        </tr>
      </tbody>
    </table>
    <p>106 rows × 106 columns</p>
    </div>


Build function to condense and visualize data
---------------------------------------------

.. code:: ipython3

    import numpy as np # need numpy functions 
    import pandas as pd # need pandas functions

.. code:: ipython3

    def group_by_family(matrix):
        families = {'Fossil':['Fossil_Brown_coal/Lignite', 'Fossil_Coal-derived_gas',
                              'Fossil_Gas', 'Fossil_Hard_coal', 'Fossil_Oil', 'Fossil_Oil_shale',
                              'Fossil_Peat','Other_fossil'],
                    'Nuclear':['Nuclear'],
                    'Hydro':['Hydro_Pumped_Storage','Hydro_Run-of-river_and_poundage',
                             'Hydro_Water_Reservoir', 'Marine'],
                    'Other Renwable':['Biomass', 'Geothermal', 'Other_renewable',
                                      'Solar', 'Waste', 'Wind_Offshore', 'Wind_Onshore'],
                    'External imports':['Mix']}
        
        per_family = []
        for f in families:
            idx = [k for k in matrix.index if "_".join(k.split("_")[:-1]) in families[f]]
            per_family.append(pd.Series(matrix.loc[idx].sum(), name=f))
        return pd.concat(per_family, axis=1)
    
    
    def group_per_country(matrix):
        """Function to group datasets per country"""
        countries = np.unique([k.split("_")[-1] for k in matrix.index])
        
        per_country = []
        for c in countries:
            idx = [k for k in matrix.index if k.split("_")[-1]==c]
            per_country.append(pd.Series(matrix.loc[idx].sum(), name=c))
            
        return pd.concat(per_country,axis=1)

Visualize the origin per production type (columns) in each country (index)
--------------------------------------------------------------------------

.. code:: ipython3

    # Visualize table grouped by type of plant for 1st time step
    group_by_family(mix[0].loc["Mix_Other":, :"Mix_IT"])




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
          <th>Fossil</th>
          <th>Nuclear</th>
          <th>Hydro</th>
          <th>Other Renwable</th>
          <th>External imports</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_AT</th>
          <td>0.485921</td>
          <td>0.030766</td>
          <td>0.261810</td>
          <td>0.097588</td>
          <td>0.123915</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.303191</td>
          <td>0.415665</td>
          <td>0.141009</td>
          <td>0.135522</td>
          <td>0.004613</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.593127</td>
          <td>0.136792</td>
          <td>0.030061</td>
          <td>0.237861</td>
          <td>0.002158</td>
        </tr>
        <tr>
          <th>Mix_FR</th>
          <td>0.126312</td>
          <td>0.713809</td>
          <td>0.095752</td>
          <td>0.064128</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Mix_IT</th>
          <td>0.666016</td>
          <td>0.046303</td>
          <td>0.090563</td>
          <td>0.196964</td>
          <td>0.000154</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

    # Visualize table grouped by type of plant for 2st time step
    group_by_family(mix[1].loc["Mix_Other":, :"Mix_IT"])




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
          <th>Fossil</th>
          <th>Nuclear</th>
          <th>Hydro</th>
          <th>Other Renwable</th>
          <th>External imports</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_AT</th>
          <td>0.504558</td>
          <td>0.033226</td>
          <td>0.234255</td>
          <td>0.097251</td>
          <td>0.130711</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.291884</td>
          <td>0.413615</td>
          <td>0.163239</td>
          <td>0.129777</td>
          <td>0.001485</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.594143</td>
          <td>0.141349</td>
          <td>0.028476</td>
          <td>0.233432</td>
          <td>0.002601</td>
        </tr>
        <tr>
          <th>Mix_FR</th>
          <td>0.130971</td>
          <td>0.713597</td>
          <td>0.089035</td>
          <td>0.066397</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Mix_IT</th>
          <td>0.659795</td>
          <td>0.051923</td>
          <td>0.104881</td>
          <td>0.183339</td>
          <td>0.000063</td>
        </tr>
      </tbody>
    </table>
    </div>



Visualize the origin per country (columns) in each country (index)
------------------------------------------------------------------

.. code:: ipython3

    # Visualize table grouped by country for 1st time step
    group_per_country(mix[0].loc["Mix_Other":, :"Mix_IT"]) # 1st time step




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
          <th>AT</th>
          <th>CH</th>
          <th>DE</th>
          <th>FR</th>
          <th>IT</th>
          <th>Other</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_AT</th>
          <td>0.648394</td>
          <td>0.000558</td>
          <td>0.215238</td>
          <td>0.007299</td>
          <td>4.594943e-03</td>
          <td>0.123915</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.019224</td>
          <td>0.313375</td>
          <td>0.431122</td>
          <td>0.231531</td>
          <td>1.362325e-04</td>
          <td>0.004613</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.000139</td>
          <td>0.002268</td>
          <td>0.963922</td>
          <td>0.031512</td>
          <td>9.859542e-07</td>
          <td>0.002158</td>
        </tr>
        <tr>
          <th>Mix_FR</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>1.000000</td>
          <td>0.000000e+00</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Mix_IT</th>
          <td>0.000642</td>
          <td>0.010460</td>
          <td>0.014390</td>
          <td>0.053158</td>
          <td>9.211959e-01</td>
          <td>0.000154</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

    # Visualize table grouped by country for 2nd time step
    group_per_country(mix[1].loc["Mix_Other":, :"Mix_IT"]) # 2nd time step




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
          <th>AT</th>
          <th>CH</th>
          <th>DE</th>
          <th>FR</th>
          <th>IT</th>
          <th>Other</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Mix_AT</th>
          <td>0.636863</td>
          <td>0.001394</td>
          <td>0.218425</td>
          <td>0.009160</td>
          <td>3.447687e-03</td>
          <td>0.130711</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.001698</td>
          <td>0.327280</td>
          <td>0.419678</td>
          <td>0.249849</td>
          <td>9.194443e-06</td>
          <td>0.001485</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.000013</td>
          <td>0.002588</td>
          <td>0.957950</td>
          <td>0.036848</td>
          <td>7.269581e-08</td>
          <td>0.002601</td>
        </tr>
        <tr>
          <th>Mix_FR</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>1.000000</td>
          <td>0.000000e+00</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Mix_IT</th>
          <td>0.000073</td>
          <td>0.013993</td>
          <td>0.017943</td>
          <td>0.058663</td>
          <td>9.092658e-01</td>
          <td>0.000063</td>
        </tr>
      </tbody>
    </table>
    </div>


