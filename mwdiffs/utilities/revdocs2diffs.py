r"""
``$ mwdiffs revdocs2diffs -h``
::

    Computes diffs from a page-partitioned sequence of JSON revision documents.

    Usage:
        revdocs2diffs (-h|--help)
        revdocs2diffs [<input-file>...] --config=<path> [--namespaces=<ids>]
                      [--timeout=<secs>] [--keep-text] [--threads=<num>]
                      [--output=<path>] [--compress=<type>] [--verbose]
                      [--debug]

    Options:
        -h|--help           Print this documentation
        <input-file>        The path to file containing a page-partitioned
                            sequence of JSON revision documents
                            [default: <stdin>]
        --config=<path>     The path to a deltas DiffEngine configuration
        --namespaces=<ids>  A comma separated list of namespace IDs to be
                            considered [default: <all>]
        --timeout=<secs>    The maximum number of seconds that a diff will be
                            able to run before being stopped [default: 10]
        --keep-text         If set, the 'text' field will be populated in the
                            output JSON.
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
import sys
import time
from itertools import groupby

import mwcli
import yamlconf
from deltas import DiffEngine
from stopit import ThreadingTimeout as Timeout
from stopit import TimeoutException

from .util import ops2opdocs

logger = logging.getLogger(__name__)


def process_args(args):
    config_doc = yamlconf.load(open(args['--config']))
    diff_engine = DiffEngine.from_config(config_doc, config_doc['diff_engine'])

    if args['--namespaces'] == "<all>":
        namespaces = None
    else:
        namespaces = set(int(id)
                         for id in args['--namespaces'].strip().split(","))

    return {'diff_engine': diff_engine,
            'namespaces': namespaces,
            'timeout': float(args['--timeout']),
            'keep_text': bool(args['--keep-text'])}


def _revdocs2diffs(*args, keep_text=False, **kwargs):
    keep_text = bool(keep_text)

    docs = revdocs2diffs(*args, **kwargs)

    if not keep_text:
        docs = drop_text(docs)

    yield from docs


def drop_text(docs):
    for doc in docs:
        doc.pop('text', None)
        yield doc


def revdocs2diffs(rev_docs, diff_engine, namespaces=None, timeout=None,
                  verbose=False):
    """
    Generates a sequence of revision JSON documents containing a 'diff' field
    that represents the change to the text between revisions.

    :Parameters:
        rev_docs : `iterable` ( `dict` )
            A page-partitioned sequence of JSON revision documents
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
    namespaces = set(namespaces) if namespaces is not None else None

    page_rev_docs = groupby(rev_docs, lambda rd: rd['page'])

    for page_doc, rev_docs in page_rev_docs:
        if namespaces is not None and page_doc['namespace'] not in namespaces:
            # Skip this entire page.
            continue

        if verbose:
            sys.stderr.write(page_doc['title'] + ": ")

        processor = diff_engine.processor()
        for rev_doc in diff_rev_docs(rev_docs, processor, timeout=timeout):

            if verbose:
                if 'skipped' in rev_doc['diff']:
                    sys.stderr.write("S")
                if 'timedout' in rev_doc['diff']:
                    sys.stderr.write("T")
                else:
                    sys.stderr.write(".")
                sys.stderr.flush()

            yield rev_doc

        if verbose:
            sys.stderr.write("\n")


def diff_rev_docs(rev_docs, processor, timeout=None):

    last_id = None
    for rev_doc in rev_docs:
        diff = {'last_id': last_id}
        if 'text' not in rev_doc:
            logger.debug("No text to process for {0}.  Skipping."
                         .format(rev_doc['id']))
            # Now we implement a no-op.
            diff['skipped'] = "no text"
            diff['ops'] = []

        else:
            # Diff processing uses a lot of CPU.  So we set a timeout for
            # crazy revisions and record a timer for analysis later.
            text = rev_doc['text']
            with Timer() as t:
                if timeout is None:
                    # Just process the text
                    operations, a, b = processor.process(text)
                    diff['ops'] = [op for op in ops2opdocs(operations, a, b)]
                else:
                    # Try processing with a timeout
                    try:
                        with Timeout(timeout) as ctx:
                            operations, a, b = processor.process(text)
                    except TimeoutException:
                        pass

                    if ctx.state != ctx.TIMED_OUT:
                        # We didn't timeout.  cool.
                        diff['ops'] = list(ops2opdocs(operations, a, b))
                    else:
                        # We timed out.  Record a giant delete and insert
                        diff['ops'] = [
                            {
                                'name': "delete",
                                'a1': 0,
                                'a2': len(a),
                                'b1': 0,
                                'b2': 0,
                                'tokens': a
                            },
                            {
                                'name': "insert",
                                'a1': 0,
                                'a2': 0,
                                'b1': 0,
                                'b2': len(b),
                                'tokens': b
                            }
                        ]
                        diff['timedout'] = True

                        # Make sure that the processor state is right
                        processor.update(last_text=(text))

            # All done.  Record how much time it all took
            diff['time'] = t.interval

        rev_doc['diff'] = diff

        yield rev_doc

        last_id = rev_doc['id']


class Timer:
    def __enter__(self):
        self.start = time.clock()
        self.interval = None
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


streamer = mwcli.Streamer(
    __doc__,
    __name__,
    _revdocs2diffs,
    process_args
)
main = streamer.main
