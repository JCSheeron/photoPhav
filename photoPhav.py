#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# As a best practice when using python venv, I could have used this, but the
# above seems to work and be more portable
#!/home/jcsheeron/swDev/python/ftArchPostProc/bin/python

# turn off import sorting for this file
# isort: skip_file

# Example of how to disable a pylint check
# C0103 warns that module level vars should be/are constants and should be
# named accordingly with ALL CAPS in an inconsistent and annoying way.
# Also warns of non snake_case naming.
# Disable this warning. Note, remove '__' in front to activate the disabling.
# The '--' is there so the syntax or pylint: disable can be shown Without
# actually disabling the warning
# __pylint: disable=C0103 # verbose: 'invalid-name'

# Variable Naming Conventions:
# Class Names: normally use CapWords Conventions
# Type Variable Names: CapWords convention, or single cap letter. Prefer short names.
# Exception Names: CapWords or follow class naming convention.
#   Suffix should be 'Error', 'Err', 'Warn', etc.
# Function Names: lowercase_with_underscores, or mixedCase if already prevailing.
# Variable Names: Follow naming of functions, lowercase_with_underscores or
#   mixedCase if already prevailing.
# Function and Method Arguments:
#   'self' as first argument for instance methods.
#   'cls' as first argument to class methods.
#   Append underscore '_' in the event of a name clash. Better: use synonym.
# Method Names and Instance Variables: Follow function naming rules: lowercase_with_underscores.
#   Use one leading underscore for non-public methods and instance variables.
#   Use two leading underscores to invoke name mangling rules._
# Constants: ALL_CAPS_WITH_UNDERSCORES. Usually defined on a module level.

"""
photoPhav.py

PhotoPhav (as in Photo Favorites) will create links to favorite images based on 'star'
and/or color ratings. See main.docstring for additional information.
"""

# imports

# Standard library and system imports
import sys

# arg parser
import argparse

# path, file processing, and regular expressions
from pathlib import Path
import re
import fnmatch

# pretty print
import pprint

# Third party and library imports
# xmp processing
from libxmp.utils import file_to_dict
from libxmp import consts as xmp_consts # constants

# Local application and user library imports
from bpsPrettyPrint import listPrettyPrint1Col

# Note: May need PYTHONPATH (set in ~/.profile?) to be set depending
# on the location of the imported files


