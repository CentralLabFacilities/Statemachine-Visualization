import sys
import os
from graphviz import Digraph
import xml.etree.ElementTree as ET
from data import Edge, removeDoubles, reduTransEvnt
from typing import List

debug = False


def debug_print(line: str) -> None:
    if debug:
        print('Debug: ' + str(line))

def readGraph(filename: str) -> ET.Element:
    filename : str = os.path.expandvars(filename)
    tree : ET.ElementTree = ET.parse(filename)
    rootnode : ET.Element = tree.getroot()
    purgeNameSpace(rootnode)
    return rootnode


def purgeNameSpace(node: ET.Element) -> None:
    node.tag = node.tag.replace('{http://www.w3.org/2005/07/scxml}', '')
    for child in node:
        purgeNameSpace(child)


def getSendEvents(statemachine: ET.Element) -> List[str]:
    sends : list(ET.Element) = statemachine.findall('.//send')
    events : list(str) = []
    for send in sends:
        if 'event' in send.attrib:
            events.append(send.attrib['event'])
    return events


class Statemachine:
    def __init__(self, rootnode, graphname) -> None:
        self.rootnode : ET.Element = rootnode
        self.colordict : None = {"Timeout": "blue", "success": "green", "fatal": "red", "error": "red"}
        self.internalEdges : List[Edge] = []
        self.outGoingEdges : List[Edge] = []
        self.compoundStates : List[Statemachine] = []
        self.parallelStates : List[Statemachine] = []
        self.states : List[str] = []
        self.graph = Digraph(graphname, engine='dot', format='png')
        self.graph.body.append('label="' + graphname + '"')

    def iterateThroughNodes(self) -> None:
        for node in self.rootnode:
            if node.tag.endswith('state'):
                # case: compound state
                if 'initial' in node.attrib:
                    debug_print('Compound state: ' + node.attrib['id'])
                    self.handleCmpState(node)
                # case: sourcing of another xml file
                elif 'src' in node.attrib:
                    debug_print('Sourced state: ' + node.attrib['id'])
                    self.handleSource(node)
                # case: normal node
                else:
                    debug_print('Normal state: ' + node.attrib['id'])
                    self.handleNormalState(node)
            # case: parallel state
            elif node.tag.endswith('parallel'):
                debug_print('Parallel state: ' + node.attrib['id'])
                self.handleParallel(node)
        self.redirectInitialEdges()

    def handleCmpState(self, node : ET.Element) -> None:
        #TODO
        compoundmaschine : Statemachine = Statemachine(node, 'cluster_' + node.attrib['id'])
        compoundmaschine.graph.body.append('style=""')
        compoundmaschine.graph.body.append('color="black"')
        compoundmaschine.graph.body.append('label="' + node.attrib['id'] + '"')
        self.compoundStates.append(compoundmaschine)
        compoundmaschine.iterateThroughNodes()
        compoundmaschine.redirectNonInternalEdges()
        debug_print('compound "' + node.attrib['id'] + '" noninternal edges: ' + str(compoundmaschine.outGoingEdges))
        debug_print('compound "' + node.attrib['id'] + '" internal edges: ' + str(compoundmaschine.internalEdges))
        self.internalEdges.extend(compoundmaschine.outGoingEdges)
        compoundmaschine.outGoingEdges = []


    def handleSource(self, node : ET.Element) -> None:
        path : str = node.attrib['src']
        sourcedTree : ET.Element = readGraph(path)
        events : list(str) = getSendEvents(sourcedTree)
        eventsCatched : list(str)= []

        self.graph.node(node.attrib['id'], style='filled', shape='doublecircle')
        for propTrans in node:
            if propTrans.tag == 'transition':
                if 'target' in propTrans.attrib:
                    ed = Edge()
                    ed.start = node.attrib['id']
                    ed.target = propTrans.attrib['target']
                    ed.label = reduTransEvnt(propTrans.attrib['event'])
                    eventsCatched.append(ed.label)
                    ed.color = 'blue'
                    self.internalEdges.append(ed)
                else:
                    for send_evnt in propTrans:
                        ed = Edge()
                        ed.start = node.attrib['id']
                        ed.label = send_evnt.attrib['event']
                        eventsCatched.append(ed.label)
                        self.outGoingEdges.append(ed)
        if not set(events) == set(eventsCatched):
            print('Warning: Events catched and events thrown of sourced statemachine in state ' + node.attrib['id'] + ' do not match!')

    def handleNormalState(self, node : ET.Element) -> None:
        self.states.append(node.attrib['id'])
        for each in node:
            if each.tag == 'transition':
                # case: regular state transition
                if 'target' in each.attrib:
                    ed = Edge()
                    ed.start = node.attrib['id']
                    ed.target = each.attrib['target']
                    if 'cond' in each.attrib:
                        ed.cond = each.attrib['cond']
                    if 'event' in each.attrib:
                        ed.label = reduTransEvnt(each.attrib['event'])
                        ed.color = self.detEdgeColor(each.attrib['event'])
                    else:
                        print('Warning: State ' + node.attrib['id'] + ' lacks a event in a transition. Sad.')
                    self.internalEdges.append(ed)
                # case: send event transition
                else:
                    for every in each:
                        if every.tag == 'send':
                            ed = Edge()
                            ed.start = node.attrib['id']
                            if 'cond' in each.attrib:
                                ed.cond = each.attrib['cond']
                            ed.label = every.attrib['event']
                            self.outGoingEdges.append(ed)
            elif each.tag == 'send':#dead code?
                ed = Edge()
                ed.start = node.attrib['id']
                ed.label = each.attrib['event']
                self.outGoingEdges.append(ed)

    def handleParallel(self, node : ET.Element) -> None:
        #TODO
        print('Parallels not supported at this time, will exit now!')
        sys.exit(0)

    def redirectInitialEdges(self) -> None:
        for edge in self.internalEdges:
            currentStatemachine : Statemachine = self
            while edge.target in [x.rootnode.attrib['id'] for x in
                              currentStatemachine.compoundStates + currentStatemachine.parallelStates]:
                for x in currentStatemachine.compoundStates + currentStatemachine.parallelStates:
                    if x.rootnode.attrib['id'] == edge.target:
                        edge.target = x.rootnode.attrib['initial']
                        currentStatemachine = x

    def redirectNonInternalEdges(self) -> None:
        new_internalEdges : List[Edge] = []
        for edge in self.internalEdges:
            if edge.target not in self.states:
                self.outGoingEdges.append(edge)
            else:
                new_internalEdges.append(edge)
        self.internalEdges = new_internalEdges

    def detEdgeColor(self, event):
        """Determins the color of a edge, given a specific event.

            Args:
                event (str): The event which will determine the color of the edge.
                init (SMinit): The init file which holds information on the desired edge color.

            Returns:
                str: A string stating the color of the edge. EG: red, blue, green etc

        """
        edgecolor = 'black'
        for each in self.colordict:
            if each in event:
                edgecolor = self.colordict[each]
                break
        return edgecolor

    def drawIteravely(self):
        """Will draw first all graphs of the substatemachines of this statemachine (recursively) and then this statemachines graph.
        """
        for compound in self.compoundStates:
            compound.drawIteravely()
            self.graph.subgraph(compound.graph)
        for parallel in self.parallelStates:
            parallel.drawIteravely()
            self.graph.subgraph(parallel.graph)
        self.drawGraph()

    def drawGraph(self):
        self.internalEdges = removeDoubles(self.internalEdges)
        self.outGoingEdges = removeDoubles(self.outGoingEdges)

        for each in self.internalEdges:
            self.addEdge(each)

        for each in self.outGoingEdges:
            if not each.target:
                each.target = 'Finish'
                each.fontcolor = 'blue'
            self.addEdge(each)

    def addEdge(self, edge):
        """Will add an Edge to this Graph.

        Args:
            edge: The Edge which will be added.

        Returns:
            Nothing. But will modify the graph of this statemachine.
        """
        labelcond = edge.label
        if edge.cond:
            labelcond = labelcond + ' (' + edge.cond +')'
        self.graph.edge(edge.start, edge.target, color=edge.color, label=labelcond , fontcolor=edge.fontcolor)


