#!/usr/bin/python

##
# @file canalyse.py
# @copyright (c) 2020 Marc Stoerzel
# @brief Parses the csv output of 'metrix++ export' to generate sourcecode HTML-files and optionally a Javascript datafile.
#
#  include{doc} ../README.md
##

import csv
import os
import math
import cgi
import io
import getopt
import sys
import ast

## path from where to start analysis of sourceceode
SRCPATH = "./../../../SW/Public"
## sourcecode is assumed to belong to a module (or application); adds as suffix to SRCPATH
MODULE_BASE = "30_Appl"
## directory to store intermediate files generated from data collected by metrix++
DATADIR_REL = "./data"
## directory to store generated html files to
REPORTDIR_REL = "./html"
## path where highlight.js is installed to
HIGHLIGHT_REL = "./highlight"
## stylesheet to use by highlight.js for sourcecode highlighting
HIGHLIGHT_CSS = "styles/vs.css"
## html styling and diagram styling settings get here
STYLE_REL = "./style"
## dictionary assigning criteria mnenonics to more human readable format 
CRITERIA_LABELS = {"std.code.complexity.cyclomatic" : "cyclomatic complexity", \
"std.code.filelines.comments" : "lines of comment", \
"std.code.lines.code" : "lines of code"}
GEN_DATAFILE_ONLY = False

loglevels = {"silent" : 0, "standard" : 1, "verbose" : 2}
LOGLEVEL = 1

##
# Create the opening section of an HTML file.
#
# A file of name \c path + os.sep + \c filename will be created (existing file will be overwritten) with reference to the
# generic stylesheet \c style.css and the stylesheet of the Highlight.js package referenced by \c HIGHLIGHT_CSS
#
# @param path       absolute or relative path to the HTML file to be generated. (An OS specific path separator, i. e.
#                   '/' under Linux, '\' under Windows, etc. will be appended)
# @param filename   filename of the HTML file to be generated, it shall end by '.html' or alike
##
def createHTMLfile(path, filename):
    if not os.path.exists(path):
        os.makedirs(path)
    path_rel = os.path.relpath(os.curdir, path)
    log(2, "Creating HTML file " + path +  os.sep + filename)
    with io.open(path +  os.sep + filename, "w") as ofile:
        ofile.write(u"<!DOCTYPE html> \
  <html>      \n \
	<head>  \n \
	  <title>")
        ofile.write(os.path.splitext(filename)[0] + u"</title>")
        ofile.write(u"	      <link rel='stylesheet' type='text/css' href='" + path_rel + os.sep + STYLE_REL + os.sep + u"/style.css'>\n")
        ofile.write(u"	      <link rel='stylesheet' type='text/css' href='" + path_rel + os.sep + HIGHLIGHT_REL + os.sep + HIGHLIGHT_CSS + u"'> \n \
    <script src='" + path_rel + os.sep + HIGHLIGHT_REL + os.sep + u"highlight.pack.js'></script>     \n \
    <script>hljs.initHighlightingOnLoad();</script>  \n \
	</head>     \n \
  <body><span id='" + filename + u"@top'></span>")
    ofile.close()

##
# Append the closing section to an HTML file.
#
# It is assumed that the file \c path + os.sep + \c filename exists. To the existing file the closing HTML-tags are appended.
#
# @param path       absolute or relative path to the HTML file 
# @param filename   filename of the HTML file 
##
def finalizeHTMLfile(path, filename):
    with io.open(path + os.sep + filename, "a") as ofile:
        ofile.write(u"<script>var elem = document.getElementById('NavSection'); \n \
	elem.addEventListener('change', JumpToSection); \n \
	function JumpToSection() { \n \
		window.location.href = '#' + document.getElementById('NavSection').value; \n \
    }</script>")
        ofile.write(u"  </body>\n  </html>")
    ofile.close()

