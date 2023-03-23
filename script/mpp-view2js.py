#!/usr/bin/python

##
# @file mpp-view2js.py
# @copyright (c) 2020 Marc Stoerzel
# @brief Parses the 'view --format=python' output of metrix++ to generate HTML and Javascript.
#
# Generate HTML and Javascript files to display diagram of distribution for criterias.
##

import os
import io
import getopt
import sys
import ast

MODULE_BASE = "30_Appl"
REPORTDIR_REL = "./html"
DATADIR = "./data"
STYLEDIR = "./style"
IN_FILENAME = DATADIR + os.sep + MODULE_BASE + ".py"

CRITERIA_LABELS_SET = set(
    (
        "std.code.complexity.cyclomatic",
        "std.code.complexity.maxindent",
        "std.code.filelines.code",
        "std.code.filelines.preprocessor",
        "std.code.filelines.comments",
        "std.code.filelines.total",
        "std.code.length.total",
        "std.code.lines.code",
        "std.code.lines.preprocessor",
        "std.code.lines.comments",
        "std.code.lines.total",
        "std.code.longlines",
        "std.code.longlines.limit=120",
        "std.code.magic.numbers",
        "std.code.magic.numbers.simplier",
        "std.code.member.fields",
        "std.code.member.globals",
        "std.code.member.classes",
        "std.code.member.structs",
        "std.code.member.interfaces",
        "std.code.member.types",
        "std.code.member.methods",
        "std.code.member.namespaces",
        "std.code.maintindex.simple",
        "std.code.ratio.comments",
        "std.code.todo.comments",
        "std.code.todo.strings",
        "std.suppress",
        "std.general.procerrors",
        "std.general.size",
    )
)

CRITERIA_LABELS = {
    key: {
        "label": key,
        "background-color": "orange",
        "border-color": "red",
        "index": idx,
    }
    for idx, key in enumerate(CRITERIA_LABELS_SET)
}


# CRITERIA_LABELS = {
#     "std.code.complexity.cyclomatic": {
#         "label": "cyclomatic complexity",
#         "background-color": "orange",
#         "border-color": "red",
#         "index": 6,
#     },
#     "std.code.filelines.comments": {
#         "label": "lines of comment per file",
#         "background-color": "lightgreen",
#         "border-color": "green",
#         "index": 7,
#     },
#     "std.code.lines.code": {
#         "label": "lines of code per file",
#         "background-color": "lightblue",
#         "border-color": "blue",
#         "index": 8,
#     },
# }

_loglevels = {"error": -1, "silent": 0, "standard": 1, "verbose": 2}
LOGLEVEL = _loglevels["standard"]
GEN_DATAFILE_ONLY = False
CHARTMINJS = "https://cdn.jsdelivr.net/npm/chart.js@2.9.3/dist/Chart.min.js"
DIAG_WIDTH = 600
DIAG_HEIGHT = 280

##
# Print version information and exit
##
def printVersion():
    print("mpp-view2js.py 0.2 ")
    print("Copyright (c) 2020 Marc Stoerzel")


