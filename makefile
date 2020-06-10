# makefile for generating metrix++ based html output.
# (c) 2020 Marc Stoerzel

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# settings to invoke metrix++; adapt path if necessary
METRIXPP=/opt/metrixplusplus/metrix++.py
PYTHON=/usr/bin/python
ANALYSE=script/canalyse.py

CHARTMINJS=https://cdn.jsdelivr.net/npm/chart.js@2.9.3/dist/Chart.min.js

# path from where to start analysis of sourceceode
#SRCPATH=./example-code/insecure-coding-examples-master
#MODULE_BASE=exploit
SRCPATH=./../../../SW/Public
MODULE_BASE=30_Appl

# configure directories
REPORTDIR=html
DATADIR=data
STYLEDIR=style
JSCRIPTDIR=javascript
INSTALLDIR=highlight
HIGHLIGHT_CSS=styles/vs.css
DOCDIR=doc

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

.PHONY: all clean check directories criterias indexfile indexfile_end indexfile_start doc

all: check directories indexfile

criterias: cyclomatic code_loc comments
	$(call generate_detailedDatafile)
	$(PYTHON) $(ANALYSE) --srcpath=$(SRCPATH) --modulebase=$(MODULE_BASE) --datadir=$(DATADIR) --reportdir=$(REPORTDIR) --installdir=$(INSTALLDIR) --highlight-css=$(HIGHLIGHT_CSS) --styledir=$(STYLEDIR)

indexfile: indexfile_start criterias indexfile_end

directories:
	$(info $(shell mkdir -p $(REPORTDIR) $(DATADIR)))

