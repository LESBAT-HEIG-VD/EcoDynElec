#!/usr/bin/bash


######## CREATE RST FILES FROM CODE
sphinx-apidoc -e -o ./modules/drafts/ ../dynamical/

####### CLEAN THE FILES


####### RENAME AND MOVE THE FILES


####### CREATE THE HTML DOCUMENTATION
make clean
make html
