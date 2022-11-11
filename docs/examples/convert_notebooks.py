"""
Converts example notebooks into rst files
"""

import os

path_notebooks = os.path.abspath("../../examples/")
path_doc = os.path.abspath("./")


# Convert the notebooks

notebooks = [f for f in os.listdir(path_notebooks) if f.endswith(".ipynb")]
for f in notebooks:
    print(f"Converting {f}" + " "*20, end="\r")
    os.system(f"jupyter nbconvert --to rst --output-dir {path_doc} {os.path.join(path_notebooks,f)}")

print("Completed."+" "*50)
