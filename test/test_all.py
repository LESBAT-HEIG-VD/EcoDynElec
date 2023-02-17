"""Module to run all test files alltogether"""

import os
import sys
import unittest

package = os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) # Path to package if needs to be installed

        
        
        
if __name__ == '__main__':

    try:
        import dynamical
    except:
        print("Installing dynamical...")
        os.system(f"{python} -m pip install -e {package}")

    #from test_load_downloads import TestDownload
    #from test_load_extracting import TestExtracting # Use Files
    #from test_load_auxiliary import TestAuxiliary # Use Files
    #from test_load_impacts import TestLoadImpacts # Use Files
    from test_parameter import TestParameterServer
    #from test_parameter import TestParameterPaths, TestParameterMain # Use Files
    from test_checking import TestChecking
    from test_imports import TestImportMethods
    from test_impacts import TestCalcImpacts
    from test_load_loading import TestLoading
    from test_tracking import TestTracking
    from test_load_autocomplete import TestAutocomplete
    #from test_pipelines import TestPipelines # Use Files
    
    res = unittest.main(verbosity=2)
