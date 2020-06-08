#!/usr/bin/python

##
# @file tag-files.py
# @brief Parses the cvs output of metrix++ and add, delete or modify the column 'tag' for a list of files.
# @copyright (c) 2020 Marc Stoerzel
##

import csv
import os
import io
import getopt
import sys
import fnmatch

loglevels = {"silent" : 0, "standard" : 1, "verbose" : 2}
LOGLEVEL = 1

##
# Print version information and exit
##
def printVersion():
    print "tag-files.py 0.4"
    print "Copyright (c) 2020 Marc Stoerzel"

##
# Print info how to use from command line.
##
def printUsage():
    print "usage:", sys.argv[0], "[OPTION] csv-file"
    print "Parses the cvs output of metrix++ and add, delete or modify the column 'tag' for a list of files."
    print "By default the content of csv-file is replaced by the modified content."
    print "Options and arguments:"
    print "  -h, --help             print this help message and exit"
    print "  --silent               turn on silent mode: no output except in case of error"
    print "  --verbose              enable more elaborative output"
    print "  -v, --version          print version information and exit"
    print "  -o, --outfile=OUTFILE  instead of overwriting csv-foile write content to OUTFILE"
    print "Tags can be added, deleted or modified for a single file, a group of files or a list of files."
    # print "The generic format is <OPERATOR><SELECTOR>=<TAG>, where"
    # print "  <OPERATOR> can be one of {'+', '-', '@'}"
    # print "      use '+' to add a tag"
    # print "      use '-' to remove a tag"
    # print "      use '@' to change an existing tag, in this case TAG has the format <OLDVALUE>:<NEWVALUE>"
    print "The generic format is <OPERATOR> <SELECTOR>:<TAG>, where"
    print "  <OPERATOR> can be one of {'--add' or '-a', '--remove' or '-r', '--change' or '-c'}"
    print "      use '--add' to add a tag"
    print "      use '--remove' to remove a tag"
    print "      use '--change' to change an existing tag, in this case TAG has the format <OLDVALUE>=<NEWVALUE>"
    print "  <SELECTOR> can have three different formats"
    print "      a single filename"
    print "      a valid filename qualifier as accepted by glob()"
    print "      #<listfile> filename of a file containing a list of filenames, one in each row"
    print "  <TAG> is the textual tag to add, delete or modify. The text may only contain alphanumeric characters."
    print ""
    print "Example:"
    print "  +*.bak=BACKUP add the tag 'BACKUP' to all files with extension'.bak'"
    print "  @*=BACKUP:OBSOLETE at any entry (selector=*) change the tag from BACKUP to OBSOLETE"
    print ""
    print "Attention:"
    print "Order of operations is not guaranteed to be execute in order of appearance on command line."

##
# Print a log message to stdout if loglevel is set appropriate.
#
# @param level      verbosity level of this message. If level < LOG_LEVEL the message will be printed to stdout.
# @param message    string to be printed
##
def log(level, message):
    if LOGLEVEL >= level:
        print(message)
    if level == 0:
        sys.exit()

