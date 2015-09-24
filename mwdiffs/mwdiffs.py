import mwcli

router = mwcli.Router(
    "mwdiffs",
    "This script provides access to a set of utilities for processing " +
        "revision diffs.",
    {'dump2diffs': "Generats diffs from XML dumps",
     'revdocs2diffs': "Generates diffs from page-partitioned revision " +
                      "documents"})

main = router.main
