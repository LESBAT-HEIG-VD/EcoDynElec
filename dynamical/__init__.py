### Initialization file for the module computing the impacts of the electric grid.

import os
import sys

# Allows to refer to sub-modules within the module
CURRENT_DIR = os.path.dirname( os.path.abspath(r"{}".format(__file__)) )
sys.path.append(CURRENT_DIR)
