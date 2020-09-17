============================================================
assembly_information_model: Assembly Information Model
============================================================

.. start-badges

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://github.com/augmentedfabricationlab/assembly_information_model/blob/master/LICENSE
    :alt: License MIT

.. image:: https://travis-ci.org/augmentedfabricationlab/assembly_information_model.svg?branch=master
    :target: https://travis-ci.org/augmentedfabricationlab/assembly_information_model
    :alt: Travis CI

.. end-badges

.. Write project description

**This repository provides datastructures, tools and methods for assembly information modeling.** ...


Main features
-------------

* feature
* feature
* more features

**assembly_information_model** runs on Python 3.8 and COMPAS 15.6


Requirements
------------

* COMPAS

Installation
::

    (base)  conda config --add channels conda-forge
    (base)  conda create -n your_env_name python=3.8 compas=0.15.6 --yes
    (base)  conda activate your_env_name
    (your_env_name) python -m compas_rhino.install -v 6.0 -p compas compas_ghpython compas_rhino
    
Verify
::

    (your_env_name) python
    >>> import compas
    >>> compas.__version__
    '0.15.6'
    >>> exit()


Installation
------------

Make sure you setup your local development environment correctly:

* Clone the `assembly_information_model <https://github.com/augmentedfabricationlab/assembly_information_model>`_ repository.
* Install development dependencies and make the project accessible from Rhino (change to repository directory in the Anaconda prompt):

::

    pip install -r requirements-dev.txt
    invoke add-to-rhino
    pip install your_filepath_to_assembly_information_model 

**You're ready to start working!**

During development, use tasks on the
command line to ease recurring operations:

* ``invoke clean``: Clean all generated artifacts.
* ``invoke check``: Run various code and documentation style checks.
* ``invoke docs``: Generate documentation.
* ``invoke test``: Run all tests and checks in one swift command.
* ``invoke add-to-rhino``: Make the project accessible from Rhino.
* ``invoke``: Show available tasks.

For more details, check the `Contributor's Guide <CONTRIBUTING.rst>`_.


Releasing this project
----------------------

.. Write releasing instructions here


.. end of optional sections
..

Credits
-------------

This package was created by `Kathrin Doerfler <doerfler@tum.de>`_ `@kathrindoerfler <https://github.com/kathrindoerfler>`_ at `@augmentedfabricationlab <https://github.com/augmentedfabricationlab>`_. This package is based on `compas_assembly <https://github.com/BlockResearchGroup/compas_assembly>`_ by `@BlockResearchGroup <https://github.com/BlockResearchGroup>`_


