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
# Disable this warning.
# pylint: disable=C0103 # verbose: 'invalid-name'

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

# imports
#
# Standard library and system imports
# import sys

# Third party and library imports

# path and file processing
from pathlib import Path

# arg parser
import argparse


# Local application and user library imports

#
# Note: May need PYTHONPATH (set in ~/.profile?) to be set depending
# on the location of the imported files


# Main function to execute when script is run
def main():
    """
    PhotoPhav (as in Photo Favorites) will create links to favorite images based on 'star'
    and/or color ratings.

    A souce directory will be searced for image files. (TODO: Document types). For
    each image file found, inspect the xmp metadata. If the star rating is above
    a value (default: 1) create a link to the file in the destination
    directory. If the color rating is above a value (TODO: What Value), then create
    a link to the file in the destinaiton directory.

    The star rating threshold can be specified with the -sr, --star-rating argument.
    Values at or above the indicated value will be included. Default: 1

    The star rating will be ignored if the -is, --ignore-star option is given.

    The color rating threshold can be specified with the -cr, --color-rating argument.
    Values at or above the indicated value will be included. **Default value??**

    The color rating will be ignored if the -ic, --ignore-star option is given.
    Default: true (ignore color rating by default)

    A source directory can be provided with the -sd, --source-dir argument to specify
    the directory to use for the source images. If this option is not provided,
    the working directory will used as the source directory.

    A destinaiton directory can be provided with the -dd, --dest-dir argument to specify
    the directory to use for the link destination. If this option is not provided,
    the working directory will used as the source directory.

    The -r, -R, --recursive option searches the source directory recursively. If
    images are found in sub folders, the same directory structure will be used
    in the destination (TODO: Naming conflict with orginal file vs link file in 
    the same directory structure.`
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
        metavar="",
        help="Star rating. Values equal or greater are considered Favorites \
and a link will be created. Default value is 1, so any stared image is a favorite."
    )
    parser.add_argument(
        "-is",
        "--ignore-star",
        action="store_true",
        help="Ignore star ratings if set."
    )
    # color rating
    parser.add_argument(
        "-cr",
        "--color-rating",
        default=1,
        type=int,
        metavar="",
        help="Color rating. Values equal are considered Favorites \
and a link will be created."
    )
    parser.add_argument(
        "-ic",
        "--ignore-color",
        action="store_true",
        help="NOTE: Not yet supported -- color ratings are always ignored. \
Ignore color ratings if set (default)."
    )
    # source dir
    parser.add_argument(
        "-sd",
        "--source-dir",
        default=".",
        metavar="",
        help="Source directory. Look here for image files. Omit or specify '.' \
to use the working directoy."
    )
    # destination dir
    parser.add_argument(
        "-dd",
        "--destination-dir",
        default=".",
        metavar="",
        help="Destination directory.  Create the links here. Omit or specify '.' \
to use the working directoy."
    )
    # recurse thru the source directory
    parser.add_argument(
        "-r",
        "-R",
        "--recursive",
        action="store_true",
        help="Search the source directory recursively."
    )
    # verbose output
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output, usually used for troubleshooting."
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
    # args.destination_dir   string .
    # args.recursive    bool        False
    # args.ignore-case  bool        False   case sensitive by default
    # args.regexp       string      None
    # args.verbose      bool        False

    # Force ignore_color to be true for now
    args.ignore_color = True

    if args.verbose:
        print("\nThe following arguments were parsed:")
        print(args)
        print("\nNote: ignore_color is forced True at this time. Color ratings \
are not yet supported.")

# Tell python to run main if this program is executed directly (i.e. not imported)
if __name__ == "__main__":
    main()
