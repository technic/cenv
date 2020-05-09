===============================
conda environment helper script
===============================


.. image:: https://img.shields.io/pypi/v/cenv_script.svg
        :target: https://pypi.python.org/pypi/cenv_script

.. image:: https://img.shields.io/travis/technic/cenv_script.svg
        :target: https://travis-ci.com/technic/cenv_script

.. image:: https://readthedocs.org/projects/cenv-script/badge/?version=latest
        :target: https://cenv-script.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Wrapper around conda that automatically persists changes to environment.yml
It is quite dummy but useful in simple case scenarios.


* Free software: MIT license
* Documentation: https://cenv-script.readthedocs.io.


Features
--------

* You run ``cenv-script install numpy``
* It calls ``conda install numpy``, checks for errors and then updates corresponding environment.yml

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
