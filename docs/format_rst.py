#!/usr/bin/python3

"""
Name
----
    format_rst - Script aiming at formatting the documentation files

Synopsis
--------
    ./format_rst.py [OPTIONS] PATH 

Description
-----------
    Python script to format the documentation.

Options
-------
    -f, --flag:
        flag .rst files of target directory into
        .rst.draft files
    -u, --unflag:
        unflag all .rst.draft files back to .rst
        files.
"""

import os
import sys
import warnings


def flag_drafts(path:str):
    """Modify the extension of all .rst files of a directory
    into a .rst.draft file

    Parameters
    ----------
        path: str
            path to the directory to verify
    """
    abspath = os.path.abspath(path)

    ### Verification of the path
    if not os.path.isdir(path):
        raise FileNotFoundError(f'No such file or directory: {abspath}')

    ### Modify the extension of all .rst files
    for f in os.listdir(abspath):
        if f.endswith(".rst"):
            os.rename( os.path.join(abspath,f), os.path.join(abspath,f+".draft") )

    

def unflag_drafts(path:str="./draft/"):
    """Modify the extension of all .rst.draft files of a directory
    back into a .rst file

    Parameters
    ----------
        path: str
            path to the directory to verify
    """
    abspath = os.path.abspath(path)

    ### Verification of the path
    if not os.path.isdir(path):
        raise FileNotFoundError(f'No such file or directory: {abspath}')

    ### Modify the extension of all .rst files
    for f in os.listdir(abspath):
        if f.endswith(".rst.draft"):
            if f.startswith('dynamical.'):
                os.rename( os.path.join(abspath,f), os.path.join( abspath,f.replace("dynamical.","").replace(".draft","") ) )
            else:
                os.rename( os.path.join(abspath,f), os.path.join( abspath,f.replace(".draft","") ) )

    
if __name__ == '__main__':
    ### Execution from command line

    ### Get the arguments from comand line
    argv = sys.argv
    
    ### Collect and clean the arguments
    args = []
    for arg in argv:
        if arg.startswith('--'): # Long argument
            args.append(arg)
        elif arg.startswith("-"): # Short argument
            args += list(arg[1:])

    if not os.path.isdir( os.path.abspath(argv[-1]) ):
        raise FileNotFoundError(f'Last argument is no path to directory')
    
    ### Execute the functions
    for arg in args:
        if arg in ('f','flag'): # Flag rst
            flag_drafts(path=argv[-1])
        elif arg in ('u','unflag'): # Unflag rst drafts
            unflag_drafts(path=argv[-1])
        else:
            warnings.warn(f'Option {arg} not implemented. Nothing executed')
