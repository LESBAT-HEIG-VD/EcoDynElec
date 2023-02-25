import unittest
import importlib




def test_if_available(name, package=None):
    try:
        importlib.import_module(name, package)
    except ImportError:
        return False
    else:
        return True


class TestImportMethods(unittest.TestCase):
    
    def test_pandas_import(self):
        self.assertTrue(test_if_available('pandas'))
    
    def test_numpy_import(self):
        self.assertTrue(test_if_available('numpy'))
    
    def test_openpyxl_import(self):
        self.assertTrue(test_if_available('openpyxl'))
        
    def test_main_import(self):
        self.assertTrue(test_if_available('ecodynelec'))
        
    def test_parameter_import(self):
        self.assertTrue(test_if_available('ecodynelec.parameter'))
        
    def test_tracking_import(self):
        self.assertTrue(test_if_available('ecodynelec.tracking'))
        
    def test_easyUse_import(self):
        self.assertTrue(test_if_available('ecodynelec.pipelines'))
        
    def test_impacts_import(self):
        self.assertTrue(test_if_available('ecodynelec.impacts'))
        
    def test_updating_import(self):
        self.assertTrue(test_if_available('ecodynelec.updating'))
        
    def test_checking_import(self):
        self.assertTrue(test_if_available('ecodynelec.checking'))
        
    def test_saving_import(self):
        self.assertTrue(test_if_available('ecodynelec.saving'))
        
    def test_loading_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing'))
        
    def test_loadAutocomplete_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing.autocomplete'))
        
    def test_loadAuxiliary_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing.auxiliary'))
        
    def test_loadDownload_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing.downloading'))
        
    def test_loadGenExch_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing.loading'))
        
    def test_loadImpacts_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing.load_impacts'))
        
    def test_loadRawEntsoe_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing.extracting'))
        
    def test_residual_import(self):
        self.assertTrue(test_if_available('ecodynelec.preprocessing.residual'))
        
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
