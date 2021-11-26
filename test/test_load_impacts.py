import os
import unittest

from numpy import unique
from pandas.core import frame
from pandas import DataFrame, Index
from dynamical.load_data import impacts
from dynamical.load_data.auxiliary import get_default_file



def get_rootpath(level=0):
    rp = os.path.dirname( os.path.abspath(__file__) )
    for _ in range(level):
        rp = os.path.dirname(rp)
    return (rp + "/").replace("\\","/").replace("//","/")



class TestLoadImpacts(unittest.TestCase):
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.mapping = get_default_file('Mapping_default.xlsx')
        
    
    ###########################
    #### COUNTRY FROM EXCEL
    def test_ctry_from_excelAllCorrect(self):
        is_old = {'AT':True,'CH':True,'DE':True,'FR':True,'IT':True,'CZ':True,
                  'PT':False,'NL':False,'LU':False,'ES':False,'BE':False,'GB':False,
                  'PL':False,'BG':False,'NO':False,'SE':False,'DK':False}
        for c in is_old:
            self.nature_MappingCtry( impacts.country_from_excel(self.mapping,place=c,
                                                                is_old=is_old[c]), c )
            
    def test_ctry_from_excelError(self):
        with self.assertRaises(ValueError):
            impacts.country_from_excel(self.mapping,place="KZ", is_old=True)
    
    
    
    
    ###############################
    ###### OTHER FROM EXCEL
    def test_other_from_excel(self):
        self.assertEqual(impacts.other_from_excel(self.mapping).shape[0], 1)
        self.assertEqual(list(impacts.other_from_excel(self.mapping).columns),
                         ["GWP","CED_renewable","CED_non-renewable","ES2013"])
        
        
        
        
    
    ##################################
    ###### LOCAL PROD FROM EXCEL
    def test_residual_from_excel(self):
        d, d_other,expected = self.prepare_shapeCtry(place='CH', is_old=True)
        shaped = impacts.shape_country(d, place='CH', expected=expected, is_old=True)
        self.nature_Residual( impacts.residual_from_excel(impact_ch=shaped, mapping=self.mapping),
                              expected=expected)
        
    def test_residual_from_excelError(self):
        d, d_other,expected = self.prepare_shapeCtry(place='CH', is_old=True)
        shaped = impacts.shape_country(d, place='CH', expected=expected, is_old=True)
        with self.assertRaises(ValueError):
            impacts.residual_from_excel(impact_ch=shaped, mapping="WrongFile")
        
        
        
        
        
    #################################
    ####### SHAPE COUNTRY
    def test_shape_countryCstImportError(self):
        is_old = {'AT':True,'CH':True,'DE':True,'FR':True,'IT':True,'CZ':True,
                  'PT':False,'NL':False,'LU':False,'ES':False,'BE':False,'GB':False,
                  'PL':False,'BG':False,'NO':False,'SE':False,'DK':False}
        for c in is_old:
            d, d_other, expected = self.prepare_shapeCtry(place=c, is_old=is_old[c])
            with self.assertRaises(KeyError, msg=f"Is old: {is_old[c]} ({c})"):
                impacts.shape_country(d, place=c, expected=expected, is_old=is_old[c],
                                      imp_other=None, cst_import=True)
                
    def test_shape_countryNormal(self):
        is_old = {'AT':True,'CH':True,'DE':True,'FR':True,'IT':True,'CZ':True,
                  'PT':False,'NL':False,'LU':False,'ES':False,'BE':False,'GB':False,
                  'PL':False,'BG':False,'NO':False,'SE':False,'DK':False}
        for c in is_old:
            d, d_other, expected = self.prepare_shapeCtry(place=c, is_old=is_old[c])
            out = impacts.shape_country(d, place=c, expected=expected, is_old=is_old[c],
                                        imp_other=None, cst_import=False)
            self.nature_ShapeCtry(element=out, c=c, expected=expected, cst_import=False)
                
    def test_shape_countryCstImport(self):
        is_old = {'AT':True,'CH':True,'DE':True,'FR':True,'IT':True,'CZ':True,
                  'PT':False,'NL':False,'LU':False,'ES':False,'BE':False,'GB':False,
                  'PL':False,'BG':False,'NO':False,'SE':False,'DK':False}
        for c in is_old:
            d, d_other, expected = self.prepare_shapeCtry(place=c, is_old=is_old[c])
            out = impacts.shape_country(d, place=c, expected=expected, is_old=is_old[c],
                                        imp_other=d_other, cst_import=True)
            self.nature_ShapeCtry(element=out, c=c, expected=expected, cst_import=True)
            
        
            
    
    #########################
    ######## EXTRACT IMPACTS
    def test_extract_impactErrorResidual(self):
        ctry = ['AT','DE','FR','IT','CZ','PT','NL','LU','ES','BE','GB','PL','BG','NO','SE','DK'] # All but CH
        with self.assertRaises(ValueError):
            impacts.extract_impacts(ctry=ctry, mapping_path=self.mapping, residual=True, target='AT')
            
    def test_extract_impactErrorCtry(self):
        with self.assertRaises(TypeError): # Triggers an error for wrong ctry format
            impacts.extract_impacts(ctry=0, mapping_path=self.mapping)
            
    def test_extract_impact1Ctry(self):
        self.nature_Extracted( impacts.extract_impacts(ctry='CH'), ctry=['CH'] )
            
    def test_extract_impactMoreCtry(self):
        self.nature_Extracted( impacts.extract_impacts(ctry=['CH','DE','BE']), ctry=['CH','DE','BE'] )
    
    
    
    
    
    #########################
    ########### HELPERS #####
    
    def nature_MappingCtry(self, element, c):
        ### Test the output of Mapping per Ctry
        self.assertIsInstance(element, frame.DataFrame, msg=c) # Check it is a DF
        self.assertGreater(element.shape[0],0, msg=c) # Check it has info
        self.assertGreater(element.shape[1],0, msg=c) # Check it has info
        self.assertIn("Environmental impacts of ENTSO-E sources", element.columns, msg=c) # key element here
        
    def nature_ShapeCtry(self, element, c, expected, cst_import=False):
        ### Test the shape_country output per country
        self.assertIsInstance(element, frame.DataFrame, msg=c) # Check it is a DF
        self.assertEqual(element.shape, (expected.shape[0], 4), msg=c) # Check if correct shape
        self.assertEqual(element.isna().sum().sum(), 0, msg=c) # Check if all NaNs are filled
        self.assertFalse((False in [k[-3:]==f"_{c}" for k in element.index]), msg=c) # Check renaming of index
        if cst_import:
            for i in element.columns:
                content = unique(element.loc[:,i].values)
                self.assertEqual(content[content!=0].shape[0], 1, msg=f"{i} in {c}") # Check unicity
        
    def nature_Residual(self, element, expected):
        ### Test the shape_country output per country
        self.assertIsInstance(element, frame.DataFrame) # Check it is a DF
        self.assertEqual(element.shape, (expected.shape[0]+2, 4)) # Check if correct shape
        self.assertEqual(list(element.index[:2]), ['Residual_Hydro_CH','Residual_Other_CH']) # Check labels
        
        
    def nature_Extracted(self, element, ctry):
        expected = Index(["Other_fossil","Fossil_Gas","Fossil_Peat","Biomass",
                                "Hydro_Run-of-river_and_poundage","Solar","Waste","Wind_Onshore",
                                "Other_renewable","Fossil_Oil_shale","Hydro_Water_Reservoir",
                                "Fossil_Brown_coal/Lignite","Nuclear","Fossil_Oil","Hydro_Pumped_Storage",
                                "Wind_Offshore","Fossil_Hard_coal","Geothermal",
                                "Fossil_Coal-derived_gas","Marine"])
        self.assertIsInstance(element, frame.DataFrame) # Check if is a DF
        self.assertEqual( element.shape[0], expected.shape[0]*len(ctry)+1 ) # Check if good number of elements
        
        
    
    
    def prepare_shapeCtry(self, place, is_old):
        ### Prepare data for shape_country function
        d = impacts.country_from_excel(self.mapping, place, is_old=is_old)
        d_other = impacts.other_from_excel(self.mapping)
        expected = Index(["Other_fossil","Fossil_Gas","Fossil_Peat","Biomass","Hydro_Run-of-river_and_poundage",
                    "Solar","Waste","Wind_Onshore","Other_renewable","Fossil_Oil_shale","Hydro_Water_Reservoir",
                    "Fossil_Brown_coal/Lignite","Nuclear","Fossil_Oil","Hydro_Pumped_Storage","Wind_Offshore",
                    "Fossil_Hard_coal","Geothermal","Fossil_Coal-derived_gas","Marine"])
        return d, d_other, expected

        
        
        
#############
if __name__ == '__main__':
    unittest.main(verbosity=2)