# makefile for generating metrix++ based html output.
# (c) 2020 Marc Stoerzel

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# settings to invoke metrix++; adapt path if necessary
PYTHON=/usr/bin/python
METRIXPP=/opt/metrixplusplus/metrix++.py
METRIXDB=metrixpp.db

ANALYSE=script/canalyse.py

CHARTMINJS=https://cdn.jsdelivr.net/npm/chart.js@2.9.3/dist/Chart.min.js

# path from where to start analysis of sourceceode
#SRCPATH=./example-code/insecure-coding-examples-master
#MODULE_BASE=exploit
SRCPATH=./../../../SW/Public
MODULE_BASE=30_Appl

# configure directories
REPORTDIR=./html
DATADIR=./data
STYLEDIR=./style
JSCRIPTDIR=./javascript
SCRIPTDIR=./script
INSTALLDIR=./highlight
HIGHLIGHT_CSS=styles/vs.css
DOCDIR=./doc

# configure diagram settings
# to add a new criteria: you add to CRITERIA_LIST the metrix++ argument AND create and add target to target 'criterias'
CRITERIA_LIST = std.code.complexity.cyclomatic std.code.lines.code std.code.filelines.comments
DIAGRAM_STYLE=diagram_style.js
# settigs for each diagram
CANVAS_WIDTH=600
CANVAS_HEIGHT=280

# calculate some directory paths for easier reference
SRCPATH_ESC= $(shell echo $(SRCPATH) | sed -e 's/\//\\\//g;s/\./\\./g')
REPORTDIR_ABS=$(abspath $(REPORTDIR))
DATADIR_ABS=$(abspath $(DATADIR))
DATADIR_REL = $(shell realpath --relative-to $(REPORTDIR_ABS) $(DATADIR_ABS))
STYLEDIR_ABS=$(abspath $(STYLEDIR))
STYLEDIR_REL = $(shell realpath --relative-to $(REPORTDIR_ABS) $(STYLEDIR_ABS))
JSCRIPTDIR_ABS=$(abspath $(JSCRIPTDIR))
JSCRIPTDIR_REL = $(shell realpath --relative-to $(REPORTDIR_ABS) $(JSCRIPTDIR_ABS))

# pre-calculate some HTML strings
criteria_nav := $(foreach criteria, $(CRITERIA_LIST), "<a target= 'criteria_frame' href='$(MODULE_BASE).$(criteria).html' onClick='switchCriteria(\"$(criteria)\")'>$(criteria)</a>")

.PHONY: all clean check directories criterias doc

all: check directories $(REPORTDIR)/index.html criterias

criterias: $(METRIXDB)
	echo Converting database into file $(DATADIR_REL)/$(MODULE_BASE).js
	$(PYTHON) $(METRIXPP) export --log-level=ERROR | tail --lines=+1 > $(DATADIR)/$(MODULE_BASE).csv
	$(PYTHON) $(ANALYSE) --srcpath=$(SRCPATH) --modulebase=$(MODULE_BASE) --datadir=$(DATADIR) --reportdir=$(REPORTDIR) --installdir=$(INSTALLDIR) --highlight-css=$(HIGHLIGHT_CSS) --styledir=$(STYLEDIR)
	echo Generating HTML files for $(CRITERIA_LIST)
	$(PYTHON) $(METRIXPP) view --log-level=ERROR --format=python > $(DATADIR)/$(MODULE_BASE).py
	$(PYTHON) $(SCRIPTDIR)/mpp-view2js.py --modulebase=$(MODULE_BASE) --datadir=$(DATADIR) --reportdir=$(REPORTDIR) --styledir=$(STYLEDIR) --diagram-width=$(CANVAS_WIDTH) --diagram-height=$(CANVAS_HEIGHT) $(DATADIR)/$(MODULE_BASE).py

$(METRIXDB):
	echo Generating data for $(CRITERIA_LIST)
	$(PYTHON) $(METRIXPP) collect --log-level=ERROR --db-file=$(METRIXDB) $(addprefix '--', $(CRITERIA_LIST)) -- $(SRCPATH)/$(MODULE_BASE)

