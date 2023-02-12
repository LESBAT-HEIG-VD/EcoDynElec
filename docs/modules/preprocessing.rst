preprocessing
===============================

The submodule `autocomplete <https://dynamical.readthedocs.io/en/latest/modules/preprocessing.autocomplete.html>`_ gathers functions used for automatically identify, sort and fill missing data in the original data from the ENTSO-E.

The submodule `auxiliary <https://dynamical.readthedocs.io/en/latest/modules/preprocessing.auxiliary.html>`_ is useful to load and prepare all informations needed in the process of ``dynamical`` that are neither from the ENTSO-E database nor from the LCA databases. This module is mostly involved in the process if a residual is included or exchanges are the Swiss border are modified.

The submodule `downloading <https://dynamical.readthedocs.io/en/latest/modules/preprocessing.downloading.html>`_ allows a connection with ENTSO-E servers to retrieve information.

The submodule `loading <https://dynamical.readthedocs.io/en/latest/modules/preprocessing.loading.html>`_ supervises and organizes the loading and cleaning of electricity data for the generation and exchanges. It partially relies on the ``extracting`` and the ``autocomplete`` modules. It is also in charge of adapting the frequency (time step) of the data.

The submodule `load_impacts <https://dynamical.readthedocs.io/en/latest/modules/preprocessing.load_impacts.html>`_ loads and organizes the information related to the impacts of electricity generation sources.

The submodule `extracting <https://dynamical.readthedocs.io/en/latest/modules/preprocessing.extracting.html>`_ selects relevant information in the files downloaded from the ENTSO-E databases. It specifically operates on this format to minimize the computation time and necessary memory space while extracting all required information.

The submodule `residual <https://dynamical.readthedocs.io/en/latest/modules/preprocessing.residual.html>`_ handles the creation and integration of a possible residual in the data.


.. toctree::
   :maxdepth: 1
   :hidden:

   preprocessing.autocomplete
   preprocessing.auxiliary
   preprocessing.downloading
   preprocessing.loading
   preprocessing.load_impacts
   preprocessing.extracting
   preprocessing.residual
