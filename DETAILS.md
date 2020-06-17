This file explains more on the implementation details of SourceMetrix.

# CONFIGURATION ITEMS

SourceMetrix is highly configurable. Its aim is to keep all configurations centralized in the central make file. Configuration data is then passed to the respective scripts by command line arguments.

The following list shows up all the configuration data and where they are used.

configuration item  | index.html | filelist.js | $CRITERIA.html | $CRITERIA.js | <sourcefiles>.html | CLI-option       
--------------------|:----------:|:-----------:|:--------------:|:------------:|:------------------:|------------------
module basename     | page title |             |                |              |                    | --modulebase     
source path         |            |             |                |              |           x        | --srcpath        
criteria list       | navigation |             |       x        |       x      |                    |                  
criteria-label      |            |      x      | filename       | filename     | info               | --criteria-labels
criteria-scope      |            |             |                |       x      |                    |     part of above 
background-color    |            |      x      |       x        |       x      |          x         |     part of above
border-color        |            |             |       x        |       x      |          x         |     part of above
combined-index      |            |      x      |                |              |                    |     part of above
digram-width        |            |             |       x        |              |                    |     part of above
digram-height       |            |             |       x        |              |                    |     part of above
report dir          |      x     |             |       x        |              |          x         | --reportdir
data dir            |            |      x      |       x        |              |                    | --datadir
style dir           |            |             |       x        |              |                    | --styledir
highlight dir       |            |             |       x        |              |                    | --installdir
highlight css       |            |             |       x        |              |                    | --highlight-css
jscript dir         |      x     |             |                |              |                    |
