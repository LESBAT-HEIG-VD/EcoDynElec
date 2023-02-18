EcoDynElec: Dynamic Life Cycle Assessment of electricity for ENTSO-E countries
==============================================================================

EcoDynElec software tracks the origin of electricity accross european countries based on generation and cross-border exchanges and allows the dynamic evaluation of environmental impacts of electricity.

.. image:: images/workflow.png

``ecodynelec`` is a free software under APACHE 2.0 licence. It was developped in a collaboration between the `EMPA <https://www.empa.ch/>`_, `HEIG-VD <https://heig-vd.ch/>`_, the `SUPSI <https://www.supsi.ch/home.html>`_.

Installation
============
For now the software can only be installed from the `gitlab repository <https://gitlab.com/fledee/ecodynelec/>`_

Contributions
=============
EcoDynElec did contribute to the project `EcoDynBat - Ecobilan Dynamique des Bâtiments <https://www.aramis.admin.ch/Texte/?ProjectID=41804>`_.

.. image:: images/logo.png

.. toctree::
    :maxdepth: 1
    :caption: Supplementary

    supplementary/download
    supplementary/mapping_usage
    supplementary/parameters
    supplementary/auxilary_files
    supplementary/functional_unit

.. toctree::
    :maxdepth: 3
    :caption: Structure

    structure/architecture
    structure/data_loading
    structure/load_impacts
    structure/tracking
    structure/impacts
    structure/local_residual

.. toctree::
    :maxdepth: 1
    :caption: Examples

    examples/Getting_started
    examples/Handle_parameters
    examples/Downloading
    examples/Execute_main_pipeline
    examples/Exploit_results
    examples/Electricity_mix_map

.. toctree::
    :maxdepth: 2
    :caption: Modules
    :hidden:

    modules/pipelines
    modules/parameter
    modules/impacts
    modules/tracking
    modules/preprocessing
    modules/saving
    modules/checking



Renaming the whold directory
============================
We are going to need a complete renaming, as ``ecodynelec`` is not satisfying at all.
This means different things, as explained in `this post <https://stackoverflow.com/questions/2041993/how-do-i-rename-a-git-repository>`_


There are various possible interpretations of what is meant by renaming a Git repository: the displayed name, the repository directory, or the remote repository name. Each requires different steps to rename.

Displayed Name
**************

Rename the displayed name (for example, shown by `gitweb`):

    - Edit ``.git/description`` to contain the repository's name.
    - Save the file.

Repository Directory
********************

Git does not reference the name of the directory containing the repository, as used by git clone master child, so we can simply rename it:

    - Open a command prompt (or file manager window).
    - Change to the directory that contains the repository directory (i.e., do not go into the repository directory itself).
    - Rename the directory (for example, using `mv` from the command line or the `F2` hotkey from a GUI).

Remote Repository
*****************

Rename a remote repository as follows:

    - Go to the remote host (for example, https://github.com/User/project).
    - Follow the host's instructions to rename the project (will differ from host to host, but usually Settings is a good starting point).
    - Go to your local repository directory (i.e., open a command prompt and change to the repository's directory).
    - Determine the new URL (for example, git@github.com:User/project-new.git)
    - Set the new URL using Git:

.. code-block::

    git remote set-url origin git@github.com:User/project-new.git




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