##
# Print info how to use from command line.
##
def printUsage():
    print("usage:", sys.argv[0], "[OPTION] [in-file]")
    print(
        "Parses the 'view --format=python' of metrix++ to generate Javascript datafiles."
    )
    print("Options and arguments:")
    print("  -h, --help                 print this help message and exit")
    print(
        "  --silent                   turn on silent mode: no output except in case of error"
    )
    print("  --verbose                  enable more elaborative output")
    print("  -v, --version              print version information and exit")
    print(
        "  --gen-datafile-only        generate only javascript data file (no HTML is generated)"
    )
    print("  -m, --modulebase=DIR       shall be name of the sourcecode's root folder")
    print("                                 defaults to:", MODULE_BASE)
    print(
        "  -r, --reportdir=DIR        the output directory of the generated html files"
    )
    print("                                 defaults to:", REPORTDIR_REL)
    print(
        "  -d, --datadir=DIR          directory to store converted Javascrip output to"
    )
    print("                                 defaults to:", DATADIR)
    print(
        "  -y, --styledir=DIR         directory containing the generic style.css file"
    )
    print("                                  defaults to:", STYLEDIR)
    print(
        "  in-file                    input file for conversion; shall be output of metrix++ view command"
    )
    print(
        "                                 defaults to:",
        DATADIR + os.sep + MODULE_BASE + ".py",
    )
    print("  -l, --criteria-labels=DICT dictionary, where ")
    print("                                 key = mnemnonic of the criteria and ")
    print("                                 value = dictionary with following items")
    print("                                     label = human readable label")
    print(
        "                                     background-color = background- or fill-color of the diagram bars"
    )
    print(
        "                                     border-color = border-color of the diagram bars"
    )
    print(
        "                                     index = index of column in the overall data file"
    )
    print("                                 defaults to:", CRITERIA_LABELS)
    print("  -c, --chart-js=URL         URL from where to include cahrt.min.js")
    print("                                 defaults to:", CHARTMINJS)
    print("  -w, --diagram-width=x      width of cahrt.js diagram canvas")
    print("                                 deafaults to: ", DIAG_WIDTH)
    print("  -t, --diagram-height=y      height of cahrt.js diagram canvas")
    print("                                 deafaults to: ", DIAG_HEIGHT)


##
# Print global paramter settings.
##
def dumpParameters():
    print("Parameters set as")
    print("  --modulebase      =", MODULE_BASE)
    print("  --datadir         =", DATADIR)
    print("  --reportdir       =", REPORTDIR_REL)
    print("  --styledir        =", STYLEDIR)
    print("  --criteria-labels =", CRITERIA_LABELS)
    print("  --gen-datafile-only =", GEN_DATAFILE_ONLY)
    print("  --chart-js =", CHARTMINJS)
    print("  --diagram-width =", DIAG_WIDTH)
    print("  --diagram-height =", DIAG_HEIGHT)


##
# Print a log message to stdout if loglevel is set appropriate.
#
# @param level      verbosity level of this message. If level < LOG_LEVEL the message will be printed to stdout.
# @param message    string to be printed
##
def log(level, message):
    if LOGLEVEL >= level:
        print(message)
    if level < 0:
        sys.exit(-level)


##
# Scan commandline arguments.
#
# Scan command line arguments and set global parameters accordingly (use '--help' on commandline to get list of
# supported command line arguments).
##
def scanArguments():
    global REPORTDIR_REL, STYLEDIR, LOGLEVEL, MODULE_BASE, REPORTDIR_REL, DATADIR, IN_FILENAME, CRITERIA_LABELS, GEN_DATAFILE_ONLY, DIAG_WIDTH, DIAG_HEIGHT, CHARTMINJS
    shortOptions = "hvs:r:m:d:y:l:c:w:t:"
    longOptions = [
        "help",
        "version",
        "verbose",
        "silent",
        "srcpath=",
        "reportdir=",
        "modulebase=",
        "datadir=",
        "styledir=",
        "criteria-labels=",
        "gen-datafile-only",
        "chart-js=",
        "diagram-width=",
        "diagram-height=",
    ]
    opts = []
    args = []

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], shortOptions, longOptions)
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))
        printUsage()
        sys.exit()

    for (
        o,
        a,
    ) in opts:
        if o in ("--help", "-h"):
            printUsage()
            sys.exit()
        elif o in ("--version", "-v"):
            printVersion()
            sys.exit()
        elif o == "--verbose":
            LOGLEVEL = _loglevels["verbose"]
            if not a == "":
                LOGLEVEL = int(a)
        elif o == "--silent":
            LOGLEVEL = _loglevels["silent"]
        elif o == "-m" or o == "--modulebase":
            MODULE_BASE = a
        elif o == "-d" or o == "--datadir":
            DATADIR = a
        elif o == "-r" or o == "--reportdir":
            REPORTDIR_REL = a
        elif o == "-y" or o == "--styledir":
            STYLEDIR = a
        elif o == "-l" or o == "--criteria-labels":
            try:
                CRITERIA_LABELS = ast.literal_eval(a)
            except:
                log(
                    -1,
                    "error while trying to parse following argument for 'criteria-labels':"
                    + str(a),
                )
        elif o == "--gen-datafile-only":
            GEN_DATAFILE_ONLY = True
        elif o in ("chart-js", "c"):
            CHARTMINJS = str(a)
        elif o in ("diagram-width", "w"):
            try:
                DIAG_WIDTH = int(a)
            except:
                log(-1, "Error parsing argument for --diagram-width=" + str(a))
        elif o in ("diagram-height", "t"):
            try:
                DIAG_HEIGHT = int(a)
            except:
                log(-1, "Error parsing argument for --diagram-height=" + str(a))

    if len(args) == 1:
        IN_FILENAME = args[0]
    if not os.path.isfile(IN_FILENAME):
        log(-1, "Can't read input file: " + IN_FILENAME)


