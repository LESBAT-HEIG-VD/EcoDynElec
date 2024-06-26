import unittest

import numpy as np
import pandas as pd
from pandas import DataFrame, MultiIndex

from ecodynelec import tracking
from ecodynelec.tracking import compute_producing_mix


def generate_table():
    columns = ['Plant_C1', 'Mix_C1_C1', 'Mix_C2_C1', 'Mix_Other_C1',
               'Plant_C2', 'Mix_C2_C2', 'Mix_C1_C2', 'Mix_Other_C2']

    df = pd.DataFrame(0, index=range(2), columns=columns)
    df.loc[:, f'Plant_C1'] = 1
    df.loc[:, f'Plant_C2'] = 1

    df.loc[:, f'Mix_C1_C1'] = [6, 0]
    df.loc[:, f'Mix_C2_C2'] = [0, 6]

    df.loc[:, f'Mix_Other_C1'] = 3
    df.loc[:, f'Mix_Other_C2'] = 3

    return df


class TestTracking(unittest.TestCase):

    def test_reorderInfo(self):
        expected = (['C1', 'C2'],
                    ['C1', 'C2', 'Other'],
                    ['Plant', 'Mix_C1', 'Mix_C2', 'Mix_Other'],
                    ['Mix_C1', 'Mix_C2', 'Mix_Other', 'Plant_C1', 'Plant_C2'])

        df = generate_table()
        out = tracking.reorder_info(df)

        for i, name in enumerate(['Country', 'Ctry Mix', 'Prod Mix', 'All elements']):
            self.assertTrue(out[i] == expected[i], msg=f"Reorder {name}")

    def test_buildTechMatrix(self):
        expected = [np.concatenate([np.array(vec).reshape(5, 2), np.zeros((5, 3))], axis=1)
                    for vec in ([.6, 0, 0, 0, .3, .75, .1, 0, 0, .25], [0, .6, 0, 0, .75, .3, .25, 0, 0, .1],)]

        df = generate_table()
        ctry, ctry_mix, prod_means, all_sources = tracking.reorder_info(df)  # Labels
        df_mix = compute_producing_mix(df, ctry=ctry, prod_means=prod_means)
        # the '2*' indicates the number of countries (C1 and C2)
        self.assertTrue(np.all(df_mix.sum(axis=1).values == 2*np.ones(df_mix.shape[0])), msg='Valid prod mix matrix')

        out = [tracking.build_technology_matrix(df_mix.iloc[i], ctry, ctry_mix, prod_means).round(2)
               for i in range(2)]

        self.assertTrue(np.all([np.all(out[i] == expected[i]) for i in range(2)]),
                        msg='Valid content Tech Matrix')

    def test_cleanTechMatrix(self):
        A = np.ones((4, 4))
        A[2, :] = A[:, 2] = 0
        out = tracking.clean_technology_matrix(A)

        self.assertTrue(np.all(out[0] == np.ones((3, 3))),
                        msg="Values in lighter tech matrix")
        self.assertTrue(np.all(out[1] == np.array([0, 1, 3])),
                        msg="Indexes registered to reduce tech matrix")

    def test_invertTechMatrix(self):
        expected = [np.array([-2, 1, 1.5, -.5]).reshape((2, 2)),
                    np.array([-2, 0, 1, 0, 0, 0, 1.5, 0, -.5]).reshape((3, 3))]

        A = -np.array([[0, 2], [3, 3]])
        out = [tracking.invert_technology_matrix(A, presence=[0, 1 + i], L=2 + i)
               for i in range(2)]

        self.assertTrue(np.all([np.all(out[i].round(2) == expected[i].round(2)) for i in range(2)]),
                        msg="Values when inverting Tech Matrix")

    def test_setFU(self):
        all_sources = ['Mix_C1', 'Mix_C2', 'Mix_Other', 'Plant_C1', 'Plant_C2']
        expected = np.eye(3, 5)
        out = np.array([tracking.set_FU_vector(all_sources, target=k)
                        for k in ['C1', 'C2', 'Other']])

        self.assertTrue(np.all(out == expected), msg='Conform FU vector')

    def test_computeTracking(self):
        df = generate_table()
        ctry = ['C1', 'C2']
        ctry_mix = ctry + ['Other']
        prod_means = ['Plant', 'Mix_C1', 'Mix_C2', 'Mix_Other']
        all_sources = ['Mix_C1', 'Mix_C2', 'Mix_Other', 'Plant_C1', 'Plant_C2']
        Up = pd.Series(1, index=range(2))
        df_mix = compute_producing_mix(df, ctry=ctry, prod_means=prod_means)

        expected = [pd.DataFrame(np.array(vec).reshape(2, 5), columns=all_sources).astype('float32')
                    for vec in
                    ([2.5, 0., .75, .25, 0., 1, 0., .75, .25, 0., ], [0., 1, .75, 0., .25, .6, 1, .75, .15, .1, ])]
        expectM = [pd.DataFrame(np.concatenate([np.array(vec).reshape(5, 2), np.zeros((5, 3))], axis=1)
                                + np.eye(5), index=all_sources, columns=all_sources).astype('float32')
                   for vec in
                   ([1.5, .0, .0, .0, .75, .75, .25, .0, .0, .25], [.0, .6, .0, .0, .75, .75, .25, .15, .0, .1])]

        ### Check the matrix extraction
        out = tracking.compute_tracking(df_mix, all_sources, uP=Up, ctry=ctry, ctry_mix=ctry_mix,
                                        prod_means=prod_means)

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
