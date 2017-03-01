import xml.etree.ElementTree as ET
from graphviz import Digraph
from init import *
import sys

"""Object oriented statemachine renderer.
"""


class Statemachine(object):
    """Main class for all Statemachines"""

    def __init__(self, path="", level=0, father=0, filename="", graphname="", rootnode=0):
        super(Statemachine, self).__init__()
        self.pathprefix = path
        self.level = level
        self.father = father
        self.filename = filename
        self.graphname = graphname
        self.rootnode = rootnode

    inEdges = []
    """list(Edge): Contains all the edges inside the graph.
    """

    outEdges = []
    """list(Edge): Contains all the edges leading out of the graph.
    """

    substatemachines = {}
    """dict(str, str): Contains all the substatemachines of this statemachine. Saved as name:initialstate
    """

    graph = 0
    """Digraph: The graphviz graph resembling this statemachine.
    """

    body = []
    """list(str): Contains all the body options this statemachines graph will use.
    """

    level = 0
    """int: Describes this statemachines level. If a statemachine gets sourced its level will be greater than its parents one.
    """

    pathprefix = ""
    """str: The path in which the file which will be read in lies.
    """

    filename = ""
    """str: The name of the file which will be read in. See pathprefix.
    """

    father = 0
    """Statemachine: The parent of this statemachine. Will only be not 0 if it is sourced by the main Statemachine.
    """

    initialstate = ""
    """str: The initial state of this statemachine.
    """

    label = ""
    """str: The label with which this statemachine will be visualized.
    """

    translessnodes = []  # nodes without transitionevents
    """list(str): A list containing all nodes which have no transition. These nodes will either be the last ones in a \
        statemachine or ones where the statemachines creator unintentionally and mistakenly left out transitions. The \
        later case is to be avoided and thus highlighted in the visualised graph.
    """

    possiblereturnvalues = []
    """list(str): A list containing all possible return values of this statemachine.
    """

    draw = True
    """bool: Defines whether this statemachines graph will be drawn or not.
    """

    rootnode = 0
    """Some kind of ElementTree structure. The root node of this statemachine.
    """

    def addbody(self):
        """Will add all the options in body to this statemachines graph.
        """
        if self.level:
            for option in self.body:
                self.graph.body.append(option)

    def drawiteravly(self):
        """Will draw first all graphs of the substatemachines of this statemachine (recursively) and then this statemachines graph.
        """
        for each in self.substatemachines:
            self.substatemachines[each].drawiteravly()
        if self.draw:
            self.drawGraph()

    def drawGraph(self):
        self.inEdges = self.removeDoubles(self.inEdges)
        self.outEdges = self.removeDoubles(self.outEdges)
        if self.label:
            self.graph.body.append('label = \"' + self.label + '\"')
        if not self.level:
            self.graph.body.append("label=\"\nSM for " + self.filename + "\"")
            self.graph.body.append('fontsize=20')
            self.graph.node('Start', shape='Mdiamond')

            tmp = Edge(start='Start')
            if self.initialstate in self.substatemachines:
                tmp.target = self.substatemachines[self.initialstate]
            else:
                tmp.target = self.initialstate
            self.addEdge(tmp)

            self.graph.node('Finish', shape='Msquare')
            for each in self.outEdges:
                each.target = 'Finish'
                each.fontcolor = sendevntcolor
                self.addEdge(each)
            for each in self.translessnodes:
                each.target = 'Finish'
                each.label = 'unaccounted'
                each.color = 'deeppink'
                each.fontcolor = 'deeppink'
                self.addEdge(each)
        else:
            for each in self.body:
                self.graph.body.append(each)

        for each in self.inEdges:
            self.addEdge(each)

    def detEdgeColor(self, event):
        """Determins the color of a edge, given a specific event.

            Args:
                event (str): The event which will determine the color of the edge.

            Returns:
                str: A string stating the color of the edge. EG: red, blue, green etc

        """
        edgecolor = "black"
        for each in self.colordict:
            if event.__contains__(each):
                edgecolor = self.colordict[each]
                break
        return edgecolor

    def splitInPathAndFilename(self, together):
        """Splits a string into a Path and a filename

        Args:
            together (str): complete filename w/ path

        Returns:
            A tuple containing the path of the file (first element) and its name (second element)

        Example:
            splitInPathAndFilename("bla/blubb") = ('bla/', 'blubb')
            splitInPathAndFilename("blubb") = ('', 'blubb')

        """
        lastslash = -together[::-1].find('/')
        if lastslash == 1:
            return "", together
        return together[:lastslash], together[lastslash:]

    @staticmethod
    def removeDoubles(edges):
        """Will remove all doubles in the specified list of edges so that each element will be unique.
        Args:
            edges (list(Edge)): The list of edges of which doubles are to be deleted.

        Returns: 
            list(Edge): A list of edges containing all the unique elements of the input.

        """
        doubleless = []
        for each in edges:
            for every in doubleless:
                if each.start == every.start and \
                                each.target == every.target and \
                                each.color == every.color and \
                                each.label == every.label and \
                                each.fontcolor == every.fontcolor:
                    break
            else:
                doubleless.append(each)
        return doubleless

    @staticmethod
    def reduTransEvnt(event):
        """Reduces a given event so its skills name is removed.

            Args:
                event (str): The event which shall be reduced.

            Returns:
                str: The event without its skills name.
        """
        return event[event.find(".") + 1:]

    def iterateThroughNodes(self):
        """
        """
        for node in self.rootnode:
            if node.tag.endwith("state"):
                # case: compound state
                if "initial" in node.attrib:
                    self.handleCmpState(node)
                # case: sourcing of another xml file
                elif "src" in node.attrib:
                    self.handleSource(node)
                # case: parallel state
                elif "parallel" in node.attrib:
                    self.handleParallel(node)
                # case: normal node
                else:
                    for each in node:
                        if each.tag[len(ns):] == "transition":
                            # case: regular state transition
                            if "target" in each.attrib:
                                ed = Edge()
                                ed.start = node.attrib['id']
                                ed.target = each.attrib['target']
                                ed.label = self.reduTransEvnt(each.attrib['event'])
                                ed.color = self.detEdgeColor(each.attrib['event'])
                                self.inEdges.append(ed)
                            # case: send event transition
                            else:
                                for every in each:
                                    if every.tag[len(ns):] == "send":
                                        ed = Edge()
                                        ed.start = node.attrib['id']
                                        ed.label = every.attrib['event']
                                        self.outEdges.append(ed)
                        elif each.tag[len(ns):] == "send":
                            ed = Edge()
                            ed.start = node.attrib['id']
                            ed.label = each.attrib['event']
                            self.outEdges.append(ed)

    def handleCmpState(self, node):
        pass

    def handleParallel(self, node):
        pass

    def handleSource(self, node):
        src = node.attrib['src']

    def findNodesWithoutNextNode(self):
        nodes = []
        targets = []
        startnodes = []
        for each in self.inEdges:
            if each.target not in targets:
                targets.append(each.target)
                startnodes.append(each.start)
        for each in self.outEdges:
            if each.start not in startnodes:
                startnodes.append(each.start)
        for each in targets:
            if each not in startnodes:
                nodes.append(each)
        return nodes

    def readGraph(self):
        """Reads a graph from a specified filename. Will initialize this statemachines graph as well as its initial state and then call iterateThroughNodes.
        """

        self.graph = Digraph(self.graphname, engine=rengine, format=fmt)

        tree = ET.parse(self.filename)
        self.rootnode = tree.getroot()
        self.initialstate = self.rootnode.attrib['initial']

        self.iterateThroughNodes()

    def addEdge(self, edge):
        """Will add an Edge to this Graph.

        Args:
            edge: The Edge which will be added.

        Returns:
            Nothing. But will modify the graph of this statemachine.
        """
        self.graph.edge(edge.start, edge.target, color=edge.color, label=edge.label, fontcolor=edge.fontcolor)


