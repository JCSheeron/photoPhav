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
import traceback
import os
from sys import exit as sys_exit

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
from libxmp import consts as xmp_consts  # constants

# Local application and user library imports
from bpsPrettyPrint import listPrettyPrint1Col

# Note: May need PYTHONPATH (set in ~/.profile?) to be set depending
# on the location of the imported files


# Main function to execute when script is run
def main():
    """
    PhotoPhav (as in Photo Favorites) will create links to favorite images
    based on 'star' and/or color ratings.

    A source directory will be searched for image files. For each image file
    found, inspect the xmp metadata. If the star rating is above
    a value (default: 1) create a link to the file in the destination
    directory. If the color rating is above a value (TODO: What Value), then
    create a link to the file in the destination directory.

    The star rating threshold can be specified with the -S/--star_rating <rating>
    option, where rating is 1-5. Values at or above the indicated value will be
    included. Default: 1. Mutually exclusive with the -s/--ignore_star option.

    The star rating will be ignored if the -s/--ignore_star option is given.
    Mutually exclusive with the -S/--star_rating option.

    The color label threshold can be specified with the -C/--color_label <rating>
    option where label is 1-10 ???. Values at or above the indicated value will be
    included. Mutually exclusive with the -c/--ignore_color option.
    **Default value??** NOTE: Not yet supported.

    The color label will be ignored if the -c/--ignore_color option is given.
    Default: true (ignore color rating by default). Mutually exclusive with the
    -C/--color_label option.

    A source directory can be provided with the -I/--source_dir <path> option
    to specify the directory to use for the source images. If this option is
    not provided, the working directory will used as the source directory.

    A destination directory can be provided with the -d/-D/--dest_dir <path>
    option to specify the directory to use for the link destination. If this
    option is not provided, a 'favorites' sub directory in the working
    directory will first be created if it does not exist, and will used for
    the destination path.

    The -r/-R/--recursive option searches the source directory recursively. If
    images are found in sub folders, the same directory structure will be used
    for the destination directory structure.

    The -F/--file_priority option will give priority to information embedded
    in the image file. Without this option, priority is given to a xmp
    'sidecar' file if one exists, and the embedded xmp data would only be used
    if the xmp sidecar file does not exist or can't be read or for some reason
    isn't usable. Mutually exclusive with -f/--ignore_file option.

    The -f/--ignore_file option will ignore xmp data embedded in the image
    file, even if it exists. Mutually exclulsive with -F/--file_priority option.

    The -x/--ignore_xmp option will ignore xmp sidecar file(s), even if they
    are present.

    The -g/--globp <pattern> option allows files to be searched using a glob
    pattern. Mutually exclusive with the -e/--regexp option.

    The -e/--regexp <pattern> option allows files to be searched using a
    regular expression. Mutually exclusive with the -g/--globp option.

    The -i/--ignore_case option ignores file name case when matching using a glob
    pattern or regex pattern. This option is ignored if neither the -g or -e,
    patterns are specified.

    The -v/--verbose option increases output messaging. Mutually exclusive
    with -q and -w.

    The -q/--quiet option eliminates output messaging, even in the event of
    errors. Mutually exclusive with -v and -w.

    The -w/--show_ew show errors and warning option.
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
    sr_group = parser.add_mutually_exclusive_group(required=False)
    sr_group.add_argument(
        "-S",
        "--star_rating",
        default=1,
        type=int,
        choices=range(1, 6),  # 1-5
        metavar="rating",
        help="Star rating. Values equal or greater are considered Favorites \
and a link will be created. Default value is 1, so any stared image is a favorite. \
Mutually exclusive with the -s/--ignore_star rating.",
    )
    sr_group.add_argument(
        "-s",
        "--ignore_star",
        action="store_true",
        help="Ignore star ratings \
if set. Mutually exclusive with the -S/--star_rating option.",
    )
    # color label
    cl_group = parser.add_mutually_exclusive_group(required=False)
    cl_group.add_argument(
        "-C",
        "--color_label",
        default=1,
        type=int,
        choices=range(1, 11),  # 1-10
        metavar="label",
        help="Color label. Values equal are considered Favorites \
and a link will be created. Mutually exclusive with the -c/--ignore_color option.",
    )
    cl_group.add_argument(
        "-c",
        "--ignore_color",
        action="store_true",
        help="Color label will be ignored if this option is given. Mutually \
exclusive with the -C/-color_label option. NOTE: Not yet supported -- color \
lables are always ignored.",
    )
    # source dir
    parser.add_argument(
        "-I",
        "--source_dir",
        default=".",
        metavar="path",
        help="Source directory. Look in this directory for image files. Omit \
the option or specify '.' to use the working directory.",
    )
    # destination dir
    parser.add_argument(
        "-d",
        "-D",
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
        "-F",
        "--file_priority",
        action="store_true",
        help="Give priority to information embedded in the image file. Without \
this option, priority is given to a xmp 'sidecar' file if one exists, and the \
embedded xmp data would only be used if the xmp sidecar file does not exist or \
can't be read or for some reason isn't usable. Mutually exclusive with \
-f/--ignore_file option.",
    )
    fx_pattern.add_argument(
        "-f",
        "--ignore_file",
        action="store_true",
        help="Ignore xmp data embedded in the image file, even if it exists. \
Mutually exclulsive with -F/--file_priority option.",
    )
    parser.add_argument(
        "-x",
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
        "-w",
        "--show_ew",
        action="store_true",
        help="Show only errors and warnings.",
    )
    # parse the arguments
    args = parser.parse_args()

    # At this point, the arguments will be:
    # Argument              Type        Default
    # Path/file related:
    # args.source_dir       string      .
    # args.destination_dir  string      favorites
    # args.recursive        bool        False
    # args.ignore_case      bool        False   case sensitive by default
    # args.globp            string      None    (globp | regexp)
    # args.regexp           string      None
    # Rating related:
    # args.star_rating      int         1
    # args.ignore_star      bool        False   use star ratings >= 1 by default
    # args.color_rating     int         1
    # args.ignore_color     bool        False   Forced True for now to ignore color rating
    # args.file_priority    bool        False
    # args.ignore_file      bool        False
    # args.ignore_xmp       bool        False
    # Output related:
    # args.verbose          bool        False   Increase messaging (v | q | w)
    # args.quiet            bool        False   No messaging, not even for errors
    # args.show_ew          bool        False   Show errors and warnings only

    # Force ignore_color to be true for now
    args.ignore_color = True

    # check for --ignore_file and --ignore_xmp. If both options are present
    # there is no action. Warn (if not quiet) and quit. These are not treated
    # as mutually exclusive, becuase --file_priority and --ignore_file are already
    # in a mutually exclusive group, so I don't think --ignore_file and
    # --ignore_xmp can be in a different mutually exclusive group. Furthermore
    # note that --file_priority and --ignore_xmp is valid, so --ignore_xmp can't
    # be added to the exiting file mutually exclusive group.
    # Check for the case manually.
    if args.ignore_file and args.ignore_xmp:
        if not args.quiet:
            print(
                "\nWARNING: -f/--ignore_file and -x/--ignore_xmp options are both \
selected. This will result in no action as there is no data to act on, and is \
probably not what was intended."
            )
        sys_exit(2)

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
    if args.verbose:
        print("The source path is:")
        print(path_src.resolve())
        print("The destination path is:")
        print(path_dest.resolve())

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

    # Get the files only -- exclude the directories. Use a set since values are
    # unique and should not change
    path_all_files = {file for file in contents if file.is_file()}
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

    path_src_files = set()  # This will hold the filtered (final) list of path objects
    # filter out files based on regex filter
    for path in path_all_files:
        fp = path.as_posix()  # get full path name
        try:
            if re.match(re_pattern, fp):
                path_src_files.add(path)
        except re.error as err:
            if not args.quiet:
                print("ERROR: Regular Expression Error. Bad escape?")
                print(err)
                sys_exit("Exiting.")
            else:
                sys_exit(1)

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

    # Get a list of xmp and non-xmp files. Store path objects so full compliment
    # of info is avail later. If xmp is ignored (-ix/--ignore_xmp),
    # the xmp list object will get created, but will remain empty. This was done
    # so later checks for an empty list cover the no file case and the ignore
    # case, and are less error prone that if the list didn't exist.
    image_paths = set()  # list of full path non-xmp file names
    image_paths_xmp = set()  # list of full path file names with xmp suffix
    for file in path_src_files:
        if not args.ignore_xmp and file.suffix.lower() == ".xmp":
            image_paths_xmp.add(file)
        elif file.suffix.lower() != ".xmp":
            image_paths.add(file)

    # At this point, image_paths[] will have all the non-xmp files, and
    # image_paths_xmp[] will have the *.xmp file name,
    # or will be empty if there are no xmp files or will also be empty if xmp
    # is ignored (-x/--ignore_xmp)

    # Create a helper function to retreive the rating from an xmp property and
    # return it as a function.
    def get_embedded_rating(props: list[tuple]):
        """Given properties (props) as a list of tuples, extract the Rating
        as an integer. Return 0 if not found or if can't be converted to an int."""
        r_tuple = tuple(filter(lambda iterable: "xmp:Rating" in iterable, props))
        # If no rating is found, return 0
        # If a rating entry is found, then it is in a tuple with the format:
        # ("xmp:Rating", <rating value as a string>, {dict_of_entry properties})
        # We want the rating as an integer
        if r_tuple:
            # return 0 if extracted rating cannot be an integer
            try:
                return int(r_tuple[0][1])
            except ValueError:
                return 0
        # if we get here, the tuple was empty, and there is no rating
        return 0

    # Create helper function to test if a file has an associated xmp file
    def has_xmp(fname: str, xmp_files: set[Path]):
        """Given a file name and a set of xmp files, see if the file name matches
        an xmp filename, less the suffixes. e.g. foo.jpg and foo.xmp would be
        a match."""
        # strip off the extensions and if there is a match, the set will have a member
        return (
            len(
                {
                    fn
                    for fn in xmp_files
                    if fn.as_posix().rsplit(".", 1)[0] == fname.rsplit(".", 1)[0]
                }
            )
            > 0
        )

    # Create helper function to return the file name of the associated xmp file
    def get_xmp_filename(fname: str, xmp_files: set[Path]):
        """Given a file name and a set of xmp files, return the name of the
        corresponding xmp file name. Nominally this is the same name as the
        file name, except the suffix would be '.xmp' or '.XMP'"""
        # strip off the extensions and if there is a match, return the full xmp
        # file name. If there is not match, xname will be the empty set, and
        # return an empty stiring.
        xname = {
            fn.as_posix()
            for fn in xmp_files
            if fn.as_posix().rsplit(".", 1)[0] == fname.rsplit(".", 1)[0]
        }
        if not xname:
            return ""

        # if we get here, there is something to return
        return list(xname).pop()  # return the only memeber of the set

    # Create helper function to copy group, owner, and permissions of a dir
    def cp_ogp(src_path: Path, dest_path: Path):
        """Copy the owner, group, and permissions from a source path."""
        dest_str = dest_path.resolve().as_posix()
        src_stat = os.stat(src_path.resolve().as_posix())
        os.chown(dest_str, src_stat.st_uid, src_stat.st_gid)
        os.chmod(dest_str, src_stat.st_mode)

    # Create helper function to create a link.
    def create_link(target_path: Path, dest_path: Path, src_path: Path):
        """Given a target path, create a symbolic link in the destination
        directory. The source directory structure that comes after the source
        path will be retained, so the source path is needed for reference.
        For example, if:
        target_path: /a/b/c/fav1.jpg
        source_path: /a/b
        dest_path:   /e/f/g
        The above would mean the target was in the 'c' sub-directory of the
        source, and this would be retained on the destination side, so the
        link created would be /e/f/g/c/fav1.jpg."""
        try:
            # Get the part of the target path that is relative to the source
            # path. Append this to the destination to make the link path, and
            # create the link
            rel_path = target_path.resolve().relative_to(src_path.resolve())
            link_path = dest_path.joinpath(rel_path).resolve()
            # print("\ncreate_link() called")
            # print(f"Target Path: {target_path.resolve()}")
            # print(f"Src Path: {src_path.resolve()}")
            # print(f"Src Path Short: {src_path}")
            # print(f"Dest Path: {dest_path.resolve()}")
            # print(f"Dest Path Short: {dest_path}")
            # print(f"Rel Path: {rel_path}")
            # print(f"Link Path: {link_path.resolve()}")
            # print(f"Link Path Short: {link_path}")
            # print(f"Parent Path: {rel_path.parent}")

            # See if the parent of the target link exists. If it does not exist,
            # make it, along with any necessary parent directories. For any
            # dirctories made, copy the owner, group, and permissions from the
            # target directories.
            if not link_path.parent.is_dir():
                # The link target dir (parent of the symbolic link we want to
                # make) does not exist. rel_path gives us the difference between
                # to 'root' of the destination and the link path. Walk the
                # rel_path and create any needed subdirectories. These are made
                # individually so the owner, group, and permissions of each can
                # be made to match the corresponding sub-directory in the source
                # directory structure. The path.parents property includes the
                # '.' case so this loop will also make the root destination
                # directory if it does not exist.
                if args.verbose:
                    print("Link destination directory does not exist.")
                    print("Creating the necessary link destination directories.")
                # Go thru the directories in order of shallowest to deepest.
                # If a directory does not exist, create it. Some sub-directories
                # may already exist.
                for p in reversed(rel_path.parents):
                    dpath = dest_path.joinpath(p).resolve()
                    if not dpath.is_dir():
                        if args.verbose:
                            print(f"Directory {dpath} does not exit. Creating it.")
                        dpath.mkdir()
                        cp_ogp(path_src, dpath)

            # Make the link
            os.symlink(target_path.resolve(), link_path.resolve())

        except Exception:
            print("***ERROR: Exeption in create_link()")
            traceback.print_exc()

    for path in image_paths:
        # Default behavior is xmp priority, so get the rating from xmp if there is one
        # and if not, check for data embedded in the file. Otherwise check the other
        # combinations
        ifn = path.as_posix()  # use the full path file name in this case
        if not args.file_priority and not args.ignore_file and not args.ignore_xmp:
            if has_xmp(ifn, image_paths_xmp):
                # There is an xmp file for this image file. Use it.
                ifx = get_xmp_filename(ifn, image_paths_xmp)
                try:
                    dict_xmp = file_to_dict(ifx)
                    if dict_xmp:
                        props = dict_xmp[xmp_consts.XMP_NS_XMP]
                        rating = get_embedded_rating(props)
                        if rating > 0:
                            create_link(path, path_dest, path_src)
                except Exception:
                    pass
            else:
                # There is no xmp file for this image file. Use the embedded
                # data if it exists.
                dict_xmp = file_to_dict(ifn)
                if dict_xmp:
                    # There is embedded xmp data found. Try to get a rating.
                    try:
                        props = dict_xmp[xmp_consts.XMP_NS_XMP]
                        rating = get_embedded_rating(props)
                        if rating > 0:
                            create_link(path, path_dest, path_src)
                    except Exception:
                        pass
        elif (not args.file_priority and args.ignore_xmp) or args.file_priority:
            # If file priority or ignore_xmp, then initially check the data
            # embedded in the file for a rating. If there is no data, then try
            # the xmp file if it exists and should not be ignored.
            dict_xmp = file_to_dict(ifn)
            if dict_xmp:
                # There is embedded xmp data found. Try to get a rating.
                try:
                    props = dict_xmp[xmp_consts.XMP_NS_XMP]
                    rating = get_embedded_rating(props)
                    if rating > 0:
                        create_link(path, path_dest, path_src)
                except Exception:
                    pass
            elif not args.ignore_xmp and has_xmp(ifn, image_paths_xmp):
                # There was no embedded xmp data found, but we are not ignoring
                # xmp, and there is an xmp file for this image file. Use it.
                ifx = get_xmp_filename(ifn, image_paths_xmp)
                try:
                    dict_xmp = file_to_dict(ifx)
                    if dict_xmp:
                        props = dict_xmp[xmp_consts.XMP_NS_XMP]
                        rating = get_embedded_rating(props)
                        if rating > 0:
                            create_link(path, path_dest, path_src)
                except Exception:
                    pass
        elif args.ignore_file:
            # Ignore the embedded data in the image file, and use the xmp
            # file if it exists
            if has_xmp(ifn, image_paths_xmp):
                # There is an xmp file for this image file. Use it.
                ifx = get_xmp_filename(ifn, image_paths_xmp)
                try:
                    dict_xmp = file_to_dict(ifx)
                    if dict_xmp:
                        props = dict_xmp[xmp_consts.XMP_NS_XMP]
                        rating = get_embedded_rating(props)
                        if rating > 0:
                            create_link(path, path_dest, path_src)
                except Exception:
                    pass
        else:
            # Should not get here. Here for completeness and documentation.
            # Print a message and leave.
            print(
                "ERROR: Argument or logic error. Not sure which xmp data \
to process. Exiting"
            )
            sys_exit(3)


# Tell python to run main if this program is executed directly (i.e. not imported)
if __name__ == "__main__":
    main()