##
# Scan commandline arguments.
# 
# Scan command line arguments and set global parameters accordingly (use '--help' on commandline to get list of
# supported command line arguments). Name of the csv-file is a mandatroy argument. It checks for readability of the csv-file.
##
def scanArguments():
    global LOGLEVEL, ADD_LIST, REMOVE_LIST, CHANGE_LIST, OUTFILE, CSV_FILE

    shortOptions = "hva:r:c:o:"
    longOptions = ["help", "version", "verbose", "silent", "add=", "remove=", "change=", "outfile="]
    opts = []
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], shortOptions, longOptions)
    except getopt.GetoptError as err:
        log(0, str(err))

    for opt, arg, in opts:
        selector = ""
        tag = ""
        old_tag = ""
        new_tag = ""
        if arg != "":
            try: 
                selector, tag = arg.split(':', 1)
            except:
                pass
        
        if opt in("--help", "-h"):
            printUsage()
            sys.exit()
        elif opt in ("--version", "-v"):
            printVersion()
            sys.exit()
        elif opt == "--verbose":
            LOGLEVEL = loglevels["verbose"]
        elif opt == "--silent":
            LOGLEVEL = loglevels["silent"]
        elif opt in ("--outfile", "-o"):
            OUTFILE = arg
        elif opt in ("--add", "-a"):
            if not tag.isalnum():
                log(0, "Tag may only consist of alphanumeric characters: " + tag)
            else: 
                ADD_LIST.append([selector.strip(), tag])
        elif opt in ("--remove", "-r"):
            if not tag.isalnum():
                log(0, "Tag may only consist of alphanumeric characters: " + tag)
            else: 
                REMOVE_LIST.append([selector.strip(), tag])
        elif opt in ("--change", "-c"):
            old_tag, new_tag = tag.split('=', 1)
            if not (old_tag.isalnum() and new_tag.isalnum):
                log(0, "Tags may only consist of alphanumeric characters: " + tag)
            else: 
                CHANGE_LIST.append([selector.strip(), old_tag, new_tag])
    if len(args) != 1:
        log(0, "Specify csv-file as mandatory argument.")
    else:
        CSV_FILE = args[0]
        if not os.path.isfile(CSV_FILE):
            log(0, "Unable to open csv-file : " + CSV_FILE)

def alternativeSyntax():    
    if len(remainder) == 0:
        log (0, "No operator specified.")

    # remainder must be parsed as list of <OPERATOR><SELECTOR>=<TAG>-tuples
    for tup in remainder:
        selector = ""
        tag = ""
        old_tag = ""
        new_tag = ""

        selector, tag = tup[1:].split('=', 1)

        if tup[0] == '+':
            if not tag.isalnum():
                log(0, "Tag must only consist of alphanumeric characters: " + tag)
            else: 
                addTag(selector, tag)
        elif tup[0] == "-":
            if not tag.isalnum():
                log(0, "Tag must only consist of alphanumeric characters: " + tag)
            else: 
                removeTag(selector, tag)
        elif tup[0] == '@':
            old_tag, new_tag = tag.split(':', 1)
            if not (old_tag.isalnum() and new_tag.isalnum):
                log(0, "Tag must only consist of alphanumeric characters: " + tag)
            else: 
                changeTag(selector, old_tag, new_tag)
        else:
            log(0, "Unrecognized operator '" + tup[0] + "'")

##
# Read in complete content of csv-file into global variable DATASETS. All consecutive operations shall operate on DATASETS.
##
def readCSVfile():
    global LOGLEVEL, ADD_LIST, REMOVE_LIST, CHANGE_LIST, OUTFILE, CSV_FILE, DATASETS
    with open(CSV_FILE, 'rb') as csv_file:
    # read in cvs output of the 'export' command of metrix++
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            DATASETS.append(row)

##
# Add a tag to the datasets in DATASETS.
#
# First check if column 'tag' already exists, append otherwise. Check if selector matches filename in first col.
# If col 'tag' was added, then append 'tag', else add 'tag' to the whitespace separated list of tags (if it is already 
# in the list of tags it will be duplicated).
##
def addTag(selector, tag):
    global LOGLEVEL, ADD_LIST, REMOVE_LIST, CHANGE_LIST, OUTFILE, CSV_FILE, DATASETS

    tag_index = 0
    needs_append = False
    log(2, "Adding tag '" + tag + "' to selector " + selector)
    line_count = 0
    for row in DATASETS:
        # first row contains header defintion
        if line_count == 0:
            # if there is no column 'tag'
            if not "tag" in row:
                # add such a row and raise marker
                row.append("tag")
                needs_append = True
            # in any case we need to know index of col 'tag'
            tag_index = row.index("tag")
        else:
            # when filename matches selectro
            if fnmatch.fnmatch(row[0], selector):
                # if we need to append a col
                if needs_append:
                    row.append(u" "+ tag)
                else:
                    # add tag to the existing content of col 'tag'
                    row[tag_index] = row[tag_index] + u" " + tag
                log(2, "  + " + row[0])
            else:
                # also for a non-matching filename we need to know if we have to add a col
                if needs_append:
                    row.append(u"")
        line_count += 1

