# Get deleted fileslist and old path from renames

Script to find the list of files which are deleted or renamed after a
given timestamp.


    $ python main.py --help
    usage: main.py [-h] [--output-file OUTPUT_FILE]
                   [--modified-since MODIFIED_SINCE]
                   [--output-prefix OUTPUT_PREFIX]
                   brick_path
     
    positional arguments:
      brick_path            Brick Path
     
    optional arguments:
      -h, --help            show this help message and exit
      --output-file OUTPUT_FILE, -o OUTPUT_FILE
                            Output File
      --modified-since MODIFIED_SINCE, -m MODIFIED_SINCE
                            Files modified since
      --output-prefix OUTPUT_PREFIX, -p OUTPUT_PREFIX
                            Output prefix for path

Example:

    python main.py /bricks/b1 -m 1494662597 --output-prefix /mnt/gv2/.gfid

Example output:

    #!/bin/bash
    rm -f /mnt/gv2/.gfid/00000000-0000-0000-0000-000000000001/f3  # Renamed to 00000000-0000-0000-0000-000000000001/f0
    rm -f /mnt/gv2/.gfid/00000000-0000-0000-0000-000000000001/f2
    rm -f /mnt/gv2/.gfid/00000000-0000-0000-0000-000000000001/f0  # Renamed to 00000000-0000-0000-0000-000000000001/f3
    rm -f /mnt/gv2/.gfid/00000000-0000-0000-0000-000000000001/f1
    # Changelogs processed Till 1495530876

