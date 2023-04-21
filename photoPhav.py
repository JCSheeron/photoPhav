#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# As a best practice when using python venv, I could have used this, but the
# above seems to work and be more portable
#!/home/jcsheeron/swDev/python/ftArchPostProc/bin/python

# Example of how to disable a pylint check
# C0103 warns that module level vars should be/are constants and should be
# named accordingly with ALL CAPS in an inconsistent and anyoying way.
# Also warns of non snake_case naming.
# Disable this warning. Note, remove '__' in front to activate the disabling.
# The '--' is there so the syntax or pylint: disable can be shown Without
# actually disabling the warning
# __pylint: disable=C0103 # verbose: 'invalid-name'

# Varialbe Naming Conventions:
# Class Names: normally use CapWords Conventions
# Type Variable Names: CapWords convention, or single cap letter. Prefer short names.
# Exception Names: CapWords or follow class naming convention. Suffix should be Error, etc.
# Function Names: lowercase_with_underscores. or mixedCase if already prevailing.
# Variable Names: Follow naming of functions. lowercase_with_underscores or mixedCase if already prevailing.
# Function and Method Arguments:
#   'self' as first argument for instance methods.
#   'cls' as first argument to class methods.
#   Append underscore '_' in the event of a name clash. Better: use synonym.
# Method Names and Instance Variables: Follow function naming rules: lowercase_with_underscores.
#   Use one leading underscore for non-public methods and instance varialbes.
#   Use two leading underscores to invoke name mangling rules._
# Constants: ALL_CAPS_WITH_UNDERSCORES. Usually defined on a module level.

"""
photoPhav.py

PhotoPhav (as in Photo Favorites) will create links to favorite images based on 'star'
and/or color ratings. See main.docstring for additional information.
"""

# arg parser
import argparse
# imports
#
# Standard library and system imports
# import sys
import re  # regular expressions
# path and file processing
from pathlib import Path

# Third party and library imports


# Local application and user library imports

#
# Note: May need PYTHONPATH (set in ~/.profile?) to be set depending
# on the location of the imported files


