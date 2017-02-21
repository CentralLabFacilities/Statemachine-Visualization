import xml.etree.ElementTree as ET
from graphviz import Digraph
import sys
import os.path

# TODO's
## readGraph and build_mini_sg need to return a tuple of the graph and a list of tuples which contain edges and node from which these edges derive

"""This is a little program written to visualize statemachines in scxml with the help of GraphViz. 

Most if not all of the functions and variables should be documented according to the Google Python Style Guide.

Written by Slothologist.
"""

############################ variables ####################################

help_text= "\
Usage: sm-viz.py your-statemachine.xml\n\
Possible switches:\n\t\
--h \t\t Displays this very helpful text. \n\t\
--ex \t\t Exclude Substatemachines in the generated graph. Actually reduces them to single states. Use this to make your graph more readable. \n\t\
--reduce=n \t Exclude all Substatemachines below n levels. Use this to make your graph more readable without sacrificing inormation. WIP \n\t\
--bw \t\t Will render the graph without colors (aka in black and white). \n\t\
--eventclr=event:color \t Will use the specified color for the event. Uses a contains internally. Multiple values possible, eg: --eventclr=success:green,error:red \n\t\
--format=fmt \t Will render the graph in the specified format. Available formats are: png (default), pdf etc. WIP\n\t\
--savegv \t Will save the generated GraphViz code. WIP \n\t\
--gvname=name \t Will save the generated Graphviz code under the given name. Default name is the same as your input (but with extension .gv) Use with -savegv WIP \n\t\
--rengine=ngin \t Will use the specified engine (ngin) to render the graph \n\t\
--nocmpstates \t Similarly to ex and reduce this will suppress compound states (states in states). WIP \
\n"
"""str: Helping text. If you change things here the amount of tabs (after the flags) may be in need of adjustments.
"""

inputName = ""
"""str: Specifies the name of the input file.
"""

ns = "{http://www.w3.org/2005/07/scxml}"
"""str: Namespace of the statemachine. Will be calculated again when reading the first xml file.
"""

colordict = {"Timeout": "blue", "success": "green", "fatal": "red", "error": "red"}
"""dict(str->str): Dictionary that contains the events
"""

############################# switches ####################################

