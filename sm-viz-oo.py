import xml.etree.ElementTree as ET
from graphviz import Digraph
from init import *
import sys

"""Object oriented statemachine renderer.
"""


class Statemachine(object):
    """docstring for Statemachine"""

    def __init__(self, path="", level=0, father=0, filename="", graphname=""):
        super(Statemachine, self).__init__()
        self.pathprefix = path
        self.level = level
        self.father = father
        self.filename = filename
        self.graphname = graphname

    inEdges = []

    outEdges = []

    substatemachines = {}
    """Saved as name:initialstate
    """

    graph = 0

    body = []

    level = 0

    pathprefix = ""

    father = 0

    filename = ""

    initialstate = ""

    label = ""

    translessnodes = []  # nodes without transitionevents

    possiblereturnvalues = []

    draw = True

    def addbody(self):
        if self.level:
            for option in self.body:
                self.graph.body.append(option)

    def drawiteravly(self):
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
            together: complete filename w/ path

        Returns:
            A tuple containing the path of the file (first element) and its name (second element)

        Example:
            splitInPathAndFilename("bla/blubb") = ('bla/', 'blubb')

        """
        lastslash = -together[::-1].find('/')
        return together[:lastslash], together[lastslash:]

    @staticmethod
    def removeDoubles(edges):
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

        :return:
        """
        pass

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
        """Reads a graph from a specified filename.
        """

        self.graph = Digraph(self.graphname, engine=rengine, format=fmt)

        tree = ET.parse(self.filename)
        root = tree.getroot()
        self.initialstate = root.attrib['initial']

        self.iterateThroughNodes()

    def addEdge(self, edge):
        self.graph.edge(edge.start, edge.target, color=edge.color, label=edge.label, fontcolor=edge.fontcolor)


class Edge(object):
    """docstring for Edge"""

    def __init__(self, start="", target="", color="black", label="", fontcolor=""):
        super(Edge, self).__init__()
        self.start = start
        self.target = target
        self.color = color
        self.label = label
        self.fontcolor = fontcolor

    start = ""

    target = ""

    color = ""

    label = ""

    fontcolor = ""

#  If this script is executed in itself, run the main method (aka generate the graph).
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
