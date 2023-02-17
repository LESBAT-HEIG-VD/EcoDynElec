import unittest
import os
from pandas.core.frame import DataFrame

from ecodynelec.preprocessing import extracting


def get_rootpath(level=0):
    rp = os.path.dirname( os.path.abspath(__file__) )
    for _ in range(level):
        rp = os.path.dirname(rp)
    return (rp + "/").replace("\\","/").replace("//","/")


class TestExtracting(unittest.TestCase):
        
    
    def nature(self, element, keys):
        ### Test the content of  dicts
        self.assertIsInstance(element, dict) # Test the output type
        self.assertEqual(list(element.keys()), keys) # Test if all expected keys are here
        self.assertTrue( [type(element[c])==DataFrame
                          for c in keys].count(False)==0 ) # Test if pandas dicts
        
    def files_created(self, root, ctry, case):
        for c in ctry: # Test if all files were created
            filepath = f"{root}{c}_{case}_MW.csv"
            self.assertTrue(os.path.isfile(filepath))
            
            if os.path.isfile(filepath): # Clear file if it exists
                os.remove(filepath)
        
    def test_get_parameters(self):
        self.assertEqual(extracting.get_parameters('import'),
                         ('InMapCode','OutMapCode','FlowValue','OutAreaTypeCode'),
                         msg=" Exchange case")
        self.assertEqual(extracting.get_parameters('generation'),
                         ('MapCode','ProductionType','ActualGenerationOutput','AreaTypeCode'),
                         msg=" Generation case")
        
    def test_get_parametersError(self):
        with self.assertRaises(KeyError):
            extracting.get_parameters(0) # Test the error for bad parameter
    
    def test_load_filesError(self): # Error if no case given
        path = get_rootpath()
        with self.assertRaises(KeyError):
            extracting.load_files(path, destination=None, case=None)
    
    def test_extractBadFiles(self): # Error if no filepath passed
        with self.assertRaises(KeyError):
            extracting.extract(ctry=['CH'], dir_gen=None, dir_imp=None)
            
    def test_extractGen(self): # Check the nature of returned elments
        root = get_rootpath(level=1)
        list_countries = ['AT','CH','DE','FR','IT']
        dir_gen = f"{root}examples/test_data/generations/"
        # Generation only
        self.nature(extracting.extract(ctry=list_countries, dir_gen=dir_gen, dir_imp=None),
                    keys=list_countries)
            
    def test_extractExch(self): # Check the nature of returned elments
        list_countries = ['AT','CH','DE','FR','IT']
        root = get_rootpath(level=1)
        dir_imp = root+"examples/test_data/exchanges/"
        # Exchanges only
        self.nature(extracting.extract(ctry=list_countries, dir_gen=None, dir_imp=dir_imp),
                    keys=list_countries)
            
    def test_extractAll(self): # Check the nature of returned elments
        list_countries = ['AT','CH','DE','FR','IT']
        root = get_rootpath(level=1)
        dir_gen = root+"examples/test_data/generations/"
        dir_imp = root+"examples/test_data/exchanges/"
        # Generation and Exchanges
        out = extracting.extract(ctry=list_countries, dir_gen=dir_gen, dir_imp=dir_imp)
        self.assertEqual(len(out),2) # 2 elements returned
        self.nature(out[0], keys=list_countries)
        self.nature(out[1], keys=list_countries)
    
    def test_create_per_countryGeneration(self):
        list_countries = ['AT','CH','DE','FR','IT']
        root1 = get_rootpath(level=1)
        root0 = get_rootpath(level=0)
        out = extracting.create_per_country(path_dir=root1+"examples/test_data/generations/", case='generation',
                                            ctry=list_countries,
                                            savedir=root0+"test_data/prep_generations/",
                                            savedir_resolution=root0+"test_data/")
        
        ### Test output
        self.nature(out, list_countries)
        
        ### Test preprocessed files
        self.files_created(root=root0+"test_data/prep_generations/",
                           ctry=list_countries,
                           case='generation')
        ### Test resolution
        path_resolution = root0+"test_data/Original_resolution_generation.csv"
        self.assertTrue( os.path.isfile(path_resolution) )
        if os.path.isfile(path_resolution):
            os.remove(path_resolution)
            
     
    def test_create_per_countryExchange(self):
        list_countries = ['AT','CH','DE','FR','IT']
        root1 = get_rootpath(level=1)
        root0 = get_rootpath(level=0)
        out = extracting.create_per_country(path_dir=root1+"examples/test_data/exchanges/", case='import',
                                            ctry=list_countries,
                                            savedir=root0+"test_data/prep_exchanges/",
                                            savedir_resolution=root0+"test_data/")
        ### Test output
        self.assertIsInstance(out, dict) # Test the output type
        self.assertEqual(list(out.keys()), list_countries) # Test if all expected keys are here
        self.assertTrue( [type(out[c])==DataFrame
                          for c in list_countries].count(False)==0 ) # Test if pandas dicts
        
        ### Test preprocessed files
        self.files_created(root=root0+"test_data/prep_exchanges/",
                           ctry=list_countries,
                           case='import')
        ### Test resolution
        path_resolution = root0+"test_data/Original_resolution_import.csv"
        self.assertTrue( os.path.isfile(path_resolution) )
        if os.path.isfile(path_resolution):
            os.remove(path_resolution)
        

        
        
        
#############
if __name__=='__main__':
    res = unittest.main(verbosity=2)
