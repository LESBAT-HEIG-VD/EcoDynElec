import unittest
import os
import numpy as np
import pandas as pd

from dynamical import checking


def generate_mapping():
    sources = ['Mix_Other','Tech_C1','Unit_C1', 'Tech_C2','Unit_C2']
    impact_matrix = pd.DataFrame(data=np.array([(k+1)*np.arange(1,6) for k in range(2)]).T,
                                 index=sources, columns=['Idx1','Idx2'])

    mix = pd.DataFrame(data=[[99]+[1]*5+[99]], columns=['Mix_C1_C2']+sources+['Mix_C2_C1'])
    return impact_matrix, mix


def generate_residual(freq='MS', fit_start=True, fit_end=True):
    ### 3 years production
    if freq=='MS':
        prodIdx = pd.date_range("2017", "2020", freq="MS")
    elif freq=='YS':
        prodIdx = pd.date_range("2017", "2020", freq="YS")
    
    ### Residual
    resIdx = pd.period_range(start=str(2017+int(not fit_start)),
                             end=str(2020-int(not fit_end)))
        
    ### Generate data
    prod = pd.DataFrame(1, index=prodIdx, columns=range(2))
    res = pd.DataFrame(1, index=resIdx, columns=range(1))
    return prod, res




class TestChecking(unittest.TestCase):
            
            
    def test_mappingGood(self):
        mapping, mix = generate_mapping()
        self.assertTrue( checking.check_mapping(mapping, mix), msg="Good mapping check" )
            
            
    def test_mappingNaN(self):
        # Only creating one artificial missing
        mapping, mix = generate_mapping()
        mapping.loc['Tech_C1',"Idx2"] = np.nan # Create one NaN artificially
        
        ### ERROR STRATEGY
        with self.assertRaises(checking.IncompleteError, msg="Error due to NaNs"):
            checking.check_mapping(mapping=mapping, mix=mix, strategy='error')
        ### OTHER STRATEGY
        with self.assertWarns(checking.IncompleteWarning, msg='Warning due to NaNs'):
            checking.check_mapping(mapping=mapping, mix=mix, strategy='other')
            
            
    def test_mappingMissUnit(self):
        # Remove an entire unit from the impact matrix
        mapping, mix = generate_mapping()
        mapping = mapping.drop(index=['Tech_C1']) # Remove the tech
        
        ### ERROR STRATEGY
        with self.assertRaises(checking.MissingError, msg="Error due to missing unit"):
            checking.check_mapping(mapping=mapping, mix=mix, strategy='error')
        ### OTHER STRATEGY
        with self.assertWarns(checking.MissingWarning, msg='Warning due to missing unit'):
            checking.check_mapping(mapping=mapping, mix=mix, strategy='other')
            
            
            
    def test_residualGood(self):
        for freq in ['MS','YS']:
            prod, residual = generate_residual(freq=freq, fit_start=True, fit_end=True)
            self.assertTrue(checking.check_residual_availability(prod=prod, residual=residual, freq=freq),
                            msg=f"Residual available at freq {freq}")
            
            
            
    def test_residualError(self):
        for freq in ['MS','YS']:
            for start,end in zip([True,False],[False,True]):
                prod, residual = generate_residual(freq=freq, fit_start=start, fit_end=end)
                fatality = "end" if start else 'start'
                with self.assertRaises(IndexError, msg=f"Residual missing {fatality} at freq {freq}"):
                    checking.check_residual_availability(prod=prod, residual=residual, freq=freq)



#############
if __name__=='__main__':
    res = unittest.main(verbosity=2)