##
# Append portions of sourcecode to an existing HTML file.
# 
# It is assumed that the file \c path + os.sep + \c destfilename exists. To this file a portion of the sourcecode from file srcfilename
# is copied. The portion is defined by line_start and line_end (both incl.). Each line is prepended by HTML tags to show linenumbers. The 
# complete portion is prepended by a header, which defines an anchor point and shows criterias and respective labels.
##
def copyCode2HTML(path, destfilename, srcfilename, region, type, line_start, line_end, criterias, labels):
    with io.open(srcfilename, "r", errors='replace') as srcfile:
        src_txt = srcfile.readlines()
        with io.open(path + os.sep + destfilename, "a") as destfile:
            destfile.write(u"<span class='detail_wrapper' id='" + destfilename + u"@" + str(line_start) + u"-" + str(line_end) + u"'>\n")
            log(2, type + ": " + region + u" (" + str(line_start) + u" - " + str(line_end) + ")")
            destfile.write(u"<span class='detail_type_region'>" + type + u": " + region + u" (" + str(line_start) + u" - " + str(line_end) + ")</span>\n")
            i = 0
            for criteriaValue in criterias:
                if not criteriaValue == "":
                    if i < len(labels):
                        if CRITERIA_LABELS.has_key(labels[i]):
                            destfile.write(u"<span class='detail_" + labels[i].replace(".", "_") + u"'>")
                            destfile.write(CRITERIA_LABELS[labels[i]] + u": " + str(criteriaValue) + u"</span>\n")
                i += 1
            if region == "" or region == "__global__":
                # __global__ line count bug
                lastline = line_end -1
            else:
                lastline = line_end
            destfile.write(u"<button onClick=\"window.location.href='#" + destfilename + u"@top'\">top &#x25B4;</button></span>\n")
            destfile.write(u"    <pre class='sourcecode'><code class='#language-c'>\n")
            for linenum in range(line_start -1, lastline):
                destfile.write(u"<span title='" + str(linenum +1) + u"'>")
                destfile.write(cgi.escape(src_txt[linenum]))
                destfile.write(u"</span>")
            destfile.write(u"    </code></pre>")
        destfile.close()
    srcfile.close()

##
# Generates a javascript file consisting of the detailed data definitions as collected in \c filelist.
#
# Creates the file \c datadir + os.sep + \modulebase + '.js' (existing file will be overwritten). Content of the file 
# is definition of a single array \c combined. Each entry is an array of the following structure:
# 
# [html_path, html_filename, filename, region, type, line_start, line_end, rest of the row (i. e. all criteria values)]
# 
# Where (srcpath + os.sep + modulebase) is stripped from filename.
#
# @param datadir        absolute or relative path to the javascript file
# @param modulebasse    basename of the jjavascript file, will be prepended by '.js'
# @param srcpath        absolute or relative path to the sourcefiles; stored filname will be stripped from (srcpath + os.sep + modulebase)
##
def generateDetailedDatafile(datadir, modulebase, srcpath):
    log(2, "Generating detailed data file " + datadir + os.sep + modulebase + ".js")
    with io.open(datadir + os.sep + modulebase + ".js", "w") as moduleJSfile:
        moduleJSfile.write(u"var combined = [")
        # filelist is a dictionary with key=filename and value is a list of entries
        # each entry itself is a list [html_path, html_filename, filename, region, type, line_start, line_end, rest of the row (i. e. all criteria values)
        for fileData in FILELIST.values():
            # iterate over all files in the filelist
            count = 0
            for fileEntry in fileData:
                # each file (key) might point to a list of fileData
                count += 1
                # iterate over each entry for every file
                dataPerFile = ""
                filename = fileEntry[2].replace(srcpath + os.sep + modulebase, "")
                criteriaValues = ""
                for val in fileEntry[8]:
                    criteriaValues += str(val) + u", "
                criteriaValues = criteriaValues[:-2]    # remove trailig ", "
                dataPerFile += (u"['" + filename + u"', '" + fileEntry[3] + u"', '" + fileEntry[4] + u"', '" + str(fileEntry[5]) + u"', " \
                    + u", " + str(fileEntry[6]) + u", " + criteriaValues + u"],\n")
                if count == len(FILELIST.values()):
                    dataPerFile = dataPerFile[:-1]      # remove trialing ","
                moduleJSfile.write(dataPerFile)
        moduleJSfile.write(u"];\n")
    moduleJSfile.close()

