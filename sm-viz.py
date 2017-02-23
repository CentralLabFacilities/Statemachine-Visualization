import xml.etree.ElementTree as ET
from graphviz import Digraph
import sys
import os.path
import os

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
--ex \t\t Exclude Substatemachines in the generated graph. Actually reduces them to single states. Use this to \
make your graph more readable. WIP \n\t\
--reduce=n \t Exclude all Substatemachines below n levels. Use this to make your graph more readable without \
sacrificing inormation. WIP \n\t\
--nocmpstates \t Similarly to ex and reduce this will suppress compound states (states in states). \n\t\
--cmpstateclr=clr \t Will set the color of the border in which compound states reside. \n\t\
--bw \t\t Will render the graph without colors (aka in black and white). \n\t\
--eventclr=event:color \t Will use the specified color for the event. Uses a contains internally. Multiple values \
possible, eg: --eventclr=success:green,error:red \n\t\
--format=fmt \t Will render the graph in the specified format. Available formats are: png (default), pdf etc. \n\t\
--savegv \t Will save the generated GraphViz code. \n\t\
--gvname=name \t Will save the generated Graphviz code under the given name. Default name is the same as your input\
 (but with extension .gv) Use with -savegv \n\t\
--rengine=ngin \t Will use the specified engine (ngin) to render the graph \n\
\n\
Will render a given statemachine into a .png file (unless otherwise specified) using GraphViz. \n\
Will defautly color regular edges. Edges containing the words \"fatal\" or \"error\" will be rendered red, \
\"success\" green and \"Timeout\" blue. Furthermore, edges representing \'send events\' will have their label \
rendered blue.\n\
Compound states will either be rendered surrounded by a black border or into a single, gray state, depending on the \
\'nocmpstates\' flag. \n\
Substatemachines will be coloured differently depending on the level or be reduced into a single, double bordered state.\n\
"
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

cmp_color = "black"
"""str: Color of the border in which surrounds compound states.
"""

