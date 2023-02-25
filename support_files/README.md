# Support Files

The support files reflect files in the software. However these are simply a collection of files and are not used by the software, ***unless specified by the user***.

If nothin is specified, the software relies on the data files in `ecodynelec/data/`. All tests in the test procedure also rely on the files in `ecodynelec/data/`. To update the software files, a module `ecodynelec.updating` was added. With the correct parameters, it will simply take files in the present `support_files/` directory and copy them or reduce them before overwriting the fies data.

However parametrization of EcoDynElec allows the user to directly point at specific files for different purposes. In such case, it is possible to point at the files in `support_files/` directory, ***or anywhere else on your local machine***.