# Main function to execute when script is run
def main():
    """
    PhotoPhav (as in Photo Favorites) will create links to favorite images based on 'star'
    and/or color ratings.

    A source directory will be searched for image files. For each image file
    found, inspect the xmp metadata. If the star rating is above
    a value (default: 1) create a link to the file in the destination
    directory. If the color rating is above a value (TODO: What Value), then create
    a link to the file in the destination directory.

    The star rating threshold can be specified with the -sr, --star_rating <rating>
    option, where rating is 1-5. Values at or above the indicated value will be
    included. Default: 1

    The star rating will be ignored if the -is, --ignore_star option is given.

    The color rating threshold can be specified with the -cr, --color_rating <rating>
    option where rating is ???. Values at or above the indicated value will be
    included. **Default value??** NOTE: Not yet supported.

    The color rating will be ignored if the -ic, --ignore_color option is given.
    Default: true (ignore color rating by default)

    A source directory can be provided with the -sd, --source_dir <path> option
    to specify the directory to use for the source images. If this option is
    not provided, the working directory will used as the source directory.

    A destination directory can be provided with the -dd, --dest_dir <path> option
    to specify the directory to use for the link destination. If this option
    is not provided, a 'favorites' sub directory in the working directory
    will first be created if it does not exist, and will used for the
    destination path.

    The -r, -R, --recursive option searches the source directory recursively. If
    images are found in sub folders, the same directory structure will be used
    for the destination directory structure.

    The -fp, --file_priority option will give priority to information embedded
    in the image file. Without this option, priority is given to a xmp
    'sidecar' file if one exists, and the embedded xmp data would only be used
    if the xmp sidecar file does not exist or can't be read or for some reason
    isn't usable. Mutually exclusive with -if/--ignore_file option.

    The -if, --ignore_file option will ignore xmp data embedded in the image
    file, even if it exists. Mutually exclulsive with -fp/--file_priority option.

    The -ix, --ignore_xmp option will ignore xmp sidecar file(s), even if they
    are present.

    The -g, --globp <pattern> option allows files to be searched using a glob
    pattern. Mutually exclusive with the -e/--regexp option.

    The -e, --regexp <pattern> option allows files to be searched using a
    regular expression. Mutually exclusive with the -g/--globp option.

    The -i, --ignore_case option ignores file name case when matching using a glob
    pattern or regex pattern. This option is ignored if neither the -g or -e,
    patterns are specified.

    The -v, --verbose option increases output messaging. Mutually exclusive
    with -q and -w.

    The -q, --quiet option eliminates output messaging, even in the event of
    errors. Mutually exclusive with -v and -w.

    The -w, --show_ew show errors and warning option.
    Mutually exclusive with -v and -q.
    """
    # Description string will show up in help.
    DESC_STR = main.__doc__
    # Create an epilogue string to further describe the input file
    # The epilogue will show up at the bottom of the help
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
        "--star_rating",
        default=1,
        type=int,
        choices=range(1, 6),  # 1-5
        metavar="rating",
        help="Star rating. Values equal or greater are considered Favorites \
and a link will be created. Default value is 1, so any stared image is a favorite.",
    )
    parser.add_argument(
        "-is", "--ignore_star", action="store_true", help="Ignore star ratings if set."
    )
    # color rating
    parser.add_argument(
        "-cr",
        "--color_rating",
        default=1,
        type=int,
        choices=range(1, 11),  # 1-10
        metavar="rating",
        help="Color rating. Values equal are considered Favorites \
and a link will be created.",
    )
    parser.add_argument(
        "-ic",
        "--ignore_color",
        action="store_true",
        help="NOTE: Not yet supported -- color ratings are always ignored. \
Ignore color ratings if set (default).",
    )
    # source dir
    parser.add_argument(
        "-sd",
        "--source_dir",
        default=".",
        metavar="path",
        help="Source directory. Look in this directory for image files. Omit \
the option or specify '.' to use the working directory.",
    )
    # destination dir
    parser.add_argument(
        "-dd",
        "--destination_dir",
        default="favorites",
        metavar="path",
        help="Destination directory.  Create the links in this directory. \
If this option is not provided, a 'favorites' sub directory in the working \
directory will first be created if it does not exist, and will used for the \
destination path.",
    )
    # recourse thru the source directory
    parser.add_argument(
        "-r",
        "-R",
        "--recursive",
        action="store_true",
        help="Search for image files recursively, starting at the source directory.",
    )
    # xmp options
    fx_pattern = parser.add_mutually_exclusive_group(required=False)
    fx_pattern.add_argument(
        "-fp",
        "--file_priority",
        action="store_true",
        help="Give priority to information embedded in the image file. Without \
this option, priority is given to a xmp 'sidecar' file if one exists, and the \
embedded xmp data would only be used if the xmp sidecar file does not exist or \
can't be read or for some reason isn't usable. Mutually exclusive with \
-if/--ignore_file option."
    )
    fx_pattern.add_argument(
        "-if",
        "--ignore_file",
        action="store_true",
        help="Ignore xmp data embedded in the image file, even if it exists. \
Mutually exclulsive with -fp/--file_priority option."
    )
    parser.add_argument(
        "-ix",
        "--ignore_xmp",
        action="store_true",
        help="Ignore xmp files even if they are present.",
    )
    # Mutually exclusive pattern group
    og_pattern = parser.add_mutually_exclusive_group(required=False)
    og_pattern.add_argument(
        "-g",
        "--globp",
        metavar="pattern",
        help="Glob style pattern. Mutually exclusive with -e/--regexp option.",
    )
    og_pattern.add_argument(
        "-e",
        "--regexp",
        metavar="pattern",
        help="Regular expression style pattern. Mutually exclusive with -g/--globp option.",
    )
    # ignore case if file name otherwise matches the glob or regex pattern
    parser.add_argument(
        "-i",
        "--ignore_case",
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
        help="Suppress all output, including errors and warnings.",
    )
    # show only errors and warnings
    og_output.add_argument(
        "--show_ew",
        action="store_true",
        help="Show only errors and warnings.",
    )
    # parse the arguments
    args = parser.parse_args()

    # At this point, the arguments will be:
    # Argument              Type        Default
    # args.star_rating      int         1
    # args.ignore_star      bool        False   use star ratings >= 1 by default
    # args.color_rating     int         1
    # args.ignore_color     bool        False   Forced True for now to ignore color rating
    # args.source_dir       string      .
    # args.destination_dir  string      favorites
    # args.recursive        bool        False
    # args.fileTypes        string      None    single value, or comma or space or semicolon delimited
    # args.file_priority    bool        False
    # args.ignore_xmp       bool        False
    # args.globp            string      None    (globp | regexp)
    # args.regexp           string      None
    # args.ignore_case      bool        False   case sensitive by default
    # args.verbose          bool        False   Increase messaging (v | q | w)
    # args.quiet            bool        False   No messaging, not even for errors
    # args.show_ew          bool        False   Show errors and warnings only

    # Force ignore_color to be true for now
    args.ignore_color = True

    # make a pretty printer
    pp = pprint.PrettyPrinter(width=41, compact=True)

    if args.verbose:
        print("\nThe following arguments were parsed:")
        print(args)
        print(
            "\nNote: ignore_color is forced True at this time. Color ratings \
are not yet supported."
        )

    # Establish source and destination paths
    path_src = Path(args.source_dir)
    path_dest = Path(args.destination_dir)
    # if args.verbose:
    #    print("The source path is:")
    #    print(path_src.resolve())
    #    print("The destination path is:")
    #    print(path_dest.resolve())

    # Search the source directory for files based on recursive, glob, and regex
    # options. Since the case-insensitive globp or regexp options will use regex,
    # simplify the pattern matching by using glob(*)/rgblob(*) and the using
    # regex to match patterns, converting glopb option to a regex if necessary.

    # Start out with a pattern for all files. Then limit based on options.
    # Convert globp option to a regex
    re_pattern = r".*"
    if args.globp:
        re_pattern = fnmatch.translate(args.globp)
    if args.regexp:
        re_pattern = args.regexp
    if args.ignore_case:
        # prepend (?i) to regex pattern to ignore case
        re_pattern = r"(?i)" + re_pattern

    # At this point, any file name filtering will be done with regex. Glob
    # patterns were converted to regex above.

    # get all files (including directories), considering recursive search option
    if args.recursive:
        contents = path_src.rglob("*")
    else:
        contents = path_src.glob("*")

    # Get the files only -- exclude the directories
    path_all_files = [file for file in contents if file.is_file()]
    # if verbose and filtering options are opted, then display the files found
    # before filtering
    if args.verbose and args.globp:
        # extract the path name as a string for display
        print(
            "\nThe following files were found in the source path before applying the glob pattern:"
        )
        listPrettyPrint1Col([file.as_posix() for file in path_all_files])
    elif args.verbose and args.regexp:
        # extract the path name as a string for display
        print(
            "\nThe following files were found in the source path before applying the regex pattern:"
        )
        listPrettyPrint1Col([file.as_posix() for file in path_all_files])

    path_src_files = []  # This will hold the filtered (final) list of path objects
    # filter out files based on regex filter
    for path in path_all_files:
        fp = path.as_posix() # get full path name
        try:
            if re.match(re_pattern, fp):
                path_src_files.append(path)
        except re.error as err:
            if not args.quiet:
                print("ERROR: Regular Expression Error. Bad escape?")
                print(err)
                sys.exit("Exiting.")
            else:
                sys.exit(1)

    if args.verbose and args.globp:
        # extract the path name as a string for display
        print("\nThe following is a list of source files that have been filtered")
        print("with the '" + args.globp + "' glob pattern:")
        if args.ignore_case:
            print("\nNote the i-/--ignore_case option is in effect, so file name")
            print("case will ignored when considering a match.\n")
        listPrettyPrint1Col([path_src_files])
    elif args.verbose and args.regexp:
        # extract the path name as a string for display
        print("\nThe following is a list of source files that have been filtered")
        print("with the '" + args.regexp + "' regex pattern:")
        if args.ignore_case:
            print("Note the i-/--ignore_case option is in effect, so file name")
            print("case will ignored when considerig a match.")
        listPrettyPrint1Col([file.as_posix() for file in path_src_files])
    elif args.verbose:  # no glob or regex filtering
        # extract the path name as a string for display
        print("\nThe following files were found in the source path:")
        listPrettyPrint1Col([path_src_files])

    # At this point, path_src_files is a list of path objects for the files
    # we want to process.... Let's go!

    # Get a list of xmp and non-xmp files. If xmp is ignored (-ix/--ignore_xmp),
    # the xmp list object will get created, but will remain empty. This was done
    # so later checks for an empty list are less error prone that if the list
    # didn't exist.
    file_names = [] # list of full path non-xmp file names
    file_names_xmp =[] # list of full path file names with xmp extensions.
    files_xmp_data = [] # list of full path file names with xmp data
    files_no_xmp_data = [] # list of full path file names with xmp data
    files_rated = [] # list of full path file names that are rated

    def get_embedded_rating(props):
        """Given properties (props) as a list of tuples, extract the Rating
        as an integer. Return 0 if not found."""
        r_tuple = tuple(filter(lambda iterable: "xmp:Rating" in iterable, props))
        # If no rating is found, return 0
        # If a rating entry is found, then it is in a tuple with the format:
        # ("xmp:Rating", <rating value as a string>, {dict_of_entry properties})
        # We want the rating as an integer
        if r_tuple:
            # return 0 if extracted rating cannot be an integer
            try:
                return(int(r_tuple[0][1]))
            except ValueError:
                return 0
       # if we get here, the tuple was empty, and there is no rating
        return 0

    for file in path_src_files:
        if not args.ignore_xmp and file.suffix.lower() == ".xmp":
            file_names_xmp.append(file.as_posix())
        elif file.suffix.lower() != ".xmp":
            file_names.append(file.as_posix())

    for file in file_names:
        dict_xmp = file_to_dict(file)
        if dict_xmp:
            try:
                files_xmp_data.append(file)
                props = dict_xmp[xmp_consts.XMP_NS_XMP]
                print(f"Xmp namespace data found embedded in file {file}")
                rating = get_embedded_rating(props)
                if rating > 0:
                    files_rated.append(file)
            except KeyError as ke:
                print(f"No xmp namespace data found embedded in file {file}")
        else:
                print(f"No xmp data found embedded in file {file}")
                files_no_xmp_data.append(file)

    for file in file_names_xmp:
        dict_xmp = file_to_dict(file)
        if dict_xmp:
            try:
                files_xmp_data.append(file)
                props = dict_xmp[xmp_consts.XMP_NS_XMP]
                print(f"Xmp namespace data found embedded in file {file}")
                print("props:")
                pprint.pprint(props)
            except KeyError as ke:
                print(f"Xmp key error in file {file}")
        else:
                print(f"No xmp data found embedded in file {file}")
                files_no_xmp_data.append(file)
    print("\nXMP files found:")
    pprint.pprint(file_names_xmp)
    print("\nThere was XMP data was found in these files:")
    pprint.pprint(files_xmp_data)
    print("\nThere was NO XMP data found in these files:")
    pprint.pprint(files_no_xmp_data)
    print("\nThere was rating data found in these files:")
    pprint.pprint(files_rated)



# Tell python to run main if this program is executed directly (i.e. not imported)
if __name__ == "__main__":
    main()
