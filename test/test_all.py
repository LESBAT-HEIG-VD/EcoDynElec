"""Module to run all test files alltogether"""

import os, sys, pathlib
sys.path.insert(0, "/home/user/EcoDynBat/ecodyn/") # Better would be to pip-install in modifiable version...


def test_all():
    try:
        import dynamical
    except:
        os.system("python3 -m pip install --user -e /home/user/EcoDunBat/ecodyn/")
    
    path = pathlib.Path(__file__).parent.resolve()
    print(f"Current folder is {path}")
    files = [f for f in os.listdir(path) if ((f.startswith("test_"))&(f!="test_all.py"))]
    
    for f in files:
        os.system(f"python3 ./{f}")

        
        
        
        
if __name__ == '__main__':
    test_all()