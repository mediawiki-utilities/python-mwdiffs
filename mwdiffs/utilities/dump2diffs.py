r"""
``$ mwdiffs dump2diffs -h``
::

    Computes diffs from an XML dump.

    Usage:
        dump2diffs (-h|--help)
        dump2diffs [<input-file>...] --config=<path> [--namespaces=<ids>]
                   [--timeout=<secs>] [--keep-text] [--threads=<num>]
                   [--output=<path>] [--compress=<type>] [--verbose] [--debug]

    Options:
        -h|--help           Print this documentation
        <input-file>        The path to a MediaWiki XML Dump file
                            [default: <stdin>]
        --config=<path>     The path to a deltas DiffEngine configuration
        --namespaces=<ids>  A comma separated list of namespace IDs to be
                            considered [default: <all>]
        --timeout=<secs>    The maximum number of seconds that a diff will be
                            able to run before being stopped [default: 10]
        --keep-text         If set, the 'text' field will not be dropped after
                            diffs are computed.
        --threads=<num>     If a collection of files are provided, how many
                            processor threads? [default: <cpu_count>]
        --output=<path>     Write output to a directory with one output file
                            per input path.  [default: <stdout>]
        --compress=<type>   If set, output written to the output-dir will be
                            compressed in this format. [default: bz2]
        --verbose           Print progress information to stderr.
        --debug             Prints debug logs to stder.
"""
import logging

import mwcli
import mwxml
import mwxml.utilities

from .revdocs2diffs import drop_text, process_args, revdocs2diffs

logger = logging.getLogger(__name__)


def _dump2diffs(*args, keep_text=False, **kwargs):
    keep_text = bool(keep_text)

    docs = dump2diffs(*args, **kwargs)

    if not keep_text:
        docs = drop_text(docs)

    yield from docs


def dump2diffs(dump, *args, **kwargs):
    """
    Generates a sequence of revision JSON documents containing a 'diff' field
    that represents the change to the text between revisions.

    :Parameters:
        dump : :class:`mwxml.Dump`
            An XML dump to process
        diff_engine : :class:`deltas.DiffEngine`
            A configured diff engine for comparing revisions
        namespaces : `set` ( `int` )
            A set of namespace IDs that will be processed.  If left
            unspecified, all namespaces will be processed.
        timeout : `float`
            The maximum time in seconds that a difference detection operation
            should be allowed to consume.  This is used to handle extremely
            computationally complex diffs that occur from time to time.  When
            a diff takes longer than this many seconds, a trivial diff will be
            reported (remove all the tokens and add them back) and the
            'timedout' field will be set to True
        verbose : `bool`
            Print dots and stuff to stderr
    """
    rev_docs = mwxml.utilities.dump2revdocs(dump)
    return revdocs2diffs(rev_docs, *args, **kwargs)

streamer = mwcli.Streamer(
    __doc__,
    __name__,
    _dump2diffs,
    process_args,
    file_reader=mwxml.Dump.from_file
)
main = streamer.main