##
# Read and parse a csv file.
#
##
def readCSVfile(datapath, module_base):
    log(1, "Opening database file " + datapath + os.sep + module_base + '.csv')
    with open(datapath + os.sep + module_base + '.csv') as csv_file:
        # read in cvs output of the 'export' command of metrix++
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # first row contains header defintion
            if line_count == 0:
                criterias = row[6:]
                for i in range(0, len(criterias)):      # 'for criteria in criterias': not possible to modify criteria
                    criterias[i] = criterias[i].replace(':', '.')
                log(2, "Processing following criterias: ")
                log(2, criterias)
            else:
                filename = row[0]
                codefilename = filename.replace(SRCPATH, "")
                html_path = REPORTDIR_REL + (os.path.split(codefilename)[0]).replace(module_base, "")
                html_filename = os.path.split(filename)[1] + ".html"
                region = row[1]
                metrix_type = row[2]
                modified = row[3]
                criteria_values = row[6:]
                for c in range(0, len(criteria_values)):
                    if criteria_values[c] == "":
                        criteria_values[c] = 0
                
                try:
                    line_start = int(row[4])
                    line_end = int(row[5])
                except:
                    line_start = -1
                # only parse entries with a valid line_start
                if (line_start > -1):
                    # Add an entry to filelist with key=filename and value=an empty list
                    if not filename in FILELIST:
                        FILELIST[filename] = []

                    if metrix_type == "global":
                        for each in FILELIST[filename]:
                            # iterate over all entries of current filename
                            if each[4] == "file":
                                for c in range(0, len(criteria_values)):
                                    old_values = each[8]
                                    old_values[c] = int(criteria_values[c]) + int(old_values[c])
                    
                    if metrix_type == "file":
                        for each in FILELIST[filename]:
                            # iterate over all entries of current filename
                            if each[4] == "global":
                                for c in range(0, len(criteria_values)):
                                    old_values = each[8]
                                    old_values[c] = int(criteria_values[c]) + int(old_values[c])
                                each[4] = "file"
                    
                    FILELIST[filename].append([html_path, html_filename, filename, region, metrix_type, modified, line_start, line_end, criteria_values])
            line_count += 1
        log(2, "Read " + str(line_count) + " entries.")
    csv_file.close()
    return criterias

##
# Print version information and exit
##
def printVersion():
    print "canalyse.py 0.4 "
    print "Copyright (c) 2020 Marc Stoerzel"

##
# Print info how to use from command line.
##
def printUsage():
    print "usage:", sys.argv[0], "[OPTION]"
    print "Parses the cvs output of metrix++ to generate HTML-files and optionally a Javascript datafile."
    print "Options and arguments:"
    print "  -h, --help                 print this help message and exit"
    print "  --silent                   turn on silent mode: no output except in case of error"
    print "  --verbose                  enable more elaborative output"
    print "  -v, --version              print version information and exit"
    print "  --gen-datafile-only        generate only javascript data file (no HTML is generated)"
    print "  -s, --srcpath=DIR          directory containing the sourcecode root folder"
    print "                                 defaults to:", SRCPATH
    print "  -m, --modulebase=DIR       shall be name of the sourcecode's root folder"
    print "                                 defaults to:", MODULE_BASE
    print "  -d, --datadir=DIR          directory containing the raw data of the metrix++ export"
    print "                                 defaults to:", DATADIR_REL
    print "  -r, --reportdir=DIR        the output directory of the generated html files"
    print "                                 defaults to:", REPORTDIR_REL
    print "  -i, --installdir=DIR       location where 'highlight' package is installed"
    print "                                 defaults to:", HIGHLIGHT_REL
    print "  -c, --highlight-css=FILE   filename of CSS file to be used for syntax highlighting"
    print "                                  defaults to:", HIGHLIGHT_CSS
    print "  -y, --styledir=DIR         directory containing the generic style.css file"
    print "                                  defaults to:", STYLE_REL
    print "  -l, --criteria-labels=DICT dictionary, where "
    print "                                 key = mnemnonic of the criteria and "
    print "                                 value = human readable label"
    print "                                 defaults to:", CRITERIA_LABELS

##
# Print global paramter settings.
##
def dumpParameters():
    print "Parameters set as"
    print "  --srcpath         =", SRCPATH
    print "  --modulebase      =", MODULE_BASE
    print "  --datadir         =", DATADIR_REL
    print "  --reportdir       =", REPORTDIR_REL
    print "  --installdir      =", HIGHLIGHT_REL
    print "  --highlight-css   =", HIGHLIGHT_CSS
    print "  --styledir        =", STYLE_REL
    print "  --criteria-labels =", CRITERIA_LABELS

##
# Print a log message to stdout if loglevel is set appropriate.
#
# @param level      verbosity level of this message. If level < LOG_LEVEL the message will be printed to stdout.
# @param message    string to be printed
##
def log(level, message):
    if LOGLEVEL >= level:
        print(message)
    if (level) < 0:
        sys.exit(-level)