if __name__ == '__main__':
    file : str = sys.argv[1]
    node = readGraph(file)
    statemachine = Statemachine(node, file)
    try:
        statemachine.iterateThroughNodes()
    except Exception as e:
        print('Got an error iterating through the nodes: ' + str(e))
        sys.exit(0)

    # Stuff for top level
    statemachine.graph.body.append('fontsize=20')
    statemachine.graph.node('Start', shape='Mdiamond')
    statemachine.graph.node('Finish', shape='Msquare')
    startingEdge : Edge = Edge(start='Start')
    initial : str = statemachine.rootnode.attrib['initial']
    currentStatemachine : Statemachine = statemachine
    while initial in [x.rootnode.attrib['id'] for x in currentStatemachine.compoundStates + currentStatemachine.parallelStates]:
        for x in currentStatemachine.compoundStates + currentStatemachine.parallelStates:
            if x.rootnode.attrib['id'] == initial:
                initial = x.rootnode.attrib['initial']
                currentStatemachine = x
    startingEdge.target = currentStatemachine.rootnode.attrib['initial']
    statemachine.addEdge(startingEdge)

    trailingEdge : Edge = Edge(target='Finish')
    for node in statemachine.rootnode:
        if 'final' in node.attrib:
            trailingEdge.start = node.attrib['id']
    if trailingEdge.start:
        statemachine.addEdge(trailingEdge)

    debug_print('Edges: ' + str(statemachine.internalEdges))

    # draw
    try:
        statemachine.drawIteravely()
    except Exception as e:
        print('Got an error drawing the statemachine: ' + str(e))
        sys.exit(0)

    # render
    try:
        statemachine.graph.render(filename=file.replace('.xml', ''), cleanup=not debug)
    except Exception as e:
        print('Got an error rendering the statemachine: ' + str(e))
        sys.exit(0)

    sys.exit(0)