sendevntcolor = "blue"
"""str: Determins the color of the labels of send-event edges.
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
	global cmp_color

	for each in args:
		if each == "-h" or each == "--h" or each == "--help" or each=="-help":
			print(help_text)
			exit(0)
		elif each == "--ex":
			excl_subst = True
			subst_recs = 0
		elif each.startswith("--reduce="):
			subst_recs = int(each.split("=")[1])
		elif each.startswith("--cmpstateclr="):
			cmp_color = each.split("=")[1]
		elif each == "--bw":
			for each in colordict:
				colordict[each] = "black"
				sendevntcolor = "black"
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

def readGraph(filename, level=-1, body=[], label="", graphname=""):
	"""Reads a graph from a specified filename.

		Args:
			filename (str): The name of the file in which the graph 
			level (int, optional): Used for sub-statemachine purposes, this corresponds to the level in which the graph lies. If greater
				than subst_recs given at the start of the programm, this graph will be reduced to just one state (but will still have all edges).
			body (list[str], optional): Used to set the style of the body of this graph. Contains of a list of str.
			label (str, optional): Used to set the label of the graph.
			graphname (str, optional): name of the graph which will be created. Needed only for clustering of subgraphs.

		Returns:
			tuple(Digraph, list[edge], str): A tuple containing:
				1. The Digraph of the specified rootnode.
				2. A list of edges. The edges themself are tuples containing two str: The first beeing the start-node, the second beeing 
				a special string containing the event this state sends. These 'special' edges need to be accounted for.
				3. The initial state of this graph.
	"""
	# prepare return graph
	gname = filename
	if graphname:
		gname = graphname
		label = filename

	g = Digraph(gname, engine=rengine, format=fmt)

	# prepare xml tree
	tree = ET.parse(filename)
	root = tree.getroot()
	initial_state = root.attrib['initial']


	if not level == -1:
		for option in body:
			g.body.append(option)

	(g, oE, iE, subs) = iterateThroughNodes(root, g, level=level)

	if label:
		g.body.append('label = \"' + label + '\"')
	if level == -1:
		g.body.append("label=\"\nSM for " + filename + "\"")
		g.body.append('fontsize=20')
		g.node('Start', shape='Mdiamond')

		if initial_state in subs:
			g.edge('Start', subs[initial_state])
		else:
			g.edge('Start', initial_state)

		g.node('Finish', shape='Msquare')
		for each in oE:
			g.edge(each[0], 'Finish', label=each[1], color=detEdgeColor(each[1]), fontcolor=sendevntcolor)

	return (g, oE, initial_state)

def iterateThroughNodes(root, graph, level=1):
	"""Iterates through the childnodes of the given rootnode. Adds all children to a given graph.

		Args:
			root (Digraph.node): The rootnode through which shall be iterated
			graph (Digraph): The graph to which the nodes and edges will be added.
			level (int, optional): The level of the graph. 

		Returns:
			tuple(Digraph, list(outEdges), list(inEdges)): A tuple containing:
				1. The passed graph, extended with the nodes and edges found in the rootnode and its children.
				2. A list of all outgoing edges. These edges are represented as tuples of two str: The first beeing the start-node, the second beeing 
				a special string containing the event this state sends. These 'special' edges need to be accounted for.
				3. A list of all added internal edges. Returned for convenience, so this function can be used to iterate through compound states.
				4. A dictionary containing all names of substatemachines and their respective initial states.
	"""

	g = graph
	outEdges = []
	inEdges = []
	cmpstates = {}
	subsms = {}

	# first: gather all the edges
	for child in root:
		if child.tag.endswith("state"):
			# case: compound state
			if "initial" in child.attrib:
				(sg, ed) = buildMiniSg(child, label=child.attrib['id'])
				
				if minisg:
					cmpstates[child.attrib['id']] = child.attrib['initial']
					g.subgraph(sg)
					for each in ed:
						inEdges.append((each[0], each[1], each[2], detEdgeColor(each[2])))
				else:
					# make the node stand out visually, keep edges
					g.node(child.attrib['id'], style="filled")
					for each in ed:
						inEdges.append((child.attrib['id'], each[1], each[2], detEdgeColor(each[2])))
			# case: substatemachine in seperate .xml
			elif "src" in child.attrib: #WIP
				(sg, oE, ini) = readGraph(child.attrib['src'], level=level+1, body=detSubBody(level), graphname="cluster_" + child.attrib['src'])
				# case: level too big, subsm will be reduced WIP
				if level+1 >= subst_recs:
					g.node(child.attrib['id'], style="filled", shape="doublecircle")
					for out_edge in oE:
						for propTrans in child: # propably transitions
							if propTrans.tag[len(ns):] == "transition" and propTrans.attrib['event'] == child.attrib['id'] + "." + out_edge[1]:
								if 'target' in propTrans.attrib:
									target = propTrans.attrib['target']
									eventName = out_edge[0][:out_edge[0].find(".")] + "." + out_edge[0]  + "." + out_edge[1]
									inEdges.append((child.attrib['id'], target, eventName, sendevntcolor))
								else:
									for sent_evnt in propTrans:
										outEdges.append((child.attrib['id'], sent_evnt.attrib['event']))
										break
								break
				# case: draw graph completely
				else:
					subsms[child.attrib['id']] = ini
					g.subgraph(sg)
					for out_edge in oE:
						for propTrans in child: # propably transitions
							if propTrans.tag[len(ns):] == "transition" and propTrans.attrib['event'] == child.attrib['id'] + "." + out_edge[1]:
								# case: send-event
								if "target" not in propTrans.attrib:
									outEdges.append((out_edge[0], out_edge[1]))
								# case: normal transition
								else:
									target = propTrans.attrib['target']
									inEdges.append((out_edge[0], target, out_edge[1], sendevntcolor))
								break
			# case: parallel states
			elif "parallel" in child.attrib:
				print("draw parallel subgraph")
			# case: regular state
			else:
				for each in child:
					if each.tag[len(ns):] == "transition":
						# case: regular state transition
						if "target" in each.attrib:
							inEdges.append((child.attrib['id'], each.attrib['target'], each.attrib['event'], detEdgeColor(each.attrib['event'])))
						# case: send event transition
						else:
							for every in each:
								if every.tag[len(ns):] == "send":
									outEdges.append((child.attrib['id'], every.attrib['event']))
					elif each.tag[len(ns):] == "send":
						outEdges.append((child.attrib['id'], each.attrib['event']))

	# second: determine which edges remain and which ones will be replaced (because they contain cmp or sm states) 
	actual_inEdges = []

	for each in inEdges:
		edg = [each[0], each[1], each[2], each[3]]
		if each[1] in cmpstates:
			edg[1] = cmpstates[each[1]]
		if each[1] in subsms:
			edg[1] = subsms[each[1]]
		actual_inEdges.append((edg[0], edg[1], edg[2], edg[3]))

	inEdges = actual_inEdges

	# third: remove doubles (may occur because of conditions or naturally in outEdges)
	inEdges = removeDoubles(inEdges)
	outEdges = removeDoubles(outEdges, amount=2)

	# fourth: actually add the edges to the graph
	for each in inEdges:
		g.edge(each[0], each[1], label=reduTransEvnt(each[2]), color=each[3])

	return (g, outEdges, inEdges, subsms)

def removeDoubles(ed, amount=4):
	doubleless = []
	for each in ed:
		for every in doubleless:
			if amount == 4 and each[0] == every[0] and each[1] == every[1] and each[2] == every[2] and each[3] == every[3]:
			 	break
			elif each[0] == every[0] and each[1] == every[1]:
				break
		else:
			doubleless.append(each)
	return doubleless

def reduTransEvnt(event):
	"""Reduces a given event so its skills name is removed.

		Args:
			event (str): The event which shall be reduced.

		Returns:
			str: The event without its skills name.
	"""
	return event[event.find(".")+1:]

def buildMiniSg(root, label=""):
	"""Builds a subgraph from a specified root node.

		Args:
			root (Digraph.node): The root node from which this subgraph extends.
			label (str, optional): Used to label the subgraph.

		Returns:
			tuple(Digraph, list[edge]): A tuple containing:
				1. The Digraph of the specified rootnode.
				2. A list of edges. The edges themself are tuples containing four str: The first beeing the start-node, the second beeing 
					the end-node. The third one equals the event which determins the endnode. The fourth is the color in which the edge shall be rendered.
	"""
	sub = Digraph("cluster_" + label, engine=rengine, format=fmt)
	tmp = Digraph("bla")
	(tmp, oE, iE, _) = iterateThroughNodes(root, tmp)
	E = oE

	sub.body.append("\tcolor=" + cmp_color)
	sub.body.append("\tlabel = \"" + label + "\"")

	insideNodes = []
	for each in iE:
		insideNodes.append(each[0])

	for each in iE:
		if each[1] not in insideNodes:
			E.append(each)
		else:
			sub.edge(each[0], each[1], label=reduTransEvnt(each[2]), color=each[3])

	return (sub, E)

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

def detSubBody(level):
	"""Determins the suitable body for the subgraph of a graph with a given level.

	Following order is in use: No body for the main graph.

		Args:
			level (int): The level of the graph you want to determine the body of the subgraphs of. Contains of a list of str.

		Returns:
			list[str]: The body of the subgraphs of the graph with the passed body.
	"""
	level = level+1
	body = []
	if not level % 2:
		body.append('style=filled')
		body.append('color=grey')
	else:
		body.append('style=filled')
		body.append('color=white')

	return body

def draw(graph):
	"""Draws a given graph into according to the given configuration.

		Args:
			graph (Digraph): The graph that shall be rendered.
	"""
	graph.render(filename=gvname, cleanup=not savegv)

def main():
	"""Main function of this programm. Will generate a graph based on the given arguments.
	"""

	# initialize the switches and stuff
	handleArguments(sys.argv)

	# check the sanity of the given arguments
	sanityChecks()

	# generate the main graph
	(DG, edges, ini) = readGraph(inputName)

	draw(DG)

	# rename files according to cmdline parameters
	if not gvname:
		os.rename(inputName[:-4] + ".gv." + fmt, inputName[:-4] + "." + fmt)
	else:
		os.rename(gvname + "." + fmt, inputName[:-4] + "." + fmt)
	exit()

#  If this script is executed in itself, run the main method (aka generate the graph).
if __name__ == '__main__':
	main()