##
# Scan commandline arguments.
# 
# Scan command line arguments and set global parameters accordingly (use '--help' on commandline to get list of
# supported command line arguments).
##
def scanArguments():
    global LOGLEVEL, SRCPATH, MODULE_BASE, DATADIR_REL, REPORTDIR_REL, HIGHLIGHT_REL, HIGHLIGHT_CSS, STYLE_REL, CRITERIA_LABELS, GEN_DATAFILE_ONLY
    shortOptions = "hvs:m:d:r:i:c:y:l:"
    longOptions = ["help", "version", "verbose", "silent", "srcpath=", "modulebase=", "datadir=", \
        "reportdir=", "installdir=", "highlight-css=", "styledir=", "criteria-labels=", "gen-datafile-only"]
    opts = []
    remainder = []

    try:
        opts, remainder = getopt.gnu_getopt(sys.argv[1:], shortOptions, longOptions)
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)
        printUsage()
        sys.exit()

    for o, a, in opts:
        if o in("--help", "-h"):
            printUsage()
            sys.exit()
        elif o in ("--version", "-v"):
            printVersion()
            sys.exit()
        elif o == "--verbose":
            LOGLEVEL = loglevels["verbose"]
        elif o == "--silent":
            LOGLEVEL = loglevels["silent"]
        elif o == "-s" or o == "--srcpath":
            SRCPATH = a
        elif o == "-m" or o == "--modulebase":
            MODULE_BASE = a
        elif o == "-d" or o == "--datadir":
            DATADIR_REL = a
        elif o == "-r" or o == "--reportdir":
            REPORTDIR_REL = a
        elif o == "-i" or o == "--installdir":
            HIGHLIGHT_REL = a
        elif o == "-c" or o == "--highligh-css":
            HIGHLIGHT_CSS = a
        elif o == "-y" or o == "--styledir":
            STYLE_REL = a
        elif o == "-l" or o == "--criteria-labels":
            try:
                CRITERIA_LABELS = ast.literal_eval(a)
            except:
                log(-1, "Error while trying to parse following argument for 'criteria-labels':" + str(a))
        elif o == "--gen-datafile-only":
            GEN_DATAFILE_ONLY = True

        if len(remainder) > 0:
            log(-1, "Unrecogniozed argument: " + str(remainder))

##
# Iterate over the global filelist and generate an HTML-file for each entry.
#
##
def generateHTMLfiles(criterias):
    # filelist is a dictionary with key=filename and value is a list of entries
    #                                  0            1           2         3        4           5           6          7       8...
    # each entry itself is a list [html_path, html_filename, filename, region, metrix_type, modified, line_start, line_end, rest of the row (i. e. all criteria values)
    line_count = 0
    for entries in FILELIST.values():
        # iterate over all files in the filelist
        line_count += 1
        fileData = entries[0]
        # create a HTML file only once per file
        createHTMLfile(fileData[0], fileData[1])
        with io.open(fileData[0] + os.sep + fileData[1], "a") as ofile:
            ofile.write(u"<span id='details_head'>Browse details of file " + fileData[1].replace(".html", "") + u" <select id='NavSection' onChange='JumpToSection'>")
            for fileData in entries:
                # iterate over each entry for every file
                ofile.write(u"<option value='" + fileData[1] + u"@" + str(fileData[6]) + u"-" + str(fileData[7]) + u"'s>")
                ofile.write(fileData[4] + u": " + fileData[3] + u"(" + str(fileData[6]) + u" - " + str(fileData[7]) + u")</option>\n")
            ofile.write(u"</select></span>")
        ofile.close()
        for fileData in entries:
            # iterate over each entry for every file
            copyCode2HTML(fileData[0], fileData[1], fileData[2], fileData[3], fileData[4], fileData[6], fileData[7], fileData[8], criterias)
        finalizeHTMLfile(fileData[0], fileData[1])
    log(1, str(line_count) + " files processed.\n")

FILELIST = dict()
scanArguments()
if LOGLEVEL >= 2:
    dumpParameters()
criterias = readCSVfile(DATADIR_REL, MODULE_BASE)
if not GEN_DATAFILE_ONLY:
    generateHTMLfiles(criterias)
generateDetailedDatafile(DATADIR_REL, MODULE_BASE, SRCPATH)