##
# Parse the output of 'metrix++ view format=Python' for data of \c criteria.
#
# Open in_file and parse it as Python code as generated by an invocation of 'metrix++ view format=Python'.
# Iterate over the parsed data structure and extract the information for \c criteria: minimum, maximum,
# average and total values and data on the diagram bars. Data on diagram bars will be converted to Javascript
# code.
# @param [in]   in_filename     filename pointing to the python file to be parsed
# @param [in]   criteria        identifier of a criteria to aprse for, e.g. std.code.complexity.cyclomatic
# @param [out]  dictionary with members "min", "max", "avg", "tot" holding the respective values and "code"
#               representing the data of the distribution bars converted to Javascript code
##
def parseViewOutput(in_filename, criteria):
    ret = {"avg": 0.0, "min": 0, "max": 0, "tot": 0, "code": ""}
    log(2, "Parsing file " + in_filename + " for criteria " + criteria)
    with open(in_filename, "r") as pyFile:
        pyCode = pyFile.readline()
        try:
            viewData = ast.literal_eval(pyCode)
        except:
            log(0, "Error while trying to parse file " + in_filename)
        for criteria_name, details in viewData["view"][0]["data"][
            "aggregated-data"
        ].items():
            for detail_name, detail_data in details.items():
                values = []
                categories = []
                if criteria == criteria_name + "." + detail_name:
                    log(
                        3,
                        "Found data for : "
                        + criteria
                        + " = '"
                        + CRITERIA_LABELS[criteria]["label"]
                        + "'",
                    )
                    ret["avg"] = float(detail_data["avg"]) if detail_data["avg"] else 0
                    log(3, "\tAverage: " + str(ret["avg"]))
                    ret["min"] = int(detail_data["min"]) if detail_data["min"] else 0
                    log(3, "\tMinimum: " + str(ret["min"]))
                    ret["min"] = int(detail_data["max"]) if detail_data["max"] else 0
                    log(3, "\tMaximum: " + str(ret["max"]))
                    ret["tot"] = (
                        int(detail_data["total"]) if detail_data["total"] else 0
                    )
                    log(3, "\tTotal: " + str(ret["tot"]))
                    for bar in detail_data["distribution-bars"]:
                        values.append(bar["count"])
                        categories.append(bar["metric"])
                    log(3, "values = " + str(values))
                    log(3, "categories = " + str(categories))
                    ret["code"] += "var values = " + str(values) + ";\n"
                    ret["code"] += "var categories = " + str(categories) + ";\n"
    return ret


