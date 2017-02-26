import xml.etree.ElementTree as ET
from graphviz import Digraph
import sys
import os.path
import os
from init import *

"""Object oriented statemachine renderer.
"""


class Statemachine(object):
    """docstring for Statemachine"""

    def __init__(self, path, level, father=0, filename="", graphname=""):
        super(Statemachine, self).__init__()
        self.pathprefix = path
        self.level = level
        self.father = father
        self.filename = filename
        self.graphname = graphname

    inEdges = []

    outEdges = []

    substatemachines = {}

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

    def addbody(self):
        if not self.level == -1:
            for option in self.body:
                self.graph.body.append(option)

    def drawiteravly(self):
        for each in self.substatemachines:
            self.substatemachines[each].drawiteravly()
        self.drawGraph()

    def drawGraph(self):
        if self.label:
            self.graph.body.append('label = \"' + self.label + '\"')
        if self.level == -1:
            self.graph.body.append("label=\"\nSM for " + self.filename + "\"")
            self.graph.body.append('fontsize=20')
            self.graph.node('Start', shape='Mdiamond')

            if self.initialstate in self.substatemachines:
                self.graph.edge('Start', self.substatemachines[self.initialstate])
            else:
                self.graph.edge('Start', self.initialstate)

            self.graph.node('Finish', shape='Msquare')
            for each in self.outEdges:
                self.graph.edge(each[0], 'Finish', label=each[1], color=self.detEdgeColor(each[1]),
                                fontcolor=sendevntcolor)
            for each in self.translessnodes:
                self.graph.edge(each, 'Finish', label='unaccounted', color='deeppink', fontcolor='deeppink')

        self.inEdges = self.removeDoubles(self.inEdges)
        self.outEdges = self.removeDoubles(self.outEdges)

        # fourth: actually add the edges to the graph
        for each in self.inEdges:
            g.edge(each[0], each[1], label=self.reduTransEvnt(each[2]), color=each[3])

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

    @staticmethod
    def removeDoubles(edges):
        doubleless = []
        for each in edges:
            for every in doubleless:
                if len(each) == 4 and each[0] == every[0] and each[1] == every[1] and each[2] == every[2] and each[3] == \
                        every[3]:
                    break
                elif each[0] == every[0] and each[1] == every[1]:
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
        return []

    def readGraph(self):
        """Reads a graph from a specified filename.
        """

        self.graph = Digraph(self.graphname, engine=rengine, format=fmt)

        tree = ET.parse(self.filename)
        root = tree.getroot()
        self.initialstate = root.attrib['initial']

        self.iterateThroughNodes()
