import unittest
import os
import numpy as np
import pandas as pd

from ecodynelec import impacts


def generate_data():
    sources = ['Mix_Other','Tech_C1','Unit_C1', 'Tech_C2','Unit_C2']
    impact_matrix = pd.DataFrame(data=np.array([(k+1)*np.arange(1,6) for k in range(2)]).T,
                                 index=sources, columns=['Idx1','Idx2'])

    mix = pd.DataFrame(data=[[99]+[1]*5+[99]], columns=['Mix_C1_C2']+sources+['Mix_C2_C1'])
    return impact_matrix, mix




class TestCalcImpacts(unittest.TestCase):
    
    def test_globalImpact(self):
        impact_matrix, mix = generate_data()
        expected = pd.DataFrame({0: impact_matrix.sum()}).T
        
        out = impacts.compute_global_impacts(mix, impact_matrix)
        self.assertTrue( np.all( out==expected ), msg='Global impact calculation' )
        
        
    def test_detailImpact(self):
        impact_matrix, mix = generate_data()
        
        for idx in impact_matrix.columns:
            expected = impact_matrix.loc[:,[idx]].T.rename(index={idx:0})
            out = impacts.compute_detailed_impacts(mix, impact_matrix.loc[:,idx], indicator=idx)
            self.assertTrue( np.all( out==expected ), msg=f"Detailed impact index {idx}/2" )
            
            
    def test_equalizeGood(self):
        impact_matrix, mix = generate_data()
        
        expected = impact_matrix.astype('float32')
        out = impacts.equalize_impact_vector(impact_data=impact_matrix, mix=mix)
        self.assertTrue( np.all( out==expected ), msg="Good Impact matrix equalizer" )
            
            
    def test_equalizeNoProd(self):
        impact_matrix, mix = generate_data()
        mix.loc[:,'Tech_C2'] = 0
        impact_matrix = impact_matrix.drop(index='Tech_C2')
        
        out = impacts.equalize_impact_vector(impact_data=impact_matrix, mix=mix)
        self.assertTrue( np.all( out.loc['Tech_C2']==0. ),
                         msg="Equalizer with non-producing unit missing impact" )
            
            
    def test_equalizeNaN(self):
        # Only creating one artificial missing
        impact_matrix, mix = generate_data()
        impact_matrix.loc['Tech_C1',"Idx2"] = np.nan # Create one NaN artificially
        
        ### ERROR STRATEGY
        self.assertRaises(ValueError, impacts.equalize_impact_vector, impact_matrix, mix, 'error')
        ### WORST STRATEGY
        expected = impact_matrix.loc[:,'Idx2'].max()
        out = impacts.equalize_impact_vector(impact_data=impact_matrix, mix=mix, strategy='worst')
        self.assertEqual( out.loc['Tech_C1',"Idx2"], expected,
                         msg=f"Equalizer with NaN; strategy 'worst'" )
        ### UNIT STRATEGY
        expected = impact_matrix.loc['Tech_C2',"Idx2"]
        out = impacts.equalize_impact_vector(impact_data=impact_matrix, mix=mix, strategy='unit')
        self.assertEqual( out.loc['Tech_C1',"Idx2"], expected,
                         msg=f"Equalizer with NaN; strategy 'unit'" )
            
            
    def test_equalizeMissUnit(self):
        # Remove an entire unit from the impact matrix
        impact_matrix, mix = generate_data()
        impact_matrix = impact_matrix.drop(index=['Tech_C1']) # Remove the tech
        
        ### ERROR STRATEGY
        self.assertRaises(ValueError, impacts.equalize_impact_vector, impact_matrix, mix, 'error')
        ### WORST STRATEGY
        expected = impact_matrix.loc[:,'Idx2'].max()
        out = impacts.equalize_impact_vector(impact_data=impact_matrix, mix=mix, strategy='worst')
        self.assertTrue( 'Tech_C1' in out.index, msg=f"Equalizer with NaN; strategy 'worst' (tech in idx)" )
        self.assertEqual( out.loc['Tech_C1',"Idx2"], expected,
                         msg=f"Equalizer missing Unit; strategy 'worst'" )
        ### UNIT STRATEGY
        expected = impact_matrix.loc['Tech_C2',"Idx2"]
        out = impacts.equalize_impact_vector(impact_data=impact_matrix, mix=mix, strategy='unit')
        self.assertTrue( 'Tech_C1' in out.index, msg=f"Equalizer with NaN; strategy 'unit' (tech in idx)" )
        self.assertEqual( out.loc['Tech_C1',"Idx2"], expected,
                         msg=f"Equalizer missing Unit; strategy 'unit'" )




#############
if __name__=='__main__':
    res = unittest.main(verbosity=2)
