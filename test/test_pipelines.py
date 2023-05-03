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

def test_prod_mix_impact_result(tester, raw_prod_dict, mix_dict, imp_dict):
    ## raw_prod_dict test
    ### Test the type
    tester.assertIsInstance(raw_prod_dict, pd.DataFrame, msg='raw_prod_dict is DataFrame')

    ## mix_dict test
    ### Test the type
    tester.assertIsInstance(mix_dict, pd.DataFrame, msg='mix_dict is DataFrame')

    ## Test contents
    pd.testing.assert_index_equal(raw_prod_dict.index, mix_dict.index)
    [tester.assertIn(c, mix_dict.columns, msg=f"{c} in mix_dict columns") for c in raw_prod_dict.columns]

    ## Impact dict test
    ### Test the type
    tester.assertIsInstance(imp_dict, dict, msg='imp_dict is dict')
    ### Test one key
    tester.assertIn('Global', imp_dict, msg='imp_dict global key')
    ### Test the type inside
    for k in imp_dict:
        tester.assertIsInstance(imp_dict[k], pd.DataFrame, msg=f"imp_dict {k} output is a DataFrame")
    ### Test the shapes
    base = imp_dict['Global'].shape
    tester.assertEqual(len(imp_dict.keys()), 1 + base[1], msg='Correct number of keys')
    tester.assertTrue(all(imp_dict[k].shape[0] == base[0] for k in imp_dict), msg='Correct length of all tables')
    pd.testing.assert_index_equal(mix_dict.index, imp_dict['Global'].index)

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
        raw_prod_dict, mix_dict, imp_dict = pipelines.get_prod_mix_impacts(config=config)
        test_prod_mix_impact_result(self, raw_prod_dict, mix_dict, imp_dict)

    def test_get_prod_mix_impacts_simple_target_ch_residual(self):
        config = generate_config()
        config.target = 'CH'
        config.residual_local = True
        raw_prod_dict, mix_dict, imp_dict = pipelines.get_prod_mix_impacts(config=config)
        test_prod_mix_impact_result(self, raw_prod_dict, mix_dict, imp_dict)

    def test_get_prod_mix_impacts_multi_target(self):
        config = generate_config()
        config.target = ['CH', 'FR', 'DE']
        raw_prod_dicts, mix_dicts, imp_dicts = pipelines.get_prod_mix_impacts(config=config)

        ### Test the types
        self.assertIsInstance(raw_prod_dicts, dict, msg='raw_prod_dicts is dict')
        self.assertIsInstance(mix_dicts, dict, msg='mix_dicts is dict')
        self.assertIsInstance(imp_dicts, dict, msg='imp_dicts is dict')

        ### Test the contents
        for target in config.target:
            test_prod_mix_impact_result(self, raw_prod_dicts[target], mix_dicts[target], imp_dicts[target])

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
