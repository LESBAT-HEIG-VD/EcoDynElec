import unittest
import os
import pandas as pd
from datetime import datetime

from dynamical import parameter


class NoError(Exception):
    """To raise when no error happens"""
    def __init__(self, message=''):
        super().__init__(message)
        
        
def rightSet(obj, name, value, failure=Exception):
    try:
        setattr(obj, name, value)
    except failure:
        return # Nothing happens, i.e. failure of the test
    else:
        raise NoError("No exception occurred")
        
        
def rightExecute(executable, *args, failure=TypeError):
    try:
        executable(*args)
    except failure:
        return # Nothing happens, i.e. failure of the test
    else:
        raise NoError("No exception occurred")


def verify_types(self, obj):
    for attr in self.list_attributes:
        self.assertIsInstance( getattr(obj, attr), list, msg=f"Instance {attr}" )
        self.assertTrue( all(isinstance(k,str) for k in getattr(obj, attr)), msg=f"Instance {attr} content" )
    for attr in self.date_attributes:
        self.assertIsInstance( getattr(obj, attr), datetime, msg=f"Instance {attr}" )
    for attr in self.str_attributes:
        self.assertIsInstance( getattr(obj, attr), str, msg=f"Instance {attr}" )
    for attr in self.bool_attributes:
        self.assertIsInstance( getattr(obj, attr), bool, msg=f"Instance {attr}" )
    for attr in self.int_attributes:
        self.assertIsInstance( getattr(obj, attr), int, msg=f"Instance {attr}" )
    for attr in self.str_attributes:
        k = getattr(obj, attr)
        self.assertTrue( any([isinstance(k,str), k is None]), msg=f"Instance {attr}" )





