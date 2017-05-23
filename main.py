#!/usr/bin/env python
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys
import time

import changelogparser

SEP = "\x00"
args = None
output_file_obj = None


class NoHtimeFiles(Exception):
    pass


def get_latest_htime_file(brick_path):
    htime_dir = os.path.join(brick_path, ".glusterfs/changelogs/htime")
    htime_files = sorted(os.listdir(htime_dir))
    if len(htime_files) == 0:
        raise NoHtimeFiles("HTIME File not exists, Is Changelog enabled?")

    return htime_files[-1]


def process_changelog_record(record):
    global args, output_file_obj

    isdir = False
    renamed_file = False
    path = None

    if record.fop == "RENAME":
        renamed_file = True
        path = record.path1
    elif record.fop == "UNLINK":
        path = record.path
    elif record.fop == "RMDIR":
        path = record.path
        isdir = True

    if path is None:
        return

    if args.output_prefix:
        path = os.path.join(args.output_prefix, path)

    if isdir:
        op = "rmdir {0}".format(path)
    else:
        op = "rm -f {0}".format(path)

    if renamed_file:
        op += "  # Renamed to {0}".format(record.path2)

    op += "\n"

    if output_file_obj is not None:
        output_file_obj.write(op)
    else:
        sys.stdout.write(op)


def process_htime_file(brick_path, filename):
    htime_file_path = os.path.join(brick_path,
                                   ".glusterfs/changelogs/htime",
                                   filename)
    changelog_ts = 0

    with open(htime_file_path) as f:
        # Read first few bytes and split into paths
        # get length of first path to get path size
        data = f.read(300)
        path_length = len(data.split(SEP)[0])
        f.seek(0)

        # Get each Changelog file name and process it
        while True:
            changelog_file = f.read(path_length + 1).strip(SEP)
            if not changelog_file:
                break

            changelog_ts = int(changelog_file.split(".")[-1])
            fname = changelog_file.split("/")[-1]

            # Avoid processing the changelog is not interested
            if changelog_ts < args.modified_since:
                continue

            # If no real changelog file, Changelog filename starts
            # with lower case changelog.TS instead of CHANGELOG.TS
            # Parse Changelog file only if it is real Changelog file
            if fname.startswith("changelog."):
                continue

            changelogparser.parse(changelog_file.strip(SEP),
                                  callback=process_changelog_record)

        if changelog_ts > 0:
            msg = "# Changelogs processed Till {0}\n".format(changelog_ts)
            if output_file_obj is not None:
                output_file_obj.write(msg)
            sys.stdout.write(msg)


def get_args():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=__doc__)
    parser.add_argument("brick_path", help="Brick Path")
    parser.add_argument("--output-file", "-o", help="Output File")
    parser.add_argument("--modified-since", "-m", type=int,
                        help="Files modified since",
                        default=int(time.time()))
    parser.add_argument("--output-prefix", "-p", help="Output prefix for path",
                        default="")
    return parser.parse_args()


def main():
    global args, output_file_obj

    args = get_args()

    try:
        htime_file = get_latest_htime_file(args.brick_path)
    except NoHtimeFiles as err:
        sys.stderr.write("{0}\n".format(err))
        sys.exit(1)

    out = "#!/bin/bash\n"
    if args.output_file:
        output_file_obj = open(args.output_file, "w")
        output_file_obj.write(out)
    else:
        sys.stdout.write(out)

    process_htime_file(args.brick_path, htime_file)


if __name__ == "__main__":
    main()
