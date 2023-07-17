import os
import unittest

import pandas as pd

from ecodynelec import pipeline_functions
from ecodynelec.parameter import Parameter
from test.test_tracking import generate_table


def generate_config():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config = Parameter()
    config.path.generation = os.path.join(parent_dir, "examples/test_data/generations/")
    config.path.exchanges = os.path.join(parent_dir, "examples/test_data/exchanges/")
    config.ctry = ['CH', 'FR', 'DE']
    return config

def generate_table():
    columns = ['Plant_CH', 'Mix_CH_CH', 'Mix_FR_CH', 'Mix_DE_CH', 'Mix_Other_CH',
               'Plant_FR', 'Mix_FR_FR', 'Mix_CH_FR', 'Mix_DE_FR', 'Mix_Other_FR',
               'Plant_DE', 'Mix_DE_DE', 'Mix_CH_DE', 'Mix_FR_DE', 'Mix_Other_DE']
    df = pd.DataFrame(0, index=range(3), columns=columns)
    df.loc[:, f'Plant_CH'] = 1
    df.loc[:, f'Plant_FR'] = 1
    df.loc[:, f'Mix_CH_CH'] = [6, 0, 0]
    df.loc[:, f'Mix_FR_FR'] = [0, 6, 0]
    df.loc[:, f'Mix_Other_CH'] = 3
    df.loc[:, f'Mix_Other_FR'] = 3
    df.loc[:, f'Plant_DE'] = 0.8
    df.loc[:, f'Mix_DE_DE'] = [0, 0, 6]
    df.loc[:, f'Mix_Other_DE'] = 2

    df.loc[:, f'Mix_FR_CH'] = 0.14
    df.loc[:, f'Mix_DE_CH'] = 0.25
    df.loc[:, f'Mix_FR_DE'] = 0.12

    return df