class TestParameterMain(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.subclass = parameter.Parameter
        
        self.list_attributes = ['ctry']
        self.date_attributes = ['start','end']
        self.str_attributes = ['target','freq','timezone']
        self.strNone_attributes = []
        self.bool_attributes = ['cst_imports','sg_imports','net_exchanges','network_losses',
                                'residual_local', 'residual_global','data_cleaning']
        self.int_attributes = []
            
            
    def verify_modification(self, obj, correct=True):
        """Check only the elements that may raise an Error"""
        if correct: # Verify no issue when changing
            elements = [{'list':self.date_attributes,'error':ValueError,'val':"2022",'typ':datetime},
                        {'list':['ctry'],'error':TypeError,'val':['CH'],'typ':list},
                        {'list':['freq'],'error':ValueError,'val':"Y",'typ':str},]
            
            for e in elements:
                for attr in e['list']: # Dates
                    with self.assertRaises(NoError, msg=f"Correct {attr}"):
                        rightSet(obj, attr, e['val'], failure=e['error'])
                    setattr(obj,attr,e['val']) # Set the value then
                    self.assertIsInstance(getattr(obj,attr), e['typ'], msg=f'Good Type {attr}')
                
        else:
            elements = [{'list':self.date_attributes,'error':ValueError,'val':"Wrong"},
                        {'list':['ctry','path','server'],'error':TypeError,'val':0},
                        {'list':['freq'],'error':ValueError,'val':"Wrong"},]
            for e in elements:
                for attr in e['list']:
                    with self.assertRaises(e['error'], msg=f"Wrong {attr}"):
                        setattr( obj, attr, e['val'])
            
    
    def test_typesDefault(self):
        config = self.subclass()
        verify_types(self, config)
        
    def test_typesExcel(self):
        path_excel = os.path.abspath("../examples/Spreadsheet_download.xlsx")
        config = self.subclass(excel=path_excel)
        verify_types(self, config)
        
    def test_typesFromExcel(self):
        path_excel = os.path.abspath("../examples/Spreadsheet_download.xlsx")
        config = self.subclass().from_excel(excel=path_excel)
        verify_types(self, config)
        
    def test_changingAttributes(self):
        # No new attributes
        config = self.subclass()
        with self.assertRaises(AttributeError, msg='Parameter: no additional object'):
            config.__setattr__("new_attribute", 0)
            
        # Correct type attribution
        self.verify_modification(config, correct=True)
        
        # Wrong type attribution
        self.verify_modification(config, correct=False)
        
        
    def test_datesExcel(self):
        ### Test if automatic date transformation from excel does work
        config = self.subclass()
        
        ### Test the No-date
        self.assertIsNone( config._dates_from_excel(pd.Series([0]*5)),
                           msg="Dates Excel: all zeros") # All zeros
        self.assertIsNone( config._dates_from_excel(pd.Series(dtype=float)),
                           msg="Dates Excel: all empty") # Empty
        
        ### Test overload
        self.assertEqual( config._dates_from_excel(pd.Series([1]*5)), '01-01-01 01:01',
                         msg='Dates Excel: More arguments')
        
        ### Test the auto-completing
        for i in range(1,6):
            vec = [2222,2,22,2,22][:i]
            ### Test that auto-completing the date works
            with self.assertRaises(NoError, msg='Error data from Excel'):
                rightExecute(config._dates_from_excel, pd.Series(vec))
            
            ### Test that the value obtained is conform
            self.assertEqual( config._dates_from_excel(pd.Series(vec)).count("2"),
                              str(vec).count('2'), msg='Values data from Excel')










class TestParameterPaths(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.subclass = parameter.Filepath
        
        self.list_attributes = []
        self.date_attributes = []
        self.str_attributes = []
        self.strNone_attributes = ["generation","exchanges","savedir","fu_vector",
                                   "mapping","neighbours","gap","swissGrid","networkLosses"]
        self.bool_attributes = []
        self.int_attributes = []
            
            
    def verify_modification(self, obj, correct=True):
        """Check only the elements that may raise an Error"""
        if correct: # Verify no issue when changing
            good_path = os.path.abspath("../examples/test_data/")
            for attr in self.strNone_attributes:
                with self.assertRaises(NoError, msg=f"Correct {attr}"):
                    rightSet(obj, attr, good_path, failure=FileNotFoundError)
        else:
            bad_path = "path_does_not_exist"
            for attr in self.strNone_attributes:
                with self.assertRaises(FileNotFoundError, msg=f"Wrong {attr}"):
                    setattr( obj, attr, bad_path )
            
    
    def test_typesDefault(self):
        config = self.subclass()
        verify_types(self, config)
        
    def test_typesExcel(self):
        path_excel = os.path.abspath("../examples/Spreadsheet_download.xlsx")
        config = self.subclass(excel=path_excel)
        verify_types(self, config)
        
    def test_typesFromExcel(self):
        path_excel = os.path.abspath("../examples/Spreadsheet_download.xlsx")
        config = self.subclass().from_excel(excel=path_excel)
        verify_types(self, config)
        
    def test_changingAttributes(self):
        # No new attributes
        config = self.subclass()
        with self.assertRaises(AttributeError, msg='Filepath: no additional object'):
            config.__setattr__("new_attribute", 0)
            
        # Correct type attribution
        self.verify_modification(config, correct=True)
        
        # Wrong type attribution
        self.verify_modification(config, correct=False)










class TestParameterServer(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.subclass = parameter.Server
        
        self.list_attributes = []
        self.date_attributes = []
        self.str_attributes = ["_nameGenerationFile","_nameExchangesFile",
                               "_remoteGenerationDir","_remoteExchangesDir","host"]
        self.strNone_attributes = ['username','password']
        self.bool_attributes = ["useServer","removeUnused"]
        self.int_attributes = ['port']
            
            
    def verify_modification(self, obj, correct=True):
        """Check only the elements that may raise an Error"""
        if correct: # Verify no issue when changing
            for attr in self.bool_attributes:
                with self.assertRaises(NoError, msg=f"Correct {attr}"):
                    rightSet(obj, attr, True, failure=TypeError)
        else:
            for attr in self.bool_attributes:
                with self.assertRaises(TypeError, msg=f"Wrong {attr}"):
                    setattr( obj, attr, "wrong")
            
    
    def test_typesDefault(self):
        config = self.subclass()
        verify_types(self, config)
        
    def test_typesExcel(self):
        path_excel = os.path.abspath("../examples/Spreadsheet_download.xlsx")
        config = self.subclass(excel=path_excel)
        verify_types(self, config)
        
    def test_typesFromExcel(self):
        path_excel = os.path.abspath("../examples/Spreadsheet_download.xlsx")
        config = self.subclass().from_excel(excel=path_excel)
        verify_types(self, config)
        
    def test_changingAttributes(self):
        # No new attributes
        config = self.subclass()
        with self.assertRaises(AttributeError, msg='Server: no additional object'):
            config.__setattr__("new_attribute", 0)
            
        # Correct type attribution
        self.verify_modification(config, correct=True)
        
        # Wrong type attribution
        self.verify_modification(config, correct=False)








#############
if __name__=='__main__':
    res = unittest.main(verbosity=2)
