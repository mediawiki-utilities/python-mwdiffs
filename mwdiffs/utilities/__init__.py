"""
This module implements a set of utilities for generating diffs and content
persistence, statistics from the command-line.  When the mwpersistence python
package is installed, an `mwpersistence` utility should be available from the
command-line.  Run `mwpersistence -h` for more information:

mwdiffs dump2diffs
++++++++++++++++++
.. automodule:: mwdiffs.utilities.dump2diffs
    :noindex:

mwdiffs revdocs2diffs
+++++++++++++++++++++
.. automodule:: mwdiffs.utilities.revdocs2diffs
    :noindex:
"""
from .dump2diffs import dump2diffs, process_args as dump2diffs_args, drop_text
from .revdocs2diffs import revdocs2diffs, process_args as revdocs2diffs_args

__all__ = [dump2diffs, revdocs2diffs, dump2diffs_args, revdocs2diffs_args,
           drop_text]
