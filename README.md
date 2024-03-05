# EcoDynElec: Dynamic Life Cycle Assessment of electricity for ENTSO-E countries

EcoDynElec software tracks the origin of electricity accross european countries based on generation and cross-border exchanges and allows the dynamic evaluation of environmental impacts of electricity.

![workflow](docs/images/workflow.png)

`ecodynelec` is a free software under MIT licence. It was developped in a collaboration between the [EMPA](https://www.empa.ch/), [HEIG-VD](https://heig-vd.ch/), the [SUPSI](https://www.supsi.ch/home.html).















## Getting started

`ecodynelec` must first be cloned from its [Git repository](https://github.com/LESBAT-HEIG-VD/EcoDynElec), by using prompt (example below) or any other method:

    >> cd path/to/where/to/download/elecodyn
    
    >> git clone https://github.com/LESBAT-HEIG-VD/EcoDynElec.git

After cloning the repository, the package can be used and installed in different ways, as explained below.

### Conventional install

Typical python installation softwares such as `pip` or `conda` can be used to install
`ecodynelec` from your local copy of the git. To do so, use a prompt or a terminal and 
move inside the `ecodynelec/` directory. From there, use `pip` (example) or `conda`
to install.

    >> cd /path-to-ecodynelec-copy/EcoDynElec/
    
    >> python -m pip install ./

An alternative is to use python to trigger the `setup.py` file within the `ecodynelec/`
directory. More on this in the [official Python documentation](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-from-a-local-src-tree).

    >> cd /path-to-ecodynelec-copy/EcoDynElec/
    
    >> python setup.py install

Now `ecodynelec` can be imported and used as any other python package.

If experiencing issues using `ecodynelec` in notebooks, the
*guaranteed install* below may be a good and cheap alternative.

### Guaranteed install

To make sure the package can be used in every python environment, the
absolute path to the `ecodynelec` package must be temporarily added to
the python records. This method simply tells python where to find the
source information. Actually, “installing python packages” just means
“telling python where to find packages on a machine to execute them”.
Enter the following in your Python script or Python Notebook:

    import sys, os # Required python libraries
    
    sys.path.insert(0, os.path.abspath("path/to/ecodynelec/package")) # Adds the path to the package in the python records, but only in this script


Now `ecodynelec` can be imported and used as any other python package,
only in the current script or Notebook.


    import ecodynelec







## Documentation
An online documentation was written and is available on the [dedicated ReadTheDocs](https://ecodynelec.readthedocs.io/en/latest/)





## Contributions
EcoDynElec did contribute to the project [EcoDynBat - Ecobilan Dynamique des Bâtiments](https://www.aramis.admin.ch/Texte/?ProjectID=41804).

P.Padey et al., 2020, 'Dynamic Life Cycle Assessment of the building electricity demand', *Erneuern! Sanierungsstrategien für den Gebäudepark, Status Seminar brenet (Building and Renewable Energies Network of Technology)*, Aarau Schweiz, [doi](https://doi.org/10.5281/zenodo.3900180). https://arodes.hes-so.ch/record/6718?ln=fr

[Pre-print]  Lédée, François and Padey, Pierryves and Goulouti, Kyriaki and Lasvaux, Sebastien and Beloin-Saint-Pierre, Didier, Ecodynelec: Open Python Package to Create Historical Profiles of Environmental Impacts from Regional Electricity Mixes. Available at SSRN: https://ssrn.com/abstract=4420940 or http://dx.doi.org/10.2139/ssrn.4420940 


![logo](docs/images/logo.png)
