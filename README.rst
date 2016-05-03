Openmod's Python Toolchest
==========================

This project serves as a catch-all for openmod devs' useful python tools and
APIs (though we are generally language lovers and are not limited to Python
specifically).

For the foreseeable future, this repo is a bit adhoc -- anything of use that fits
the general theme of energy modeling is welcome. We try to split additions by
subject into the appropriate files (e.g., GIS-related work to `gis.py`, etc.).

The contributors to this repository strive to write clear, understandable,
tested, and documented code. We recognize this requires a nontrivial effort and
respect the effort of others by being willing to review pull requests and
otherwise offer comments, critiques, and first-user experiences.

Communication
-------------

Apart from using the issue tracker, please join the
[listserv](https://groups.google.com/forum/#!forum/openmod-initiative) for any
in depth discussions.

Dependencies
------------

As this is a hodgepodge of tools, different tooling requires different
dependencies.

General
+++++++

0. numpy
0. pandas
0. scipy

GIS
+++

0. fiona
0. rasterio
0. shapely

Modeling & Optimization
+++++++++++++++++++++++

0. pyomo

Testing
+++++++ 

0. `nose <https://pypi.python.org/pypi/nose/1.3.7>`_

Documentation
+++++++++++++

0. `Sphinx <https://pypi.python.org/pypi/Sphinx>`_

Installing
----------

You can install `toolchest` like any other python module::

    ./setup.py install

or for local installations::

    ./setup.py install --user

Testing
----------

From the root directory, run::

    nosetests -w tests

Documentation
-------------

On *Nix Platforms
~~~~~~~~~~~~~~~~~

After you install the project locally, you can generate documentation by::

    cd docs
    make html

You can serve the documentation locally via::

    make serve
	
You can then view the docs at http://localhost:8000/build/html/

On Windows
~~~~~~~~~~~~~~~~~

Follow the above instructions replacing ``make`` with ``./make.bat``.

Contributing
-------------

`toolchest` currently follows a `master`-branch based work flow. All features
introduced in pull requests are merged directly into `master`. Should the code
base become more complex, it is likely that we will transition to a
`develop`-`master` `git`-based release work flow, as described
[here](http://nvie.com/posts/a-successful-git-branching-model/).

We follow [semantic versioning](http://semver.org/) for version numbering.

Any contribution can be pulled into `develop` via a *Pull Request* provided it
meets the following conditions:

0. follows [pep8](https://www.python.org/dev/peps/pep-0008/) style
0. is documented with docstrings formatted in the
  [numpy style](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html)
0. is tested
0. passes CI on both Windows and Linux
0. is reviewed by at least one other contributor

Documentation Caveat
++++++++++++++++++++

Contributions that upgrade *only* documentation are the sole caveat to the above
requirements. Documentation-only additions can be pushed directly to the
`develop` branch. However, if a review is desired, they can of course go through
the process as well.

Following Style Guides
++++++++++++++++++++++

Style guides are always annoying to follow at first but are
[immensely useful](http://da-data.blogspot.com/2016/04/stealing-googles-coding-practices-for.html). Feel
free to hook in [`autopep8`](https://pypi.python.org/pypi/autopep8) to your
favorite editor to automatically fix any style issues. For `emacs`, you can add
the following lines

```
; see https://github.com/paetzke/py-autopep8.el
(require 'py-autopep8)
(add-hook 'python-mode-hook 'py-autopep8-enable-on-save)
```

Conflicts between Contributors
------------------------------

Should any conflicts arise in the course of the project, without any other
particularly good solution, resolution will follow a majority rule on the
listserv.
