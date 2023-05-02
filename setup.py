from setuptools import setup, find_packages
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(dir_path+"/README.md", "r") as fh:
    long_description = fh.read()
with open(dir_path+"/requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="ecodynelec",
    version="0.1.0",
    description="A library for dynamic LCA of european electricity.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Francois Ledee",
    author_email="ledee.francois@gmail.com",
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
