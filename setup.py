import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "IP_WaveletFV",
    version = "0.0.1",
    author = "Andreas, Stefanie, Friedrich, Mostafa",
    author_email = "no-one",
    description = ("TODO."),
    license = "MIT",
    keywords = "TODO",
    url = "TODO",
    packages=['.', 'notebooks'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)