##
# Remove a tag from the datasets in DATASETS.
#
# First check if column 'tag' already exists, append otherwise. Only if col 'tag' already existed check if 
# selector matches filename in first col. If so check if 'tag' is in the whitespace separated list and remove 
# it (only first occurence will be removed).
##
def removeTag(selector, tag): 
    tag_index = 0
    needs_append = False
    log(2, "Removing tag '" + tag + "' from selector " + selector)
    line_count = 0
    for row in DATASETS:
        # first row contains header defintion
        if line_count == 0:
            # if there is no column 'tag'
            if not "tag" in row:
                # add such a row and raise marker
                row.append("tag")
                needs_append = True
            # in any case we need to know index of col 'tag'
            tag_index = row.index("tag")
        else:
            if not needs_append:
                # when filename matches selectro
                if fnmatch.fnmatch(row[0], selector):
                    log(2, "  - " + row[0])
                    tags_list = row[tag_index].split()
                    try: 
                        index_in_tagslist = tags_list.index(tag)
                        tags_list.pop(index_in_tagslist)
                    except:
                        pass
                    row[tag_index] = ' '.join(tags_list)
        line_count += 1

##
# Replace an old_tag value by new_tag in the datasets in DATASETS.
# 
# First check if column 'tag' already exists, append otherwise. Only if col 'tag' already existed check if 
# selector matches filename in first col. If so check if 'pld_tag' is in the whitespace separated list and 
# replace by 'new_tag' (only first occurence will be replaced).
def changeTag(selector, old_tag, new_tag):
    tag_index = 0
    needs_append = False
    log(2, "Replacing tag '" + old_tag + "' by '" + new_tag + "' at selector " + selector)
    line_count = 0
    for row in DATASETS:
        # first row contains header defintion
        if line_count == 0:
            # if there is no column 'tag'
            if not "tag" in row:
                # add such a row and raise marker
                row.append("tag")
                needs_append = True
            # in any case we need to know index of col 'tag'
            tag_index = row.index("tag")
        else:
            if not needs_append:
                # when filename matches selectro
                if fnmatch.fnmatch(row[0], selector):
                    log(2, "  @ " + row[0])
                    tags_list = row[tag_index].split()
                    try: 
                        index_in_tagslist = tags_list.index(old_tag)
                        tags_list[index_in_tagslist] = new_tag
                    except:
                        pass
                    row[tag_index] = ' '.join(tags_list)
        line_count += 1

ADD_LIST = []
REMOVE_LIST = []
CHANGE_LIST = []
DATASETS = []
## filename of the input file
CSV_FILE = ""
## Filename of the output file
OUTFILE = ""
# OUTPUT = []

##
# Iterate through 'theList': for every entry check if 'selector' starts with '#', if so 
# treat it as a filename. Open respective file and read line by line. Each line results 
# in a new entry to the returned list, with the line content as new selector.
def expandedList(theList):
    ret = []
    for entry in theList:
        selector = entry[0]
        if selector[0] == '#':
            try:
                selector_file = open(selector[1:], "r")
                for sel_from_file in selector_file:
                    newEntry = [sel_from_file]
                    newEntry.extend(entry[1:])
                    ret.append(newEntry)
                selector_file.close()
            except:
                log(0, "Referenced selector file not accesssible: " + selector[1:])
        else:
            ret.append(entry)
    return ret

scanArguments()
readCSVfile()
if len(ADD_LIST) > 0:
    for selector, tag in expandedList(ADD_LIST):
        addTag(selector, tag)
if len(REMOVE_LIST) > 0:
    for selector, tag in expandedList(REMOVE_LIST):
        removeTag(selector, tag)
if len(CHANGE_LIST) > 0:
    for selector, old_tag, new_tag in expandedList(CHANGE_LIST):
        changeTag(selector, old_tag, new_tag)

if OUTFILE == "":
    OUTFILE = CSV_FILE

with open(OUTFILE, "w") as csv_out:
    writer = csv.writer(csv_out)
    writer.writerows(DATASETS)
csv_out.close()