subst_recs = float('inf')
"""float: Amount of recursive steps to which substate machines will be included. Usage as int, but only float supports infty.
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

rengine = "dot"
"""str: Controls the engine used to render the graph.
"""

minisg = True
"""bool: Controls if states in states (aka mini-subgraphs) should be rendered in full.
"""

############################### methods #####################################

def handleArguments(args):
	"""Will initialize the variables and switches necessary to use all other funtions.

		Args:
			args (list[str]): The switches with which the generator shall be initialized.
	"""
	if len(args) < 2:
		print(help_text)
		exit(0)

	# global variables (basically all switches)
	global excl_subst
	global subst_recs
	global colordict
	global fmt
	global inputName
	global savegv
	global gvname
	global rengine
	global minisg

	for each in args:
		if each == "-h" or each == "--h" or each == "--help" or each=="-help":
			print(help_text)
			exit(0)
		elif each == "--ex":
			excl_subst = True
			subst_recs = 0
		elif each.startswith("--reduce="):
			subst_recs = each.split("=")[1]
		elif each == "--bw":
			for each in colordict:
				colordict[each] = "black"
		elif each.startswith("--eventclr="):
			tmp = each.split("=")[1]
			clrs = tmp.split(",")
			for each in clrs:
				tup = clrs.split(":")
				colordict[tup[0]] = tup[1]
		elif each.startswith("--format="):
			tmp = each.split("=")[1]	
			if tmp in graphviz.FORMATS:
				fmt = tmp
			else:
				print("Specified format not known! Will now exit.\n")
				exit()
		elif each.endswith(".xml"):
			inputName = each
		elif each == "--savegv":
			savegv = True
		elif each.startswith("--gvname="):
			gvname = each.split("=")[1]
		elif each.startswith("--rengine="):
			tmp = each.split("=")[1]	
			if tmp in graphviz.ENGINES:
				rengine = tmp
			else:
				print("Specified engine not known! Will now exit.\n")
				exit()
			rengine = each.split("=")[1]
		elif each == "--nocmpstates":
			minisg = False
		elif each == __file__:
			pass
		else:
			print("Parameter \"" + each + "\" not recognized. Will now exit.\n")
			exit()

def sanityChecks():
	"""Will check the given parameters for their sanity. Will print an errormessage and exit on broken sanity.
	"""

	# global variables (basically switches)
	global inputName
	global gvname
	global savegv

	# no input file
	if inputName == "":
		print("Input file is not an .xml or not specified! Will now exit.\n")
		exit()

	# gvname specified but not savegv
	if not gvname == "" and not savegv:
		print("gvname specified but not savegv! Will now exit.\n")
		exit()
	elif not gvname:
		gvname = inputName[:-4]

	# gvname does not end with ".gv"
	if not gvname.endswith(".gv"):
		gvname = gvname + ".gv"

	# input file does not exist
	if not os.path.isfile(inputName):
		print("The file \"" + inputName + "\" does not exist. Will now exit.\n")
		exit()

def readGraph(filename, level=0, body=[], label=""):
	"""Reads a graph from a specified filename.

		Args:
			filename (str): The name of the file in which the graph 
			level (int, optional): Used for sub-statemachine purposes, this corresponds to the level in which the graph lies. If greater
				than subst_recs given at the start of the programm, this graph will be reduced to just one state (but will still have all edges).
			body (list[str], optional): Used to set the style of the body of this graph. Contains of a list of str.
			label (str, optional): Used to set the label of the graph.

		Returns:
			tuple(Digraph, list[edge]): A tuple containing:
				1. The Digraph of the specified rootnode.
				2. A list of edges. The edges themself are tuples containing two str: The first beeing the start-node, the second beeing 
				a special string containing the event this state sends. These 'special' edges need to be accounted for.
	"""
	# prepare return graph
	g = Digraph(filename, engine=rengine, format=fmt)

	# prepare xml tree
	tree = ET.parse(filename)
	root = tree.getroot()
	initial_state = root.attrib['initial']
	send_events = []
	edges = []

	for child in root:
		if child.tag.endswith("state"):
			# case: compound state
			if "initial" in child.attrib:
				print("generate mini-subgraph")
			# case: substatemachine in seperate .xml
			elif "src" in child.attrib:
				print("generate true subgraph")
			# case: parallel states
			elif "parallel" in child.attrib:
				print("draw parallel subgraph")
			# case: regular state
			else:
				for each in child:
					if each.tag[len(ns):] == "transition":
						# case: regular state transition
						if "target" in each.attrib:
							g.edge(child.attrib['id'], each.attrib['target'], label=each.attrib['event'], color=detEdgeColor(each.attrib['event']))
						# case: send event transition TODO: ugly
						else:
							for every in each:
								if every.tag[len(ns):] == "send":
									edges.append((child.attrib['id'], every.attrib['event']))
					elif each.tag[len(ns):] == "send":
						edges.append((child.attrib['id'], each.attrib['event']))
	if label:
		g.body.append('label = \"' + label + '\"')
	if level == 0:
		g.body.append("label=\"\nSM for " + filename + "\"")
		g.body.append('fontsize=20')
		g.node('Start', shape='Mdiamond')
		g.edge('Start', initial_state)
		g.node('End', shape='Msquare')
		for each in edges:
			g.edge(each[0], 'End', label=each[1], color=detEdgeColor(each[1]))
	return (g, edges)

def build_mini_sg(root, label=""):
	"""Builds a subgraph from a specified root node.

		Args:
			root (Digraph.node): The root node from which this subgraph extends.
			label (str): Used to label the subgraph.

		Returns:
			tuple(Digraph, list[edge]): A tuple containing:
				1. The Digraph of the specified rootnode.
				2. A list of edges. The edges themself are tuples containing two str: The first beeing the start-node, the second beeing 
					a special string containing the event this state sends. These 'special' edges need to be accounted for.
	"""
	pass

def detEdgeColor(event):
	"""Determins the color of a edge, given a specific event.

		Args:
			event (str): The event which will determine the color of the edge.

		Returns:
			str: A string stating the color of the edge. EG: red, blue, green etc

	"""
	edgecolor = "black"
	for each in colordict:
		if event.__contains__(each):
			edgecolor = colordict[each]
			break
	return edgecolor

def detSubBody(body):
	"""Determins the suitable body for the subgraph of a graph with a given body.

	Following order is in use: No body for the main graph.

		Args:
			body (list[str]): The body of the graph you want to determine the body of the subgraphs of. Contains of a list of str.

		Returns:
			list[str]: The body of the subgraphs of the graph with the passed body.
	"""
	return body

def draw(graph):
	"""Draws a given graph into according to the given configuration.

		Args:
			graph (Digraph): The graph that shall be rendered.
	"""
	graph.render(filename=gvname, cleanup=not savegv)
	pass

def main():
	"""Main function of this programm. Will generate a graph based on the given arguments.
	"""

	# initialize the switches and stuff
	handleArguments(sys.argv)

	# check the sanity of the given arguments
	sanityChecks()

	# generate the main graph
	(DG, edges) = readGraph(inputName)

	draw(DG)

	exit()

#  If this script is executed in itself, run the main method (aka generate the graph).
if __name__ == '__main__':
	main()