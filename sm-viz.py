import xml.etree.ElementTree as ET
from graphviz import Digraph
import sys

# TODO's
## make render engine changable  


# help text. if you change things here the amount of tabs may be in need of adjustments.
help_text= "\
Usage: sm-viz.py your-statemachine.scxml\n\
Possible switches:\n\t\
--h \t\t displays this very(!) helpful text. \n\t\
--ex \t\t Exclude Substatemachines in the generated graph. Actually reduces them to single states. Use this to make your graph more readable. \n\t\
--reduce=n \t Exclude all Substatemachines below n levels. Use this to make your graph more readable without sacrificing inormation. \n\t\
--bw \t\t Will render the graph without colors (in black and white). \n\t\
--format=fmt \t Will render the graph in the specified format. Available formats are: png (default), pdf \n\t\
--savegv \t Will save the generated GraphViz code. \n\t\
--gvname=name \t Will save the generated Graphviz code under the given name. Default name is the same as your input (but with extension .gv) Use with -savegv\
\n"

############################ variables ####################################

# specifies the name of the input file
input_name = ""


############################# switches ####################################

# amount of recursive steps to which substate machines will be included
subst_recs = float('inf')

# controls whether to use auto colours or a black and white graph  
color = True

# controls the format of the output
fmt = "png"

# controls if the generated GraphViz code is saved
savegv = False

# controls the filename of the saved GraphViz code
gvname = ""


######################## start and flag stuff ##############################

if len(sys.argv) < 2:
	print(help_text)
	exit(0)

for each in sys.argv:
	if each == "-h" or each == "--h" or each == "--help" or each=="-help":
		print(help_text)
		exit(0)
	elif each == "--ex":
		excl_subst = True
		subst_recs = 0
	elif each.startswith("--reduce="):
		subst_recs = each.split("=")[1]
	elif each == "--bw":
		color = False
	elif each.startswith("--format="):
		tmp = each.split("=")[1]	
		if tmp == "png" or tmp == "pdf":
			fmt = tmp
		else:
			print("Specified format not known!\n")
			exit()
	elif each.endswith(".xml"):
		input_name = each
	elif each == "--savegv":
		savegv = True
	elif each.startswith("--gvname="):
		gvname = each.split("=")[1]

# sanity checks
if input_name == "":
	print("No input file specified! Will now exit.")
	exit()
if not gvname == "" and not savegv:
	print("gvname specified but not savegv! Will now exit.")
	exit()
else:
	gvname = input_name[:-4]

if not gvname.endswith(".gv"):
	gvname = gvname + ".gv"

############################### methods #####################################

# Reads a graph from a specified filename. Returns the Digraph of this File
# Optional parameters:
## level for sub-statemachine purposes
## body for the style of the body of this graph
def readGraph(filename, level=0, body=[]):
	#prepare return graph
	g = Digraph('g')
	#
	tree = ET.parse(filename)
	root = tree.getroot()
	initial_state = root_node.attrib['initial']
	send_events = []

	for child in root:
		if child.tag.endswith("state"):
			if "initial" in child.attrib:
				print("generate mini-subgraph")
	return g	

####################### start the graph generation ###########################

DG = Digraph('G')

exit()