class TestPipelineFunctions(unittest.TestCase):
    
    def test_load_raw_prod_exchanges(self):
        config = generate_config()
        config.residual_global = True # will load prod_gap and sg_data
        raw_prod_exch, prod_gap, sg_data = pipeline_functions.load_raw_prod_exchanges(parameters=config)
        
        ### Test the types
        self.assertIsInstance(raw_prod_exch, pd.DataFrame, msg='raw_prod_exch is DataFrame')
        self.assertIsInstance(prod_gap, pd.DataFrame, msg='prod_gap is DataFrame')
        self.assertIsInstance(sg_data, pd.DataFrame, msg='sg_data is DataFrame')
        
        # Test of the contents are covered by test_loading.py and test_auxiliary.py

    def test_get_mix_dict(self):
        config = generate_config()
        config.target = ['CH', 'FR']
        # not covered yet config.residual_local = True
        raw_prod_exch = generate_table()
        mix_dict = pipeline_functions.get_mix(parameters=config, raw_prod_exch=raw_prod_exch)

        ### Test the type
        self.assertIsInstance(mix_dict, dict, msg='mix_dict is dict')
        self.assertIn('CH', mix_dict, msg='mix_dict CH key')
        self.assertIn('FR', mix_dict, msg='mix_dict FR key')
        self.assertIsInstance(mix_dict['CH'], pd.DataFrame, msg='mix_dict CH output is a DataFrame')
        
        ### Test the contents
        pd.testing.assert_index_equal(raw_prod_exch.index, mix_dict['CH'].index)
        pd.testing.assert_index_equal(mix_dict['CH'].index, mix_dict['FR'].index)
        pd.testing.assert_index_equal(mix_dict['CH'].columns, mix_dict['FR'].columns)
        # not covered yet self.assertIn('Residual_Other_CH', mix_dict['CH'].columns, msg='Residual_Other_CH in mix_dict CH columns')
    
    def test_get_mix_matrix(self):
        config = generate_config()
        raw_prod_exch = generate_table()
        mix_matrix = pipeline_functions.get_mix(parameters=config, raw_prod_exch=raw_prod_exch, return_matrix=True)
        
        ### Test the type
        self.assertIsInstance(mix_matrix, list, msg='mix_matrix is list')
        self.assertIsInstance(mix_matrix[0], pd.DataFrame, msg='mix_matrix content are DataFrames')

        ### Test the contents
        pd.testing.assert_index_equal(mix_matrix[0].index, mix_matrix[0].columns)
        pd.testing.assert_index_equal(mix_matrix[0].index, mix_matrix[1].index)
        pd.testing.assert_index_equal(mix_matrix[0].columns, mix_matrix[1].columns)

        # not covered yet self.assertNotIn('Residual_Other_CH', mix_matrix[0].columns, msg='Residual_Other_CH not in mix_matrix columns')


    def test_prod_mix_and_mix_to_kwh(self):
        config = generate_config()
        raw_prod_exch = generate_table()
        prod_mix, cons_mix= pipeline_functions.get_mix(parameters=config, raw_prod_exch=raw_prod_exch, return_matrix=False, return_prod_mix=True)
        country = config.target[0]
        prod_df = prod_mix[country]
        mix_df = cons_mix[country]

        # Drop non-production lines of the mix (i.e. the first part of the mix matrix)
        prod_df = prod_df.drop(
            prod_df.loc[:,
            [k.startswith('Mix') and not k.endswith('Other') for k in prod_df.columns]],
            axis=1).astype('float32')
        prod_df = prod_df / prod_df.sum(axis=1).values.reshape(-1, 1)
        mix_df = mix_df.drop(
            mix_df.loc[:, [k.startswith('Mix') and not k.endswith('Other') for k in mix_df.columns]],
            axis=1).astype('float32')

        flows_dict = {'production': pd.Series(index=mix_df.index, data=1000.0), 'imports': pd.Series(index=mix_df.index, data=500.0), 'exports': pd.Series(index=mix_df.index, data=100.0)}
        flows_df = pd.DataFrame.from_dict(flows_dict)

        # Test production kwh calculation
        kwh = pipeline_functions.get_producing_mix_kwh(flows_df=flows_df, prod_mix_df=prod_df)
        ### Test the type
        self.assertIsInstance(kwh, pd.DataFrame, msg='kwh is DataFrame')
        ### Test the contents
        pd.testing.assert_index_equal(mix_df.index, kwh.index)
        pd.testing.assert_series_equal(kwh.sum(axis=1), flows_df['production'], check_names=False)
        [self.assertIn(c, mix_df.columns, msg=f'{c} in mix_dict columns') for c in kwh.columns if
         not c.startswith('Mix_')]  # Check that prod columns are in mix_dict

        # Test production + imports - exports kwh calculation
        kwh = pipeline_functions.get_consuming_mix_kwh(flows_df=flows_df, mix_df=mix_df)
        ### Test the type
        self.assertIsInstance(kwh, pd.DataFrame, msg='kwh is DataFrame')
        ### Test the contents
        pd.testing.assert_index_equal(mix_df.index, kwh.index)
        pd.testing.assert_series_equal(kwh.sum(axis=1), flows_df['production']+flows_df['imports']-flows_df['exports'], check_names=False)
        [self.assertIn(c, mix_df.columns, msg=f'{c} in mix_dict columns') for c in kwh.columns if
         not c.startswith('Mix_')]  # Check that prod columns are in mix_dict
        [self.assertIn(f'Plant_{c}', kwh.columns, msg=f'Mix_{c}_{country} in raw_prod_dict columns') for
         c in config.ctry if c != country]  # Check that import columns are in raw_prod_dict
        self.assertIn(f'Mix_Other', kwh.columns, msg='Mix_Other in raw_prod_dict columns')


    def test_get_productions(self):
        # needs to be tested with fake data and a local residual
        pass


#############
if __name__ == '__main__':
    res = unittest.main(verbosity=2)
