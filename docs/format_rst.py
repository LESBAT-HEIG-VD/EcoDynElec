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
    -d, --delete <string>:
        systematically delete a section of text if found
    -s, --substitute <string1%string2>:
        systematically replace string1 by string2 if found
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



def substitute(path:str="./draft/", infile=None, newvalue=None):
    """Substitute a section of name with another for all
    .rst files containing it.
    
    Parameters
    ----------
        path: str
            path to the directory to verify
        infile,newvalue: str
            the text to replace, and its new value.
    """
    abspath = os.path.abspath(path)

    ### Verification of the path
    if not os.path.isdir(path):
        raise FileNotFoundError(f'No such file or directory: {abspath}')

    ### Verification of the strings
    if infile is None:
        raise ValueError("Need a string to identify in file names")
    if newvalue is None:
        newvalue = "" # Just delete if nothing passed.

    ### Modify the .rst files
    for f in os.listdir(abspath):
        if infile in f: # If string in the file name
            print(f'"{os.path.join(path,f)}" --> "{os.path.join(path,f.replace(infile,newvalue))}"')
            os.rename( os.path.join(abspath,f), os.path.join( abspath,f.replace(infile,newvalue) ) )



    
if __name__ == '__main__':
    ### Execution from command line

    ### Get the arguments from comand line
    argv = sys.argv
    
    ### Collect and clean the arguments
    args = []
    was_stored = 0
    for arg in argv:
        if arg.startswith('--'): # Long argument
            args.append(arg[2:])
            was_stored = 1
        elif arg.startswith("-"): # Short argument
            args += list(arg[1:])
            was_stored = 1
        else:
            if was_stored==1:
                if args[-1] in ['s','substitute','d','delete']:
                    args.append(arg)
            was_stored = 0

    if not os.path.isdir( os.path.abspath(argv[-1]) ):
        raise FileNotFoundError(f'Last argument is no path to directory')
    
    ### Execute the functions
    is_instruction = 0
    for n,arg in enumerate(args):
        if arg in ('f','flag'): # Flag rst
            flag_drafts(path=argv[-1])
        elif arg in ('u','unflag'): # Unflag rst drafts
            unflag_drafts(path=argv[-1])
        elif arg in ('s','substitute'): # Modify string
            item,sub = args[n+1].split("%")
            substitute(path=argv[-1],infile=item,newvalue=sub)
            is_instruction=2
        elif arg in ('d','delete'): # Modify string
            substitute(path=argv[-1],infile=args[n+1])
            is_instruction=2
        elif is_instruction==0:
            warnings.warn(f'Option {arg} not implemented. Nothing executed')

        is_instruction = max(0, is_instruction-1)
