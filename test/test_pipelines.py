import os
import unittest

from pandas import MultiIndex
from pandas.core.frame import DataFrame

from ecodynelec import pipelines
from ecodynelec.parameter import Parameter


def generate_config():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config = Parameter()
    config.path.generation = os.path.join(parent_dir, "examples/test_data/generations/")
    config.path.exchanges = os.path.join(parent_dir, "examples/test_data/exchanges/")
    return config


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
            self.assertIsInstance(out[k], DataFrame, msg=f"{k} output is a DataFrame")

        ### Test the shapes
        base = out['Global'].shape

        self.assertEqual(len(out.keys()), 1 + base[1], msg='Correct number of keys')
        self.assertTrue(all(out[k].shape[0] == base[0] for k in out), msg='Correct length of all tables')

    def test_matrices(self):
        config = generate_config()
        out = pipelines.get_inverted_matrix(config=config)

        ### Test the type
        self.assertIsInstance(out, DataFrame, msg='Is DataFrame')

        ### Test the index
        self.assertIsInstance(out.index, MultiIndex, msg='Has MultiIndex')
        self.assertTrue(out.index.nlevels == 2, msg=f"Index has two levels")

        ### Test the shapes
        self.assertTrue(out.index.levshape[1] == len(out.columns), msg='Correct shape of all tables')


#############
if __name__ == '__main__':
    res = unittest.main(verbosity=2)
