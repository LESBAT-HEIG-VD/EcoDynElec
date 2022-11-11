| 
| \ **Compute electric mix for all countries**\ 

DYNAMICAL allow to only compute the electric mix for all considered
countries at the time. These matrices are intermediate results in the
usual DYNAMICAL process. The functionality was added due to its
potential usefulness.

In technical words, a function ``get_inverted_matrix`` allow to retrieve
the invert of technology matrix :math:`(I-A)^{-1}`.

.. code:: ipython3

    from dynamical.easy_use import get_inverted_matrix # Import the function
    from parameter import Parameter # Import the parameter handler object

.. code:: ipython3

    # Configure parameter to reduce the number of time steps
    my_param = Parameter().from_excel("Spreadsheet_test.xlsx")
    my_param.start="2017-02-01 12:00"
    my_param.end="2017-02-01 14:00"
    my_param.freq = "H"

.. code:: ipython3

    mix = get_inverted_matrix(p=my_param)

.. code:: ipython3

    mix[0]




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
          <td>1.000034</td>
          <td>1.914997e-02</td>
          <td>1.385938e-04</td>
          <td>0.0</td>
          <td>0.000637</td>
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
          <td>0.001787</td>
          <td>1.003225e+00</td>
          <td>7.260626e-03</td>
          <td>0.0</td>
          <td>0.033385</td>
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
          <td>0.224013</td>
          <td>4.451191e-01</td>
          <td>1.003222e+00</td>
          <td>0.0</td>
          <td>0.014813</td>
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
          <td>0.007310</td>
          <td>2.377682e-01</td>
          <td>3.155733e-02</td>
          <td>1.0</td>
          <td>0.053205</td>
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
          <td>9.551584e-05</td>
          <td>6.912757e-07</td>
          <td>0.0</td>
          <td>1.000003</td>
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
          <td>0.000390</td>
          <td>7.458758e-06</td>
          <td>5.398119e-08</td>
          <td>0.0</td>
          <td>0.078089</td>
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
          <td>9.666313e-08</td>
          <td>6.995790e-10</td>
          <td>0.0</td>
          <td>0.001012</td>
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
          <td>0.000422</td>
          <td>8.089134e-06</td>
          <td>5.854340e-08</td>
          <td>0.0</td>
          <td>0.084689</td>
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
=============================================

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
==========================================================================

.. code:: ipython3

    group_by_family(mix[0].loc["Mix_Other":, :"Mix_IT"]) # 1st time step




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
          <td>0.485924</td>
          <td>0.030762</td>
          <td>0.261834</td>
          <td>0.097567</td>
          <td>0.123913</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.298574</td>
          <td>0.414085</td>
          <td>0.150002</td>
          <td>0.134030</td>
          <td>0.003309</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.593146</td>
          <td>0.136779</td>
          <td>0.030051</td>
          <td>0.237876</td>
          <td>0.002149</td>
        </tr>
        <tr>
          <th>Mix_FR</th>
          <td>0.128053</td>
          <td>0.713730</td>
          <td>0.093241</td>
          <td>0.064976</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Mix_IT</th>
          <td>0.665790</td>
          <td>0.046107</td>
          <td>0.095778</td>
          <td>0.192215</td>
          <td>0.000110</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

    group_by_family(mix[1].loc["Mix_Other":, :"Mix_IT"]) # 2nd time step




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
          <td>0.504585</td>
          <td>0.033245</td>
          <td>0.234267</td>
          <td>0.097192</td>
          <td>0.130710</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.293068</td>
          <td>0.411462</td>
          <td>0.165844</td>
          <td>0.128263</td>
          <td>0.001363</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.594173</td>
          <td>0.141458</td>
          <td>0.028400</td>
          <td>0.233368</td>
          <td>0.002600</td>
        </tr>
        <tr>
          <th>Mix_FR</th>
          <td>0.131565</td>
          <td>0.717227</td>
          <td>0.086283</td>
          <td>0.064926</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>Mix_IT</th>
          <td>0.664596</td>
          <td>0.051813</td>
          <td>0.110943</td>
          <td>0.172590</td>
          <td>0.000058</td>
        </tr>
      </tbody>
    </table>
    </div>



Visualize the origin per country (columns) in each country (index)
==================================================================

.. code:: ipython3

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
          <td>0.648382</td>
          <td>0.000568</td>
          <td>0.215232</td>
          <td>0.007310</td>
          <td>4.596044e-03</td>
          <td>0.123913</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.012416</td>
          <td>0.318747</td>
          <td>0.427671</td>
          <td>0.237768</td>
          <td>8.801108e-05</td>
          <td>0.003309</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.000090</td>
          <td>0.002307</td>
          <td>0.963897</td>
          <td>0.031557</td>
          <td>6.369617e-07</td>
          <td>0.002149</td>
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
          <td>0.000413</td>
          <td>0.010607</td>
          <td>0.014232</td>
          <td>0.053205</td>
          <td>9.214323e-01</td>
          <td>0.000110</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

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
          <td>0.636860</td>
          <td>0.001400</td>
          <td>0.218438</td>
          <td>0.009143</td>
          <td>3.448941e-03</td>
          <td>0.130710</td>
        </tr>
        <tr>
          <th>Mix_CH</th>
          <td>0.001058</td>
          <td>0.328765</td>
          <td>0.422783</td>
          <td>0.246025</td>
          <td>5.729576e-06</td>
          <td>0.001363</td>
        </tr>
        <tr>
          <th>Mix_DE</th>
          <td>0.000008</td>
          <td>0.002599</td>
          <td>0.957974</td>
          <td>0.036818</td>
          <td>4.530087e-08</td>
          <td>0.002600</td>
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
          <td>0.000045</td>
          <td>0.014004</td>
          <td>0.018009</td>
          <td>0.058283</td>
          <td>9.096001e-01</td>
          <td>0.000058</td>
        </tr>
      </tbody>
    </table>
    </div>


