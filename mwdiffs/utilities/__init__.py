from .dump2diffs import dump2diffs, process_args as dump2diffs_args, drop_text
from .revdocs2diffs import revdocs2diffs, process_args as revdocs2diffs_args

__all__ = [dump2diffs, revdocs2diffs, dump2diffs_args, revdocs2diffs_args,
           drop_text]
