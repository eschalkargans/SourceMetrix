#!/usr/bin/python

##
# @file mxpp-report2js.py
# @copyright (c) 2020 Marc Stoerzel
# @brief Parses the 'view --format=python' output of metrix++ to generate a Javascript datafile.
#
##

import os
import io
import getopt
import sys
import ast

SRCPATH = "./../../../SW/Public"
MODULE_BASE = "30_Appl"
REPORTDIR_REL = "./html"
DATADIR_REL = "./data"

loglevels = {"silent" : 0, "standard" : 1, "verbose" : 2}
LOGLEVEL = 1

##
# Print version information and exit
##
def printVersion():
    print "mpp-view2js.py 0.1 "
    print "Copyright (c) 2020 Marc Stoerzel"

##
# Print info how to use from command line.
##
def printUsage():
    print "usage:", sys.argv[0], "[OPTION]"
    print "Parses the 'view --format=python' of metrix++ to generate Javascript datafiles."
    print "Options and arguments:"
    print "  -h, --help                 print this help message and exit"
    print "  --silent                   turn on silent mode: no output except in case of error"
    print "  --verbose                  enable more elaborative output"
    print "  -v, --version              print version information and exit"
    print "  -s, --srcpath=DIR          directory containing the sourcecode root folder"
    print "                                 defaults to:", SRCPATH
    print "  -m, --modulebase=DIR       shall be name of the sourcecode's root folder"
    print "                                 defaults to:", MODULE_BASE
    print "  -d, --datadir=DIR          directory containing the raw data of the metrix++ export"
    print "                                 defaults to:", DATADIR_REL

##
# Print global paramter settings.
##
def dumpParameters():
    print "Parameters set as"
    print "  --srcpath         =", SRCPATH
    print "  --modulebase      =", MODULE_BASE
    print "  --datadir         =", DATADIR_REL

##
# Print a log message to stdout if loglevel is set appropriate.
#
# @param level      verbosity level of this message. If level < LOG_LEVEL the message will be printed to stdout.
# @param message    string to be printed
##
def log(level, message):
    if LOGLEVEL >= level:
        print(message)

##
# Scan commandline arguments.
# 
# Scan command line arguments and set global parameters accordingly (use '--help' on commandline to get list of
# supported command line arguments).
##
def scanArguments():
    global LOGLEVEL, SRCPATH, MODULE_BASE, REPORTDIR_REL, DATADIR_REL, CRITERIA_LABELS
    shortOptions = "hvs:r: m:d:l:"
    longOptions = ["help", "version", "verbose", "silent", "srcpath=", "reportdir=", "modulebase=", "datadir=", "criteria-labels="]
    opts = []
    args = []

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], shortOptions, longOptions)
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

def parseViewOutput():
    log(2, "Parsing file " + DATADIR_REL + os.sep + MODULE_BASE + ".py")
    with open(DATADIR_REL + os.sep + MODULE_BASE + ".py", 'r') as pyFile:
        pyCode = pyFile.readline()
        try:
            viewData = ast.literal_eval(pyCode)
        except:
            log(0, "Error while trying to parse file " + DATADIR_REL + os.sep + MODULE_BASE + ".py")
        for criteria, details in viewData["view"][0]["data"]["aggregated-data"].items():
            for detail_name, detail_data in details.items():
                values = []
                categories = []
                log(2, criteria + "." + detail_name + ":")
                log(2, "\tMinimum: " + str(detail_data["min"]))
                log(2, "\tMaximum: " + str(detail_data["max"]))
                log(2, "\tTotal: " + str(detail_data["total"]))
                for bar in detail_data["distribution-bars"]:
                    values.append(bar["count"])
                    categories.append(bar["metric"])
                log(2, "values = " + str(values))
                log(2, "categories = " + str(categories))
                with open(DATADIR_REL + os.sep + MODULE_BASE + '.' + criteria + "." + detail_name + ".js", 'w') as criteriaJSfile:
                    criteriaJSfile.write(u"var values = " + str(values) + ";\n")
                    criteriaJSfile.write(u"var categories = " + str(categories) + ";\n")
                criteriaJSfile.close()
    pyFile.close()
                    

scanArguments()
if LOGLEVEL >= 2:
    dumpParameters()

LOGLEVEL = 2

parseViewOutput()