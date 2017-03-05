import os
import xml.etree.ElementTree as ET
from graphviz import Digraph
from init import SMinit
import sys

"""Object oriented statemachine renderer.
Some Details about the Graphviz API:
The order of commands is quite important. 
Any graph that is made a subgraph of another graph needs to be completed. This means that every edge 
must be added to the graph and every body modification must be appended BEFORE the subgraph-method is called.
"""


class Statemachine(object):
    """Main class for all Statemachines"""

    def __init__(self, path="", level=0, father=0, filename="", graphname="", rootnode=0, init=0, body=[]):
        super(Statemachine, self).__init__()
        self.pathprefix = path
        self.level = level
        self.father = father
        self.filename = filename
        self.graphname = graphname
        self.rootnode = rootnode
        self.init = init
        self.body = body
        self.inEdges = []
        self.outEdges = []
        self.substatemachines = []
        self.substatemachinenames = {}
        self.cmpstates = []
        self.cmpstatenames = {}
        self.parallelstates = []
        self.parallelstatenames = {}
        self.graph = 0
        self.initialstate = ''
        self.label = ''
        self.translessnodes = []
        self.possiblereturnvalues = []
        self.draw = True



    init = 0
    """SMinit: contains all the information given by initialisation.
    """

    inEdges = []
    """list[Edge]: Contains all the edges inside the graph.
    """

    outEdges = []
    """list[Edge]: Contains all the edges leading out of the graph.
    """

    substatemachines = []
    """list[Statemachine] Contains all the Statemachines that are substatemachines of this statemachine.
    """

    substatemachinenames = {}
    """dict(str, str): Contains all the substatemachinenames of this statemachine. Saved as name:initialstate
    """

    cmpstates = []
    """list[Statemachine] Contains all the Statemachines that represent compound states of this Statemachine
    """

    cmpstatenames = {}
    """dict[str, str]: Contains all the names of compound states of this statemachine. Saved as name of compoundstate:initialstate
    """

    parallelstates = []
    """list[Statemachine] Contains all the Statemachines that represent parallel states of this Statemachine
    """

    parallelstatenames = {}
    """dict[str, str]: Contains all the names of parallel states of this statemachine. Saved as name of parallelstate:initialstate
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

    pathprefix = ''
    """str: The path in which the file which will be read in lies.
    """

    filename = ''
    """str: The name of the file which will be read in. See pathprefix.
    """

    father = 0
    """Statemachine: The parent of this statemachine. Will only be not 0 if it is sourced by the main Statemachine.
    """

    initialstate = ''
    """str: The initial state of this statemachine.
    """

    label = ''
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
            if each.draw:
                each.drawiteravly()
                self.graph.subgraph(each.graph)
        for each in self.cmpstates:
            if each.draw:
                each.drawiteravly()
                self.graph.subgraph(each.graph)
        if self.draw:
            self.drawGraph()

    def drawGraph(self):
        self.inEdges = self.removeDoubles(self.inEdges)
        self.outEdges = self.removeDoubles(self.outEdges)
        if self.label:
            self.graph.body.append('label = \"' + self.label + '\"')
        if not self.level:
            self.graph.body.append('label=\"\nSM for ' + self.filename + '\"')
            self.graph.body.append('fontsize=20')
            self.graph.node('Start', shape='Mdiamond')

            tmp = Edge(start='Start')
            if self.initialstate in self.substatemachinenames:
                tmp.target = self.substatemachinenames[self.initialstate]
            else:
                tmp.target = self.initialstate
            self.addEdge(tmp)

            self.graph.node('Finish', shape='Msquare')
            for each in self.outEdges:
                if not each.target:
                    each.target = 'Finish'
                    each.fontcolor = self.init.sendevntcolor
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
        edgecolor = 'black'
        for each in self.init.colordict:
            if event.__contains__(each):
                edgecolor = self.init.colordict[each]
                break
        return edgecolor

    @staticmethod
    def splitInPathAndFilename(together):
        # type: (str) -> (str, str)
        """Splits a string into a Path and a filename

        Args:
            together (str): complete filename w/ path

        Returns:
            A tuple containing the path of the file (first element) and its name (second element)

        Example:
            splitInPathAndFilename('bla/blubb') = ('bla/', 'blubb')
            splitInPathAndFilename('blubb') = ('', 'blubb')

        """
        lastslash = -together[::-1].find('/')
        if lastslash == 1:
            return '', together
        return together[:lastslash], together[lastslash:]

    @staticmethod
    def removeDoubles(edges):
        # type: (list[Edge]) -> list[Edge]
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
        # type: (str) -> str
        """Reduces a given event so its skills name is removed.

            Args:
                event (str): The event which shall be reduced.

            Returns:
                str: The event without its skills name.
        """
        return event[event.find('.') + 1:]

    def iterateThroughNodes(self):
        """
        """
        for node in self.rootnode:
            if node.tag.endswith('state'):
                # case: compound state
                if 'initial' in node.attrib:
                    self.handleCmpState(node)
                # case: sourcing of another xml file
                elif 'src' in node.attrib:
                    self.handleSource(node)
                # case: parallel state
                elif 'parallel' in node.attrib:
                    self.handleParallel(node)
                # case: normal node
                else:
                    self.handleNormalState(node)
        self.redirectInitialEdges()


    def redirectInitialEdges(self):
        """Redirects Edges that are targeted at compound, sourced and parallel states to their respective initial states.
        """
        for edge in self.inEdges:
            if edge.target in self.cmpstatenames and not self.init.exclsubst:
                edge.target = self.cmpstatenames[edge.target]
            elif edge.target in self.substatemachinenames and self.level < self.init.substrecs:
                edge.target = self.substatemachinenames[edge.target]
            elif edge.target in self.parallelstatenames and not self.init.exclsubst:
            	edge.target = self.parallelstatenames[edge.target]

    def handleCmpState(self, node):
        self.cmpstatenames[node.attrib['id']] = node.attrib['initial']
        cmpsm = Statemachine(init=self.init, path=self.pathprefix)
        self.cmpstates.append(cmpsm)
        cmpsm.father = self
        cmpsm.level = self.level + 1
        cmpsm.label = node.attrib['id']
        cmpsm.rootnode = node
        cmpsm.graphname = 'cluster_' + node.attrib['id']
        cmpsm.graph = Digraph(cmpsm.graphname, engine=self.init.rengine, format=self.init.fmt)
        cmpsm.initialstate = node.attrib['initial']
        cmpsm.body.append("color=" + self.init.cmpcolor)
        cmpsm.body.append("style=\"\"")

        cmpsm.iterateThroughNodes()

        nodesInCmpsm = []
        for each in node:
            nodesInCmpsm.append(each.attrib['id'])

        edgesToSwitch = []

        for each in cmpsm.inEdges:
            if each.target not in nodesInCmpsm:
                edgesToSwitch.append(each)
        for each in edgesToSwitch:
            cmpsm.inEdges.remove(each)
            cmpsm.outEdges.append(each)

        for each in cmpsm.outEdges:
            if self.init.exclsubst:
                each.start = self.cmpstatenames[node.attrib['id']]
                self.inEdges.append(each)
            else:
                if each.target:
                    self.inEdges.append(each)
                else:
                    self.outEdges.append(each)

        if self.init.exclsubst:
            self.graph.node(node.attrib['id'], style="filled")
            cmpsm.draw = False
            for ed in cmpsm.outEdges:
            	ed.start = node.attrib['id']

    def handleParallel(self, node):
        pass

    def handleSource(self, node):
        subpath, newfile = self.splitInPathAndFilename(node.attrib['src'])
        completepath = self.pathprefix + subpath
        newsm = Statemachine(path=completepath, filename=newfile, init=self.init)
        newsm.father = self
        newsm.graphname = 'cluster_' + newfile
        newsm.level = self.level + 1
        newsm.label = newfile
        if self.level + 1 >= self.init.substrecs:
            newsm.draw = False
        newsm.readGraph()
        self.substatemachinenames[node.attrib['src']] = newsm.initialstate
        # case: complete subsm will get rendered
        if newsm.draw:
            self.graph.subgraph(newsm.graph)
            for out_edge in newsm.outEdges:
                for propTrans in node:  # propably transitions
                    if propTrans.tag[len(self.init.ns):] == 'transition' and propTrans.attrib['event'] == node.attrib[
                        'id'] + '.' + out_edge.label:
                        # case: send-event
                        if 'target' not in propTrans.attrib:
                            self.outEdges.append(out_edge)
                        # case: normal transition
                        else:
                            out_edge.target = propTrans.attrib['target']
                            out_edge.color = self.init.sendevntcolor
                            self.inEdges.append(out_edge)
                        break
        # case: subsm will be reduced to a single node
        else:
            self.graph.node(node.attrib['id'], style='filled', shape='doublecircle')
            for out_edge in newsm.outEdges:
                for propTrans in node:  # propably transitions
                    if propTrans.tag[len(self.init.ns):] == 'transition' and propTrans.attrib['event'] == node.attrib['id'] + '.' \
                            + out_edge.label:
                        if 'target' in propTrans.attrib:
                            target = propTrans.attrib['target']
                            eventName = out_edge.start[
                                        :out_edge.start.find('.')] + '.' + out_edge.start + '.' + out_edge.label
                            ed = Edge()
                            ed.start = node.attrib['id']
                            ed.target = target
                            ed.label = self.reduTransEvnt(eventName)
                            ed.color = self.init.sendevntcolor
                            self.inEdges.append(ed)
                        else:
                            for sent_evnt in propTrans:
                                ed = Edge()
                                ed.start = node.attrib['id']
                                ed.label = sent_evnt.attrib['event']
                                self.outEdges.append(ed)
                                break
                        break

    def handleNormalState(self, node):
        for each in node:
            if each.tag[len(self.init.ns):] == 'transition':
                # case: regular state transition
                if 'target' in each.attrib:
                    ed = Edge()
                    ed.start = node.attrib['id']
                    ed.target = each.attrib['target']
                    ed.label = self.reduTransEvnt(each.attrib['event'])
                    ed.color = self.detEdgeColor(each.attrib['event'])
                    self.inEdges.append(ed)
                # case: send event transition
                else:
                    for every in each:
                        if every.tag[len(self.init.ns):] == 'send':
                            ed = Edge()
                            ed.start = node.attrib['id']
                            ed.label = every.attrib['event']
                            self.outEdges.append(ed)
            elif each.tag[len(self.init.ns):] == 'send':
                ed = Edge()
                ed.start = node.attrib['id']
                ed.label = each.attrib['event']
                self.outEdges.append(ed)

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

        self.graph = Digraph(self.graphname, engine=self.init.rengine, format=self.init.fmt)

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

    def __init__(self, start='', target='', color='black', label='', fontcolor='black'):
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

    def __repr__(self):
        """For printing the Edges humanly readable.
        """
        return self.start + ', ' + self.target + ', ' + self.label + '\n'

    start = ''
    """str: The node from which this edge starts.
    """

    target = ''
    """str: The node to which this edge leads.
    """

    color = ''
    """str: The color of the edge.
    """

    label = ''
    """str: The writing which will appear near this edge.
    """

    fontcolor = ''
    """str: The color in which the label will appear.
    """


# If this script is executed in itself, run the main method (aka generate the graph).
if __name__ == '__main__':
    init = SMinit()
    fmt = init.fmt
    inName = init.inputName


    # initialize the switches and stuff
    init.handleArguments(sys.argv)  # check the sanity of the given arguments
    init.sanityChecks()

    p, fn = Statemachine.splitInPathAndFilename(init.inputName)

    sm = Statemachine(path=p, filename=fn, init=init)

    sm.readGraph()

    sm.drawiteravly()

    sm.graph.render(filename=fn[:-4]+'.gv', cleanup=not init.savegv)
    if init.gvname:
        os.rename(fn[:-4] + '.gv.' + fmt, fn[:-4] + '.' + fmt)
    else:
        os.rename(init.gvname + '.' + fmt, fn[:-4] + '.' + fmt)
    exit()
