========================
conda environment helper
========================


.. image:: https://img.shields.io/pypi/v/cenv.svg
        :target: https://pypi.python.org/pypi/cenv

.. image:: https://img.shields.io/travis/technic/cenv.svg
        :target: https://travis-ci.com/technic/cenv

.. image:: https://readthedocs.org/projects/cenv/badge/?version=latest
        :target: https://cenv.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Wrapper around conda that automatically persists changes to environment.yml
It is quite dummy but useful in simple case scenarios.


* Free software: MIT license
* Documentation: https://cenv.readthedocs.io.


Features
--------

* You run `cenv install numpy`, it calls `conda install numpy` checks for errors and then updates corresponding environment.yml

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
