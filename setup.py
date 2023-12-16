from setuptools import setup, find_packages
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()
if os.path.exists(os.path.join(dir_path, "requirements.txt")):
    with open(os.path.join(dir_path, "requirements.txt")) as f:
        requirements = f.read().splitlines()
else:
    requirements = ['numpy', 'pandas', 'openpyxl', 'xlrd', 'odfpy', 'paramiko', 'matplotlib', 'tabula-py']


setup(
    name="ecodynelec",
    version="0.2.0",
    description="A library for dynamic LCA of european electricity.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Francois Ledee, Aymeric Bourdy",
    author_email="ledee.francois@gmail.com, aymericb5@gmail.com",
    url="https://gitlab.com/fledee/ecodynelec/",
    packages=find_packages(".", exclude=['test']),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache License, Version 2.0",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)