$(REPORTDIR)/index.html: 
	echo Generating HTML header of $(REPORTDIR)/index.html 
	echo "<!DOCTYPE html>" > $(REPORTDIR)/index.html
	echo "  <html>\n	<head>\n	  <title>$(MODULE_BASE)</title>" >> $(REPORTDIR)/index.html
	echo "	  <script src=\"$(CHARTMINJS)\"></script>"  >> $(REPORTDIR)/index.html
	echo "	  <link rel='stylesheet' type='text/css' href='$(STYLEDIR_REL)/style.css'>" >> $(REPORTDIR)/index.html
	echo "	</head>\n  <body class='main'>" >> $(REPORTDIR)/index.html
	echo "	  <script src='$(STYLEDIR_REL)/$(DIAGRAM_STYLE)'></script>" >> $(REPORTDIR)/index.html
	echo "	  <script>" >> $(REPORTDIR)/index.html
	echo "      function switchCriteria(criteria) {" >> $(REPORTDIR)/index.html
	echo "		  clearFilelist_body(); createFilelist(DiagramStyles.get(criteria).index);" >> $(REPORTDIR)/index.html
	echo "		  populateFilelist_body(DiagramStyles.get(criteria).backgroundColor, DiagramStyles.get(criteria).criteriaLabel);" >> $(REPORTDIR)/index.html
	echo "    }</script>" >> $(REPORTDIR)/index.html

	echo "	  <navigation>" >> $(REPORTDIR)/index.html
	echo "	  <h1>$(MODULE_BASE)</h1>" >> $(REPORTDIR)/index.html
	echo "      <span id='nav_linklist'>" >> $(REPORTDIR)/index.html
	echo "      <b>Source Metrix Analyser</b> " >> $(REPORTDIR)/index.html
	echo        $(criteria_nav) >> $(REPORTDIR)/index.html
	echo "      powered by <a href='https://metrixplusplus.github.io/home.html'>Metrix++</a></span>" >> $(REPORTDIR)/index.html
	echo "    </navigation>"  >> $(REPORTDIR)/index.html
	echo "	  <iframe id='wrapper' height='100%' width='100%' src='$(REPORTDIR_ABS)/$(MODULE_BASE).std.code.complexity.cyclomatic.html' name='criteria_frame'></iframe>" >> $(REPORTDIR)/index.html
	echo "    <script src='$(DATADIR_REL)/$(MODULE_BASE).js'></script>" >> $(REPORTDIR)/index.html
	echo "    <script src='$(JSCRIPTDIR_REL)/filelist.js'></script>" >> $(REPORTDIR)/index.html
	echo "    <script>" >> $(REPORTDIR)/index.html
	echo "		document.addEventListener('DOMContentLoaded', function () {" >> $(REPORTDIR)/index.html
	echo "		    const values = Array.from(DiagramStyles.values());" >> $(REPORTDIR)/index.html
	echo "		    createFilelist(values[0].index);" >> $(REPORTDIR)/index.html
	echo "		    populateFilelist_body(values[0].backgroundColor, values[0].criteriaLabel);" >> $(REPORTDIR)/index.html
	echo "		    document.getElementById('sortAlphabetic').addEventListener('click', showAlphabetic);" >> $(REPORTDIR)/index.html
	echo "		    document.getElementById('sortNumeric').addEventListener('click', showNumeric);" >> $(REPORTDIR)/index.html
	echo "		});\n    </script>" >> $(REPORTDIR)/index.html

	echo "<span id='filelist_wrapper'>\n  <div id='filelist_header'>list of files <button type='button' id='sortAlphabetic'>sort by name &#x25BE;</button> <button type='button' id='sortNumeric'>sort by metric &#x25BE;</button></div>" >> $(REPORTDIR)/index.html
	echo "  <span id='filelist_body'></span>\n</span>" >> $(REPORTDIR)/index.html
	echo "  <iframe id='details_wrapper' height='100%' width='100%' src='details.html' name='details_frame'></iframe>" >> $(REPORTDIR)/index.html

	echo "	</body>\n</html>" >> $(REPORTDIR)/index.html

directories:
	$(info $(shell mkdir -p $(REPORTDIR) $(DATADIR)))

clean:
	$(info $(shell chmod -f 777 $(DATADIR)/*.*))				# workaround for https://www.virtualbox.org/ticket/16463
	rm -f $(DATADIR)/*.*
	$(info $(shell chmod -f 777 $(REPORTDIR)/*.html))				# workaround for https://www.virtualbox.org/ticket/16463
	rm -f $(REPORTDIR)/index.html
	$(foreach file, $(CRITERIA_LIST), rm -f $(REPORTDIR)/$(MODULE_BASE).$(file).html)
	rm -f $(METRIXDB)

check:
ifeq (,$(wildcard $(METRIXPP)))
    $(error Unable to execute $(PYTHON) $(METRIXPP) (metrixpp.py is not installed?))
endif

doc:
	cd $(DOCDIR); doxygen Doxyfile