class Edge(object):
    """Class to represent Edge appropriately"""

    def __init__(self, start="", target="", color="black", label="", fontcolor="black"):
        """Contructor of the Edge class.

        Args:
            start (str, optional): The node from which this edge starts.
            target (str, optional): The node to which this edge leads.
            color (str, optional): The color of the edge.
            label (str, optional): The writing which will appear near this edge.
            fontcolor (str, optional): The color in which the label will appear.
        """
        super(Edge, self).__init__()
        self.start = start
        self.target = target
        self.color = color
        self.label = label
        self.fontcolor = fontcolor

    start = ""
    """str: The node from which this edge starts.
    """

    target = ""
    """str: The node to which this edge leads.
    """

    color = ""
    """str: The color of the edge.
    """

    label = ""
    """str: The writing which will appear near this edge.
    """

    fontcolor = ""
    """str: The color in which the label will appear.
    """


# If this script is executed in itself, run the main method (aka generate the graph).
if __name__ == '__main__':

    # initialize the switches and stuff
    handleArguments(sys.argv)

    # check the sanity of the given arguments
    sanityChecks()

    p, fn = Statemachine.splitInPathAndFilename(inputName)

    sm = Statemachine(path=p, filename=fn)

    if not gvname:
        os.rename(inputName[:-4] + ".gv." + fmt, inputName[:-4] + "." + fmt)
    else:
        os.rename(gvname + "." + fmt, inputName[:-4] + "." + fmt)
    exit()
