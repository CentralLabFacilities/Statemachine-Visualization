import xml.etree.ElementTree as ET
from graphviz import Digraph
import sys

# TODO's
## readGraph and build_mini_sg need to return a tuple of the graph and a list of tuples which contain edges and node from which these edges derive

"""This is a little program written to visualize statemachines in scxml with the help of GraphViz. 

Most if not all of the functions and variables should be documented according to the Google Python Style Guide.

Written by Slothologist.
"""

############################ variables ####################################

help_text= "\
Usage: sm-viz.py your-statemachine.scxml\n\
Possible switches:\n\t\
--h \t\t Displays this very helpful text. \n\t\
--ex \t\t Exclude Substatemachines in the generated graph. Actually reduces them to single states. Use this to make your graph more readable. \n\t\
--reduce=n \t Exclude all Substatemachines below n levels. Use this to make your graph more readable without sacrificing inormation. \n\t\
--bw \t\t Will render the graph without colors (aka in black and white). \n\t\
--format=fmt \t Will render the graph in the specified format. Available formats are: png (default), pdf etc.\n\t\
--savegv \t Will save the generated GraphViz code. \n\t\
--gvname=name \t Will save the generated Graphviz code under the given name. Default name is the same as your input (but with extension .gv) Use with -savegv \n\t\
--rengine=ngin \t Will use the specified engine (ngin) to render the graph \n\t\
--nocmpstates \t Similarly to ex and reduce this will suppress compound states (states in states). \
\n"
"""str: Helping text. If you change things here the amount of tabs (after the flags) may be in need of adjustments.
"""

input_name = ""
"""str: Specifies the name of the input file.
"""

ns = "{http://www.w3.org/2005/07/scxml}"
"""str: Namespace of the statemachine. Will be calculated again when reading the first xml file.
"""


############################# switches ####################################

subst_recs = float('inf')
"""float: Amount of recursive steps to which substate machines will be included. Usage as int, but only float supports infty.
"""

color = True
"""bool: Controls whether to use auto colours or a black and white graph.
"""

fmt = "png"
"""str: Controls the format of the output.
"""

savegv = False
"""bool: Controls if the generated GraphViz code is saved.
"""

gvname = ""
"""str: Controls the filename of the saved GraphViz code.
"""

rengine = ""
"""str: Controls the engine used to render the graph.
"""

minisg = True
"""bool: Controls if states in states (aka mini-subgraphs) should be rendered in full.
"""

############################### methods #####################################

def readGraph(filename, level=0, body=[], label=""):
"""Reads a graph from a specified filename.

	Args:
		filename (str): The name of the file in which the graph 
		level (int, optional): Used for sub-statemachine purposes, this corresponds to the level in which the graph lies. If greater than subst_recs given at the start of the programm, this graph will be reduced to just one state (but will still have all edges).
		body (list[str], optional): Used to set the style of the body of this graph. Contains of a list of str.
		label (str, optional): Used to set the label of the graph.
	Returns:
		Digraph: The Digraph of the specified file.
"""
	# prepare return graph
	g = Digraph('g', engine=rengine)

	# prepare xml tree
	tree = ET.parse(filename)
	root = tree.getroot()
	initial_state = root_node.attrib['initial']
	send_events = []
	edges = []

	for child in root:
		if child.tag.endswith("state"):
			if "initial" in child.attrib:
				print("generate mini-subgraph")
			elif "src" in child.attrib:
				print("generate true subgraph")
			elif "parallel" in child.attrib:
				print("draw parallel subgraph")
			if "":
				pass
	if label:
		g.body.append('label = \"' + label + '\"')
	return g

def build_mini_sg(root, label=""):
"""Builds a subgraph from a specified root node.

	Args:
		root (Digraph.node): The root node from which this subgraph extends.
		label (str): Used to label the subgraph.

	Returns:
		Digraph: The Digraph of the specified rootnode.
"""
	pass

def detSubBody(body):
"""Determins the suitable body for the subgraph of a graph with a given body.

Following order is in use: No body for the main graph.

	Args:
		body (list[str]): The body of the graph you want to determine the body of the subgraphs of. Contains of a list of str.

	Returns:
		list[str]: The body of the subgraphs of the graph with the passed body.
"""
	pass


######################## startup and flag stuff ##############################

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
	elif each == "--nocmpstates":
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

####################### start the graph generation ###########################

ns = root.tag[:-5] # get the namespace of this document 

DG = Digraph('G', engine=rengine)

exit()