import os
import unittest

from numpy import unique
from pandas import DataFrame as df
from pandas.core.frame import DataFrame
from ecodynelec.preprocessing import auxiliary







class TestAuxiliary(unittest.TestCase):
    
    ########################
    ### TESTS ON get_default_file
    def test_get_default_fileFUVector(self):
        self.assertTrue(os.path.isfile(auxiliary.get_default_file('Functional_Unit_vector.csv')))
    
    def test_get_default_fileMapping(self):
        self.assertTrue(os.path.isfile(auxiliary.get_default_file('mapping_template.xlsx')))
    
    def test_get_default_fileNeighbourhood(self):
        self.assertTrue(os.path.isfile(auxiliary.get_default_file('Neighbourhood_EU.csv')))
    
    def test_get_default_fileLosses(self):
        self.assertTrue(os.path.isfile(auxiliary.get_default_file('Pertes_OFEN.csv')))
    
    def test_get_default_fileResidual(self):
        self.assertTrue(os.path.isfile(auxiliary.get_default_file('Repartition_Residus.xlsx')))
    
    def test_get_default_fileSwissGrid(self):
        self.assertTrue(os.path.isfile(auxiliary.get_default_file('SwissGrid_total.csv')))
    
    def test_get_default_fileError(self):
        with self.assertRaises(KeyError):
            auxiliary.get_default_file("NOFile")
        
        
    ##############################
    ### TESTS ON load_useful_countries
    def test_load_useful_countriesFull(self):
        full = auxiliary.load_useful_countries(None, ['AT','CH','DE','FR','IT'])
        self.assertIsInstance(full, list) # Test if returns a list
        for c in full: self.assertIsInstance(c,str) # Test if all elements are str
        self.assertEqual(full, list(unique(full))) # Test if all are unique
    
    def test_load_useful_countriesIndividuals(self):
        list_countries = ['AT','CH','DE','FR','IT']
        full = auxiliary.load_useful_countries(None, list_countries)
        for c in list_countries: # Make sure each has less than the whole
            self.assertTrue(len(full)>=len(auxiliary.load_useful_countries(None, [c])), msg=c)
    
    
    ##########################
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesAll(self):
        self.nature_Losses(auxiliary.load_grid_losses(None)) # Execute with no pathway or restriction
    
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesStartIn(self):
        self.nature_Losses(auxiliary.load_grid_losses(None,
                                                      start='2017')) # Execute with shorter start
    
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesStartOut(self):
        self.nature_Losses(auxiliary.load_grid_losses(None,
                                                      start='2012')) # Execute with longer start
    
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesEndIn(self):
        self.nature_Losses(auxiliary.load_grid_losses(None,
                                                      end='2017')) # Execute with shorter end
    
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesEndOut(self):
        self.nature_Losses(auxiliary.load_grid_losses(None,
                                                      end='2050')) # Execute with longer end
    
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesTimeIn(self):
        self.nature_Losses(auxiliary.load_grid_losses(None,
                                                      start='2017',
                                                      end='2018')) # Execute with all shorter
    
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesTimeOut(self):
        self.nature_Losses(auxiliary.load_grid_losses(None,
                                                      start='2012',
                                                      end='2050')) # Execute with all longer
    
    ### TESTS ON load_grid_losses
    def test_load_grid_lossesTimeNone(self):
        self.nature_Losses(auxiliary.load_grid_losses(None,
                                                      start='2018',
                                                      end='2017')) # Execute with no data
        
        
    
    
    
    #########################
    ####### TESTS ON load_gap_content
    def test_load_gap_contentAtYear(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='Y') )
    def test_load_gap_contentAtYearSame(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='Y', start='2017', end='2017') )
        
    def test_load_gap_contentAtMonth(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='M') )
    def test_load_gap_contentAtMonthSame(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='M', start='2017-01', end='2017-01') )
        
    def test_load_gap_contentAtWeek(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='W') )
    def test_load_gap_contentAtWeekSame(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='W', start='2017-01-01', end='2017-01-01') )
        
    def test_load_gap_contentAtDay(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='d', start='2017', end='2018') )
    def test_load_gap_contentAtDaySame(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='d', start='2017-01-01', end='2017-01-01') )
        
    def test_load_gap_contentAtHour(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='H', start='2017-01', end='2017-03') )
    def test_load_gap_contentAtHourSame(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='H', start='2017-01-01 00:00',
                                                    end='2017-01-01 00:00') )
        
    def test_load_gap_contentAt30min(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='30min', start='2017-01', end='2017-03') )
    def test_load_gap_contentAt30minSame(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='30min', start='2017-01-01 00:00',
                                                    end='2017-01-01 00:00') )
        
    def test_load_gap_contentAt15min(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='15min', start='2017-01', end='2017-03') )
    def test_load_gap_contentAt15minSame(self):
        self.nature_Gap( auxiliary.load_gap_content(None, freq='15min', start='2017-01-01 00:00',
                                                    end='2017-01-01 00:00') )
        
        
        
        
        
        
    ########################
    ### TESTS ON load_SG
    def test_load_SGNoDates(self):
        with self.assertWarns(Warning):
            auxiliary.load_swissGrid(None, freq='15min', start=None, end=None)
        
    def test_load_SGStartOut(self):
        with self.assertWarns(Warning):
            auxiliary.load_swissGrid(None, freq='15min', start="2012", end="2019")
        
    def test_load_SGEndOut(self):
        with self.assertWarns(Warning):
            auxiliary.load_swissGrid(None, freq='15min', start="2018", end="2050")
        
    def test_loadSGHour(self):
        self.nature_SG( auxiliary.load_swissGrid(None, freq='H', start="2018", end="2019") )
        
        
        
        
        
        
        
    ########################
    ### TESTS ON load_rawEntso
    def test_load_rawEntsoError(self):
        with self.assertRaises(KeyError):
            auxiliary.load_rawEntso(mix_data=0)
            
    def test_load_rawEntsoDataframe(self):
        self.assertTrue( all(auxiliary.load_rawEntso(mix_data=df(None)) == df(None)) )
        
    
    
    
    #########################
    ########### HELPERS #####
    
    def nature_Losses(self, element):
        ### Test the content of  Grid Loss output
        self.assertIsInstance(element, DataFrame)
        self.assertEqual(element.shape[1],3)
        self.assertEqual(list(element.columns),['year','month','Rate'])
        
    def nature_Gap(self, element):
        self.assertIsInstance(element, DataFrame)
        self.assertEqual(element.shape[1],2)
        self.assertEqual(list(element.columns),['Hydro_Res','Other_Res'])
        
    def nature_SG(self, element):
        self.assertIsInstance(element, DataFrame)
        self.assertEqual(element.shape[1],9)
        self.assertEqual(list(element.columns),['Production_CH','Mix_CH_AT','Mix_AT_CH',
                                                'Mix_CH_DE','Mix_DE_CH','Mix_CH_FR',
                                                'Mix_FR_CH','Mix_CH_IT','Mix_IT_CH'])

        
        
        
        
        
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
