import unittest
import os
import numpy as np
import pandas as pd

from ecodynelec.preprocessing import loading


class TestLoading(unittest.TestCase):
    
    def test_inferPaths(self):
        
        ### No path given -> error
        self.assertRaises(KeyError, loading._infer_paths, path_prep=None, path_raw=None,)
        
        ### Path raw only -> path = path_raw, savegen=None
        path, savegen = loading._infer_paths(path_prep=None, path_raw="Path")
        self.assertTrue( (path=='Path')&(savegen is None) )
        
        ### Path prep only -> path = path_prep, savegen=None
        path, savegen = loading._infer_paths(path_prep="Path", path_raw=None)
        self.assertTrue( (path=='Path')&(savegen is None) )
        
        ### Both -> path=path_raw, savegen=path_prep
        path, savegen = loading._infer_paths(path_prep="Safe", path_raw="Path")
        self.assertTrue( (path=='Path')&(savegen=='Safe') )
        
        
    def test_resampling(self):
        data = pd.DataFrame({k: pd.Series(1, index=pd.date_range("2020", end='2020-12-31 23:45', freq=k))
                             for k in ['15T','H','D','MS']}) # Data with missing due to different frequencies
        
        ### Test the resampling for short frequencies
        for freq in ['15T','H','D']:
            out = loading.resample_data({'Ctry':data}, freq=freq)['Ctry'] # compute the resampling
            self.assertTrue( np.all(out == 1/loading.get_steps_per_hour(freq, dtype=float)),
                             msg=f"Resampling short {freq}")
        
        ### Test the resampling for long frequencies (via Months)
        possible_months = 24*np.arange(28,32) # Possible values (i.e. # hours per month)
        out = loading.resample_data({'Ctry':data}, freq="MS")['Ctry'] # compute the resampling
        # Test if values are all acceptable
        self.assertTrue( all([v in possible_months for v in np.unique(out.values.ravel())]),
                         msg=f"Resampling long authorized values")
        # Test if all months return the same value for different initial frequencies
        self.assertTrue( np.all(out.T.apply(lambda x: np.all(x==x.mean()))) )
        
    
    def test_netExchanges(self):
        ### Computing the function for symplistic case
        A = pd.DataFrame({"Mix_B_A": [4,3]})
        B = pd.DataFrame({"Mix_A_B": [3,4]})
        out = loading.create_net_exchange({"A":A,"B":B})
        
        ### Compare with expected result
        expected = np.array([[1,0],[0,1]])
        self.assertTrue( np.all(pd.concat(out, axis=1).values == expected) )
        
        
    def test_adjust_exchanges(self):
        # Data of 1s, containing the Country, 2 Neighbours (to sum up) and 1 Far country (to ignore)
        data = {'Ctry':pd.DataFrame(1, index=pd.date_range("2020",freq='H',periods=2),
                                    columns=["Ctry",'Nbr1','Nbr2','Far1'])}

        neighbour = ['Ctry','Nbr1','Nbr2'] # Ignore far country. Include Ctry, as in code

        # Verifications
        out = loading.adjust_exchanges(data, neighbour)['Ctry']
        expected = np.array([[1,2]]*2)
        exp_titles = pd.Index([f'Mix_{k}_Ctry' for k in ('Ctry','Other')])
        self.assertTrue( np.all(out.values==expected), msg='Correct shape and values' )
        self.assertTrue( np.all(out.columns==exp_titles), msg='Correct column names' )
        
        
    def test_importExchange(self):
        path_parent = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )
        pathdir = os.path.join(path_parent, "examples/test_data/prepared/") # Dir with example files
        expected = pd.read_csv(os.path.join(pathdir,"ExchTest_MW.csv"), index_col=0, parse_dates=True)
        
        ### Test the error for missing file
        self.assertRaises(KeyError, loading.import_exchanges,
                          ctry=['Error'], start=None, end=None, path_prep=pathdir)
        
        ### Test the import
        out = loading.import_exchanges(ctry=['Exch'], start=None, end=None, path_prep=pathdir)
        # Dict with right key
        self.assertTrue( isinstance(out, dict) )
        self.assertTrue('Exch' in out.keys(), msg='Correct keys')
        
        # Content is conform
        self.assertTrue(out['Exch'].index.inferred_type == 'datetime64', msg='Correct index type')
        self.assertTrue(np.all(out['Exch'].index==expected.index), msg='Correct indexes')
        self.assertTrue(np.all(out['Exch']==expected), msg='Correct content')
        
        
    def test_importGeneration(self):
        path_parent = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )
        pathdir = os.path.join(path_parent, "examples/test_data/prepared/") # Dir with example files
        expected = pd.read_csv(os.path.join(pathdir,"ProdTest_MW.csv"), index_col=0, parse_dates=True)
        expected.columns = [f"Plant{k+1}_Prod" for k in range(3)] + ["Other_fossil_Prod"]
        
        ### Test the error for missing file
        self.assertRaises(KeyError, loading.import_generation,
                          ctry=['Error'], start=None, end=None, path_prep=pathdir)
        
        ### Test the import
        out = loading.import_generation(ctry=['Prod'], start=None, end=None, path_prep=pathdir)
        # Dict with right key
        self.assertTrue( isinstance(out, dict) )
        self.assertTrue('Prod' in out.keys(), msg='Correct keys')
        
        # Content is conform
        self.assertTrue(out['Prod'].index.inferred_type == 'datetime64', msg='Correct index type')
        self.assertTrue(np.all(out['Prod'].index==expected.index), msg='Correct indexes')
        self.assertTrue(np.all(out['Prod'].columns==expected.columns), msg='Correct columns')
        
        self.assertTrue(np.all(out['Prod'].values==expected.values), msg='Correct content')



        

#############
if __name__=='__main__':
    res = unittest.main(verbosity=2)