clean:
	$(info $(shell chmod -f 777 $(DATADIR)/*.*))				# workaround for https://www.virtualbox.org/ticket/16463
	rm -f $(DATADIR)/*.*
	$(info $(shell chmod -f 777 $(REPORTDIR)/*.html))				# workaround for https://www.virtualbox.org/ticket/16463
	rm -f $(REPORTDIR)/index.html
	$(foreach file, $(CRITERIA_LIST), rm -f $(REPORTDIR)/$(MODULE_BASE).$(file).html)
	#todo remove metrixpp.db

check:
ifeq (,$(wildcard $(METRIXPP)))
    $(error Unable to execute $(PYTHON) $(METRIXPP) (metrixpp.py is not installed?))
endif

doc:
	cd $(DOCDIR); doxygen Doxyfile

indexfile_start:
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

cyclomatic:	CRITERIA=std.code.complexity.cyclomatic
cyclomatic: CRITERIA_LABEL="cyclomatic complexity"
cyclomatic:
	$(call generate_criteriaHTML)

code_loc: CRITERIA=std.code.lines.code
code_loc: CRITERIA_LABEL="lines of code"
code_loc:
	$(call generate_criteriaHTML)

comments: CRITERIA = std.code.filelines.comments
comments: CRITERIA_LABEL = lines as comment
comments:
	$(call generate_criteriaHTML)

indexfile_end:
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

define generate_criteriaHTML
	echo Generating HTML header of $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html 
	echo "<!DOCTYPE html>" > $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "  <html>\n	<head>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  <script src=\"$(CHARTMINJS)\"></script>"  >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  <link rel='stylesheet' type='text/css' href='$(STYLEDIR_REL)/style.css'>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	</head>\n  <body>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	# not passed as argument, because argument substitution inser a blank
	$(call generate_rawfile)
	$(call generate_datafile)
	echo "		<h2 id='$(CRITERIA_LABEL)'>Distribution of $(CRITERIA_LABEL) per region</h2>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "      <p>"  >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	$(PYTHON) $(METRIXPP) view --log-level=ERROR | grep 'Average' >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html; echo "<br>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	$(PYTHON) $(METRIXPP) view --log-level=ERROR | grep 'Minimum' >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html; echo "<br>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	$(PYTHON) $(METRIXPP) view --log-level=ERROR | grep 'Maximum' >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html; echo "<br>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	$(PYTHON) $(METRIXPP) view --log-level=ERROR | grep 'Total' >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html; echo "<br>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "      </p>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "		<canvas id=\"$(CRITERIA)\" width=\"$(CANVAS_WIDTH)\" height=\"$(CANVAS_HEIGHT)\"></canvas>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  <script src=\"$(DATADIR_REL)/$(MODULE_BASE).$(CRITERIA).js\"></script>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  <script src='$(STYLEDIR_REL)/$(DIAGRAM_STYLE)'></script>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  <script>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html

	echo "	  	var ctx = document.getElementById(\"$(CRITERIA)\");" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	var myChart = new Chart(ctx, {" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	  type: 'bar'," >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	  data: {" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	    labels: categories," >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	    datasets: [\n	  	      { " >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	        label: '$(CRITERIA_LABEL)'," >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	        backgroundColor: DiagramStyles.get('$(CRITERIA)').backgroundColor," >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	        borderColor: DiagramStyles.get('$(CRITERIA)').borderColor," >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	        borderWidth: 1," >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	        data: values" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  	      }\n	  	    ]\n}\n	  	});" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "		document.addEventListener('DOMContentLoaded', function () {" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "		    document.getElementById('$(CRITERIA_LABEL)').innerText = 'Distribution of ' + DiagramStyles.get('$(CRITERIA)').criteriaLabel;" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "		});" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
	echo "	  </script>\n</bod></html>" >> $(REPORTDIR)/$(MODULE_BASE).$(CRITERIA).html
endef

define generate_rawfile 
	echo Generating data file for $(CRITERIA)
	$(PYTHON) $(METRIXPP) collect --log-level=ERROR --$(CRITERIA) -- $(SRCPATH)/$(MODULE_BASE)
	$(PYTHON) $(METRIXPP) view --log-level=ERROR | tail -n+8 | head --lines=-5 > $(DATADIR)/$(MODULE_BASE).$(CRITERIA)
endef

define generate_datafile
	echo Converting $(DATADIR)/$(MODULE_BASE).$(CRITERIA) into $(MODULE_BASE).$(DATADIR)/$(CRITERIA).js
	echo "// Our labels along the x-axis" > $(DATADIR)/$(MODULE_BASE).$(CRITERIA).js
	echo "var categories = [" >> $(DATADIR)/$(MODULE_BASE).$(CRITERIA).js
	# cut by ':', cut first column, remove trailing whitespace, add a ',' after cut out
	cut --delimiter=: --fields=1 $(DATADIR)/$(MODULE_BASE).$(CRITERIA) | sed 's/[[:blank:]]*\(.*\)/"\1",/' | head --bytes=-2 >> $(DATADIR)/$(MODULE_BASE).$(CRITERIA).js
	echo "];"  >> $(DATADIR)/$(MODULE_BASE).$(CRITERIA).js
	echo "var values = [" >> $(DATADIR)/$(MODULE_BASE).$(CRITERIA).js
	# cut by ':', cut 4th column, trim to 5 cahracters, add a ',' at end of line and remove last 3 chars (surplus line brake) 
	cut --delimiter=: --fields=4 $(DATADIR)/$(MODULE_BASE).$(CRITERIA) | cut -b 1-5 | sed 'a, ' | head --bytes=-3 >> $(DATADIR)/$(MODULE_BASE).$(CRITERIA).js
	echo "];"  >> $(DATADIR)/$(MODULE_BASE).$(CRITERIA).js
endef

define generate_detailedDatafile
	echo Generating data for $(CRITERIA_LIST)
	$(PYTHON) $(METRIXPP) collect --log-level=ERROR $(addprefix '--', $(CRITERIA_LIST)) -- $(SRCPATH)/$(MODULE_BASE)
	$(PYTHON) $(METRIXPP) export --log-level=ERROR | tail --lines=+1 > $(DATADIR)/$(MODULE_BASE).csv
endef