##
# Generate an HTML file to display diagram of distribution for a criteria.
#
# Write to a file (existing file will be overwritten) REPORTDIR/MODULE_BASE.<criteria>.html the HTML and Javascript code
# to display a bar diagram showing the distribution, min, max, average and total values.
##
def writeHTMLfile(criteria, min, max, avg, tot):
    global REPORTDIR_REL, STYLEDIR, LOGLEVEL, MODULE_BASE, REPORTDIR_REL, DATADIR, IN_FILENAME, CRITERIA_LABELS, GEN_DATAFILE_ONLY, DIAG_WIDTH, DIAG_HEIGHT, CHARTMINJS

    styledir_rel = os.path.relpath(STYLEDIR, REPORTDIR_REL)
    datadir_rel = os.path.relpath(DATADIR, REPORTDIR_REL)
    # TODO file open access might fail
    with io.open(
        REPORTDIR_REL + os.sep + MODULE_BASE + "." + criteria + ".html", "w"
    ) as htmlFile:
        htmlFile.write("<!DOCTYPE html>\n  <html>\n	<head>\n")
        htmlFile.write("	  <script src='" + CHARTMINJS + "'></script>\n")
        htmlFile.write(
            "	  <link rel='stylesheet' type='text/css' href='"
            + styledir_rel
            + "/style.css'>\n"
        )
        htmlFile.write("	</head>\n  <body>\n")
        htmlFile.write(
            "		<h2 id='"
            + str(CRITERIA_LABELS[criteria]["label"]).replace(" ", "_")
            + "'>Distribution of "
            + CRITERIA_LABELS[criteria]["label"]
            + "</h2>\n"
        )
        htmlFile.write("      <p>Average : " + str(avg) + "<br>\n")
        htmlFile.write("         Minimum : " + str(min) + "<br>\n")
        htmlFile.write("         Maximum : " + str(max) + "<br>\n")
        htmlFile.write("         Total : " + str(tot) + "</p>\n")
        htmlFile.write(
            "		<canvas id='"
            + criteria
            + "' width='"
            + str(DIAG_WIDTH)
            + "' height='"
            + str(DIAG_HEIGHT)
            + "'></canvas>\n"
        )
        htmlFile.write(
            "	  <script src='"
            + datadir_rel
            + os.sep
            + MODULE_BASE
            + "."
            + criteria
            + ".js'></script>\n"
        )
        htmlFile.write("	  <script>\n")
        htmlFile.write("	  	var ctx = document.getElementById('" + criteria + "');\n")
        htmlFile.write("	  	var myChart = new Chart(ctx, {\n")
        htmlFile.write("	  	  type: 'bar',\n")
        htmlFile.write("	  	  data: {\n")
        htmlFile.write("	  	    labels: categories,\n")
        htmlFile.write("	  	    datasets: [{ \n")
        htmlFile.write(
            "	  	        label: '" + CRITERIA_LABELS[criteria]["label"] + "',\n"
        )
        htmlFile.write(
            "	  	        backgroundColor: '"
            + CRITERIA_LABELS[criteria]["background-color"]
            + "',\n"
        )
        htmlFile.write(
            "	  	        borderColor: '"
            + CRITERIA_LABELS[criteria]["border-color"]
            + "',\n"
        )
        htmlFile.write("	  	        borderWidth: 1,\n")
        htmlFile.write("	  	        data: values\n")
        htmlFile.write("	  	      }]\n}\n	  	});\n")
        htmlFile.write(
            "		document.addEventListener('DOMContentLoaded', function () {\n"
        )
        htmlFile.write(
            "		    document.getElementById('"
            + str(CRITERIA_LABELS[criteria]["label"]).replace(" ", "_")
            + "').innerText = \n"
        )
        htmlFile.write(
            "               'Distribution of "
            + CRITERIA_LABELS[criteria]["label"]
            + "';\n"
        )
        htmlFile.write("		});\n")
        htmlFile.write("	  </script>\n</bod></html>")
    htmlFile.close()


scanArguments()
if LOGLEVEL >= 2:
    dumpParameters()

for criteria in CRITERIA_LABELS.keys():
    data_code = parseViewOutput(IN_FILENAME, criteria)
    if data_code["code"] == "":
        log(0, "No data found for criteria '" + criteria + "'")
    else:
        try:
            with open(
                DATADIR + os.sep + MODULE_BASE + "." + criteria + ".js", "w"
            ) as criteriaJSfile:
                criteriaJSfile.write(data_code["code"])
            criteriaJSfile.close()
        except:
            log(
                -1,
                "Can't write data file "
                + DATADIR
                + os.sep
                + MODULE_BASE
                + "."
                + criteria
                + ".js",
            )
        if not GEN_DATAFILE_ONLY:
            writeHTMLfile(
                criteria,
                data_code["min"],
                data_code["max"],
                data_code["avg"],
                data_code["tot"],
            )
