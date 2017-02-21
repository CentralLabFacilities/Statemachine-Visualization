import xml.etree.ElementTree as ET
from graphviz import Digraph
import sys

# TODO's
## readGraph and build_mini_sg need to return a tuple of the graph and a list of tuples which contain edges and node from which these edges derive


# help text. if you change things here the amount of tabs may be in need of adjustments.
help_text= "\
Usage: sm-viz.py your-statemachine.scxml\n\
Possible switches:\n\t\
--h \t\t Displays this very(!) helpful text. \n\t\
--ex \t\t Exclude Substatemachines in the generated graph. Actually reduces them to single states. Use this to make your graph more readable. \n\t\
--reduce=n \t Exclude all Substatemachines below n levels. Use this to make your graph more readable without sacrificing inormation. \n\t\
--bw \t\t Will render the graph without colors (in black and white). \n\t\
--format=fmt \t Will render the graph in the specified format. Available formats are: png (default), pdf etc.\n\t\
--savegv \t Will save the generated GraphViz code. \n\t\
--gvname=name \t Will save the generated Graphviz code under the given name. Default name is the same as your input (but with extension .gv) Use with -savegv \n\t\
--rengine=ngin \t Will use the specified engine (ngin) to render the graph \n\t\
--nosubstates \t Similarly to ex and reduce this will suppress states in states. \
\n"

############################ variables ####################################

# Specifies the name of the input file.
input_name = ""

# Namespace of the statemachine. Needs to be 
ns = "{http://www.w3.org/2005/07/scxml}"


############################# switches ####################################

# Amount of recursive steps to which substate machines will be included.
subst_recs = float('inf')

# Controls whether to use auto colours or a black and white graph.
color = True

# Controls the format of the output.
fmt = "png"

# Controls if the generated GraphViz code is saved.
savegv = False

# Controls the filename of the saved GraphViz code.
gvname = ""

# Controls the engine used to render the graph.
rengine = ""

# Controls if states in states (aka mini-subgraphs) should be rendered in full.
minisg = True


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
		if tmp in graphviz.FORMATS:
			fmt = tmp
		else:
			print("Specified format not known! Will now exit.\n")
			exit()
	elif each.endswith(".xml"):
		input_name = each
	elif each == "--savegv":
		savegv = True
	elif each.startswith("--gvname="):
		gvname = each.split("=")[1]
	elif each.startswith("--rengine="):
		tmp = each.split("=")[1]	
		if tmp in graphviz.ENGINES:
			fmt = tmp
		else:
			print("Specified engine not known! Will now exit.\n")
			exit()
		rengine = each.split("=")[1]
	elif each == "--nosubstates":
		minisg = False
	else:
		print("Parameter \"" + each + "\" not recognized. Will now exit.\n")
		exit()

# Sanity checks
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

# Reads a graph from a specified filename. Returns the Digraph of this File.
# Optional parameters:
## level: for sub-statemachine purposes
## body: for the style of the body of this graph
## label: to label the graph
def readGraph(filename, level=0, body=[], label=""):
	# prepare return graph
	g = Digraph('g', engine=rengine)

	# prepare xml tree
	tree = ET.parse(filename)
	root = tree.getroot()
	initial_state = root_node.attrib['initial']
	send_events = []

	for child in root:
		if child.tag.endswith("state"):
			if "initial" in child.attrib:
				print("generate mini-subgraph")
			elif "src" in child.attrib:
				print("generate true subgraph")
			if "":
				pass
	if label:
		g.body.append('label = \"' + label + '\"')
	return g

# Builds a subgraph from a specified root node. Returns the Digraph of this rootnode.
# Potional parameters:
## label: for labeling the subgraph
def build_mini_sg(root, label=""):
	pass


# Determins the suitable body for the subgraph of a graph with a given body.
## Following order is in use:
### no body for the main graph
#### 
def detSubBody(body):
	pass

####################### start the graph generation ###########################

ns = root.tag[:-5] # get the namespace of this document 

DG = Digraph('G', engine=rengine)

exit()