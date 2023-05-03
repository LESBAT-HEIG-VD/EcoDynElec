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
        mix_dict = pipeline_functions.get_mix(parameters=config, raw_prod_exch=raw_prod_exch, sg_data=None, prod_gap=None)
        
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
        
        
    def test_get_productions(self):
        # needs to be tested with fake data and a local residual
        pass


#############
if __name__ == '__main__':
    res = unittest.main(verbosity=2)