# Main function to execute when script is run
def main():
    """
    PhotoPhav (as in Photo Favorites) will create links to favorite images based on 'star'
    and/or color ratings.

    A souce directory will be searced for image files. For each image file
    found, inspect the xmp metadata. If the star rating is above
    a value (default: 1) create a link to the file in the destination
    directory. If the color rating is above a value (TODO: What Value), then create
    a link to the file in the destinaiton directory.

    The supported file types are: JPEG, TIFF, GIF, PNG, PSD, INDESIGN, MOV, MP3,
    MPEG2, MPEG4, AVI, FLV, SWF, ASF, POSTSCRIPT, P2, SONYHDV, AVCHD, UCF, WAV,
    XDCAM, XDCAMEX.

    The star rating threshold can be specified with the -sr, --star-rating <rating>
    option, where rating is 1-5. Values at or above the indicated value will be
    included. Default: 1

    The star rating will be ignored if the -is, --ignore-star option is given.

    The color rating threshold can be specified with the -cr, --color-rating <rating>
    option where rating is ???. Values at or above the indicated value will be
    included. **Default value??** NOTE: Not yet supported.

    The color rating will be ignored if the -ic, --ignore-color option is given.
    Default: true (ignore color rating by default)

    A source directory can be provided with the -sd, --source-dir <path> option
    to specify the directory to use for the source images. If this option is
    not provided, the working directory will used as the source directory.

    A destinaiton directory can be provided with the -dd, --dest-dir <path> option
    to specify the directory to use for the link destination. If this option
    is not provided, a 'favorites' sub directory in the working directory
    will first be created if it does not exist, and will used for the
    destination path.

    The -r, -R, --recursive option searches the source directory recursively. If
    images are found in sub folders, the same directory structure will be used
    for the destination directory structure.

    The -f, --file-types <type> or <type list> option allows a single file type,
    or space, comma, or semicolon separated list of file types.
    Supported file types are listed above. The option values not case sensitive,
    but otherwise need to match one of the options lsited above.

    The -x, --xmp-priority option will give priority to information in an xmp
    sidecar file if one exists. Without this option, priority is given to the
    image file over the xmp file, and the xmp file would only be used if there
    was not rating or color information in the image file. In all cases, in
    order to be considered, a file with the same name as the image file ending
    in 'xmp' (case insensitive) must be found. Mutually exclusive with the
    -ix/--ignore-xmp option.

    The -ix, --ignore-xmp option will ignore xmp sidecar file(s), even if they
    are present. Mutually exclusive with the -x/--xmp-priority option.

    The -g, --globp <pattern> option allows files to be searched using a glob
    pattern. Mutually exclusive with the -e/--regexp option.

    The -e, --regexp <pattern> option allows files to be searched using a
    regular expression. Mutually exclusive with the -g/--globp option.

    The -i, --ignore-case option ignores file name case when matching using a glob
    pattern or regex patten. This option is ignored if neither the -g or -e,
    patterns are specified.

    The -v, --verbose option increases output messaging. Mutually exclusive
    with -q and -w.

    The -q, --quiet option eliminates output messaging, even in the event of
    errors. Mutually exclusive with -v and -w.

    The -w, --show-errors-and-warnings option does exactly that. Mutually
    exclusive with -v and -q.
    """
    # Descripiton string will show up in help.
    DESC_STR = main.__doc__
    # Create an epilog string to further describe the input file
    # The epilog will show up at the bottom of the help
    EPL_STR = ""

    # **** argument parsing
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESC_STR,
        epilog=EPL_STR,
    )
    # define the arguments
    # star rating
    parser.add_argument(
        "-sr",
        "--star-rating",
        default=1,
        type=int,
        choices=range(1, 6),  # 1-5
        metavar="rating",
        help="Star rating. Values equal or greater are considered Favorites \
and a link will be created. Default value is 1, so any stared image is a favorite.",
    )
    parser.add_argument(
        "-is", "--ignore-star", action="store_true", help="Ignore star ratings if set."
    )
    # color rating
    parser.add_argument(
        "-cr",
        "--color-rating",
        default=1,
        type=int,
        choices=range(1, 11),  # 1-10
        metavar="rating",
        help="Color rating. Values equal are considered Favorites \
and a link will be created.",
    )
    parser.add_argument(
        "-ic",
        "--ignore-color",
        action="store_true",
        help="NOTE: Not yet supported -- color ratings are always ignored. \
Ignore color ratings if set (default).",
    )
    # source dir
    parser.add_argument(
        "-sd",
        "--source-dir",
        default=".",
        metavar="path",
        help="Source directory. Look in this directory for image files. Omit \
the option or specify '.' to use the working directory.",
    )
    # destination dir
    parser.add_argument(
        "-dd",
        "--destination-dir",
        default="favorites",
        metavar="path",
        help="Destination directory.  Create the links in this directory. \
If this option is not provided, a 'favorites' sub directory in the working \
directory will first be created if it does not exist, and will used for the \
destination path.",
    )
    # recurse thru the source directory
    parser.add_argument(
        "-r",
        "-R",
        "--recursive",
        action="store_true",
        help="Search for image files recursively, starting at the source directory.",
    )
    # file types
    parser.add_argument(
        "-f",
        "--file-types",
        metavar="file type OR [file type1, file type 2 ...]",
        help="Limit processing to specifed file types. Not case sensitive. \
Valid values are: JPEG, TIFF, GIF, PNG, PSD, INDESIGN, MOV, MP3, MPEG2, MPEG4, \
AVI, FLV, SWF, ASF, POSTSCRIPT, P2, SONYHDV, AVCHD, UCF, WAV, XDCAM, XDCAMEX.",
    )
    # xmp options
    og_xmp = parser.add_mutually_exclusive_group(required=False)
    og_xmp.add_argument(
        "-x",
        "--xmp-priority",
        action="store_true",
        help="Give priority to information in an xmp sidecar file if one \
exists. Without this option, priority is given to the image file over the xmp \
file, and the xmp file would only be used if there was not rating or color \
information in the image file. In all cases, in order to be considered, a file \
with the same name as the image file ending in 'xmp' (case insensitive) must be \
found.",
    )
    og_xmp.add_argument(
        "-ix",
        "--ignore-xmp",
        action="store_true",
        help="Ignore xmp files even if they are present.",
    )
    # Mutually exclusive pattern group
    og_pattern = parser.add_mutually_exclusive_group(required=False)
    og_pattern.add_argument(
        "-g",
        "--globp",
        metavar="pattern",
        help="Glob sytle pattern. Mutually exclusivc with -e/--regexp option.",
    )
    og_pattern.add_argument(
        "-e",
        "--regexp",
        metavar="pattern",
        help="Regular expression sytle pattern. Mutually exclusivc with -g/--globp option.",
    )
    # ignore case if file name otherwise matches the glob or regex pattern
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Ignore case if file name otherwise matches the glob or regex pattern. \
Ignored if neither -g/--globp or -e/--regexp options are specified.",
    )
    # Mutually exclusive output messaging group
    og_output = parser.add_mutually_exclusive_group(required=False)
    # verbose output
    og_output.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    # quiet output
    og_output.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Supress all output, including errors and warnings.",
    )
    # show only errors and warnings
    og_output.add_argument(
        "--show-errors-and_warnings",
        action="store_true",
        help="Show only errors and warnings.",
    )
    # parse the arguments
    args = parser.parse_args()

    # At this point, the arguments will be:
    # Argument          Type        Default
    # args.star_rating  int         1
    # args.ignore_star  bool        False   use star ratings >= 1 by default
    # args.color_rating int         1
    # args.ignore_color bool        False   Forced True for now to ignore color rating
    # args.source_dir   string      .
    # args.destination_dir string   ./favorites
    # args.recursive    bool        False
    # args.fileTypes    string      None    single value, or comma or space or semicolon delimited
    # args.globp        string      None    (globp | regexp)
    # args.regexp       string      None
    # args.ignore-case  bool        False   case sensitive by default
    # args.verbose      bool        False   Increase messaging (v | q | w)
    # args.quiet        bool        False   No messaging, not even for errors
    # args.show-errors-and-warnings bool False

    # Force ignore_color to be true for now
    args.ignore_color = True

    if args.verbose:
        # print("\nThe following arguments were parsed:")
        # print(args)
        print(
            "\nNote: ignore_color is forced True at this time. Color ratings \
are not yet supported."
        )

    # Establish source and destination paths
    src_path = Path(args.source_dir)
    dest_path = Path(args.destination_dir)
    #if args.verbose:
    #    print("The source path is:")
    #    print(src_path.resolve())
    #    print("The destination path is:")
    #    print(dest_path.resolve())


# Tell python to run main if this program is executed directly (i.e. not imported)
if __name__ == "__main__":
    main()
