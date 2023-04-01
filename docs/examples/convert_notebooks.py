"""
Converts example notebooks into rst files
"""

import os

parent = lambda path,n: os.path.dirname(path) if n==0 else parent(os.path.dirname(path),n-1)
path_notebooks = os.path.join(parent(os.path.abspath(__file__),2), 'examples/')
path_doc = os.path.dirname( os.path.abspath(__file__) )


# Convert the notebooks

notebooks = [f for f in os.listdir(path_notebooks) if f.endswith(".ipynb")]
for f in notebooks:
    print(f"Converting {f}" + " "*20, end="\r")
    os.system(f"jupyter nbconvert --to rst --output-dir {path_doc} {os.path.join(path_notebooks,f)}")

print("Completed."+" "*50)
