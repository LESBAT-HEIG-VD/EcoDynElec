import os
import unittest

import pandas as pd

from ecodynelec import pipelines
from ecodynelec.parameter import Parameter


def generate_config():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config = Parameter()
    config.path.generation = os.path.join(parent_dir, "examples/test_data/generations/")
    config.path.exchanges = os.path.join(parent_dir, "examples/test_data/exchanges/")
    return config


def test_prod_mix_impact_result(tester, config, country, raw_prod_dict, prod_dict, mix_dict, prod_imp_dict, imp_dict):
    ## raw_prod_dict test
    ### Test the type
    tester.assertIsInstance(raw_prod_dict, pd.DataFrame, msg='raw_prod_dict is DataFrame')

    ## mix_dict test
    ### Test the type
    tester.assertIsInstance(prod_dict, pd.DataFrame, msg='prod_dict is DataFrame')
    tester.assertIsInstance(mix_dict, pd.DataFrame, msg='mix_dict is DataFrame')

    ## Test contents
    tester.assertIn('production', raw_prod_dict.columns, msg='production in raw_prod_dict columns')
    tester.assertIn('imports', raw_prod_dict.columns, msg='imports in raw_prod_dict columns')
    tester.assertIn('exports', raw_prod_dict.columns, msg='exports in raw_prod_dict columns')
    pd.testing.assert_index_equal(raw_prod_dict.index, prod_dict.index)
    pd.testing.assert_index_equal(raw_prod_dict.index, mix_dict.index)

    ## Impact dict test
    ### Test the type
    tester.assertIsInstance(prod_imp_dict, dict, msg='prod_imp_dict is dict')
    tester.assertIsInstance(imp_dict, dict, msg='imp_dict is dict')
    ### Test one key
    tester.assertIn('Global', prod_imp_dict, msg='prod_imp_dict global key')
    tester.assertIn('Global', imp_dict, msg='imp_dict global key')
    ### Test the type inside
    for k in imp_dict:
        tester.assertIsInstance(prod_imp_dict[k], pd.DataFrame, msg=f"prod_imp_dict {k} output is a DataFrame")
        tester.assertIsInstance(imp_dict[k], pd.DataFrame, msg=f"imp_dict {k} output is a DataFrame")
        pd.testing.assert_index_equal(prod_imp_dict[k].index, imp_dict[k].index)
        pd.testing.assert_index_equal(mix_dict.index, imp_dict[k].index)
    ### Test the shapes
    base = prod_imp_dict['Global'].shape
    tester.assertEqual(len(prod_imp_dict.keys()), 1 + base[1], msg='Correct number of keys')
    tester.assertTrue(all(prod_imp_dict[k].shape[0] == base[0] for k in prod_imp_dict), msg='Correct length of all tables')

    base = imp_dict['Global'].shape
    tester.assertEqual(len(imp_dict.keys()), 1 + base[1], msg='Correct number of keys')
    tester.assertTrue(all(imp_dict[k].shape[0] == base[0] for k in imp_dict), msg='Correct length of all tables')

class TestPipelines(unittest.TestCase):

    def test_mainExecute(self):
        config = generate_config()
        out = pipelines.execute(config=config)

        ### Test the type
        self.assertIsInstance(out, dict, msg='Is dict')

        ### Test one key
        self.assertIn('Global', out, msg='Global key')

        ### Test the type inside
        for k in out:
            self.assertIsInstance(out[k], pd.DataFrame, msg=f"{k} output is a DataFrame")

        ### Test the shapes
        base = out['Global'].shape

        self.assertEqual(len(out.keys()), 1 + base[1], msg='Correct number of keys')
        self.assertTrue(all(out[k].shape[0] == base[0] for k in out), msg='Correct length of all tables')

    def test_get_prod_mix_impacts_simple_target_fr(self):
        config = generate_config()
        config.target = 'FR'
        raw_prod_dict, prod_dict, mix_dict, prod_imp_dict, imp_dict = pipelines.get_prod_mix_impacts(config=config)
        test_prod_mix_impact_result(self, config, 'FR', raw_prod_dict, prod_dict, mix_dict, prod_imp_dict, imp_dict)

    def test_get_prod_mix_impacts_simple_target_ch_residual(self):
        config = generate_config()
        config.target = 'CH'
        config.residual_local = True
        raw_prod_dict, prod_dict, mix_dict, prod_imp_dict, imp_dict = pipelines.get_prod_mix_impacts(config=config)
        test_prod_mix_impact_result(self, config, 'CH', raw_prod_dict, prod_dict, mix_dict, prod_imp_dict, imp_dict)

    def test_get_prod_mix_impacts_multi_target(self):
        config = generate_config()
        config.target = ['CH', 'FR', 'DE']
        raw_prod_dicts, prod_dicts, mix_dicts, prod_imp_dicts, imp_dicts = pipelines.get_prod_mix_impacts(config=config)

        ### Test the types
        self.assertIsInstance(raw_prod_dicts, dict, msg='raw_prod_dicts is dict')
        self.assertIsInstance(mix_dicts, dict, msg='mix_dicts is dict')
        self.assertIsInstance(imp_dicts, dict, msg='imp_dicts is dict')

        ### Test the contents
        for target in config.target:
            test_prod_mix_impact_result(self, config, target, raw_prod_dicts[target], prod_dicts[target], mix_dicts[target], prod_imp_dicts[target], imp_dicts[target])

    def test_matrices(self):
        config = generate_config()
        out = pipelines.get_inverted_matrix(config=config)

        ### Test the type
        self.assertIsInstance(out, list, msg='Is list')

        ### Test the type inside
        self.assertTrue(all(isinstance(obj, pd.DataFrame) for obj in out), msg=f"Outputs are DataFrame")

        ### Test the shapes
        self.assertTrue( all( obj.shape[0]==obj.shape[1] for obj in out ), msg='Correct shape of all tables' )


#############
if __name__ == '__main__':
    res = unittest.main(verbosity=2)
