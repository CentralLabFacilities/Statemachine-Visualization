import sys
import os
from graphviz import Digraph
import xml.etree.ElementTree as ET
from data import Edge, reduTransEvnt
from typing import List
import traceback

debug = False


def debug_print(line: str) -> None:
    if debug:
        print('Debug: ' + str(line))


def readGraph(filename: str) -> ET.Element:
    filename: str = os.path.expandvars(filename)
    tree: ET.ElementTree = ET.parse(filename)
    rootnode: ET.Element = tree.getroot()
    purgeNameSpace(rootnode)
    return rootnode


def purgeNameSpace(node: ET.Element) -> None:
    node.tag = node.tag.replace('{http://www.w3.org/2005/07/scxml}', '')
    for child in node:
        purgeNameSpace(child)


def getSendEvents(statemachine: ET.Element) -> List[str]:
    sends: list(ET.Element) = statemachine.findall('.//send')
    events: list(str) = []
    for send in sends:
        if 'event' in send.attrib:
            events.append(send.attrib['event'])
    return events


def combine_events(edges: List[Edge]) -> List[Edge]:
    combined: List[Edge] = []
    for edge in edges:
        for already_in_combined in combined:
            if edge.start == already_in_combined.start and \
                            edge.target == already_in_combined.target:
                edge.events = list(set().union(edge.events, already_in_combined.events))
                break
        else:
            combined.append(edge)
    return combined


class Statemachine:
    def __init__(self, rootnode, graphname) -> None:
        self.rootnode: ET.Element = rootnode
        self.colordict: None = {"Timeout": "blue", "success": "green", "fatal": "red", "error": "red"}
        self.internalEdges: List[Edge] = []
        self.outGoingEdges: List[Edge] = []
        self.compoundStates: List[Statemachine] = []
        self.parallelStates: List[Statemachine] = []
        self.states: List[str] = []
        self.graph = Digraph(graphname, engine='dot', format='png')
        self.graph.body.append('label="' + graphname + '"')
        self.graphname: str = graphname

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

    def handleParallel(self, node: ET.Element) -> None:
        parallelmaschine: Statemachine = Statemachine(node, 'cluster_' + node.attrib['id'])
        parallelmaschine.graph.body.append('style=""')
        parallelmaschine.graph.body.append('color="black"')
        parallelmaschine.graph.body.append('label="' + node.attrib['id'] + '"')
        self.parallelStates.append(parallelmaschine)
        parallelmaschine.graph.node(node.attrib['id'], shape='triangle')
        parallelmaschine.iterateThroughNodes()
        for state in parallelmaschine.states:
            triangleEdge: Edge = Edge(start=node.attrib['id'], target=state)
            parallelmaschine.internalEdges.append(triangleEdge)
        for machine in parallelmaschine.parallelStates:
            triangleEdge: Edge = Edge(start=node.attrib['id'], target=machine.graphname.replace('cluster_', ''))
            parallelmaschine.internalEdges.append(triangleEdge)
        for machine in parallelmaschine.compoundStates:
            triangleEdge: Edge = Edge(start=node.attrib['id'], target=resolve_initial(machine))
            parallelmaschine.internalEdges.append(triangleEdge)
        for potential_transition in node:
            if potential_transition.tag.endswith('transition'):
                event_full: str = potential_transition.attrib['event']
                statename: str = event_full.split('.')[0]
                event_less: str = event_full.split('.')[1:]
                outgoing_edge: Edge = Edge()  # Find way to reconstruct state name
                for state in parallelmaschine.states:
                    if state.endswith(statename):
                        outgoing_edge.start = state
                        outgoing_edge.add_event('.'.join(event_less), '')
                for machine in parallelmaschine.parallelStates:
                    if machine.graphname.endswith(statename):
                        outgoing_edge.start = machine.graphname.replace('cluster_', '')
                        outgoing_edge.add_event('.'.join(event_less), '')
                for machine in parallelmaschine.compoundStates:
                    for encapsulated_state in get_all_states(machine):
                        if encapsulated_state.endswith(statename):
                            outgoing_edge.start = encapsulated_state
                            outgoing_edge.add_event('.'.join(event_less), '')

                if 'target' in potential_transition.attrib:
                    outgoing_edge.target = potential_transition.attrib['target']
                    self.internalEdges.append(outgoing_edge)
                else:
                    for potential_send in potential_transition:
                        if potential_send.tag == 'send':
                            outgoing_edge.add_event(reduTransEvnt(potential_transition.attrib['event']), '')
                            self.outGoingEdges.append(outgoing_edge)
                            break
                if 'cond' in potential_transition.attrib:
                    outgoing_edge.events[-1] = outgoing_edge.events[-1][0], potential_transition.attrib['cond']
        parallelmaschine.redirectNonInternalEdges()
        self.internalEdges.extend(parallelmaschine.outGoingEdges)

    def handleCmpState(self, node: ET.Element) -> None:
        compoundmaschine: Statemachine = Statemachine(node, 'cluster_' + node.attrib['id'])
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

    def handleSource(self, node: ET.Element) -> None:
        path: str = node.attrib['src']
        sourcedTree: ET.Element = readGraph(path)
        events: list(str) = getSendEvents(sourcedTree)
        eventsCatched: list(str) = []

        self.graph.node(node.attrib['id'], style='filled', shape='doubleoctagon')
        self.states.append(node.attrib['id'])
        for propTrans in node:
            if propTrans.tag == 'transition':
                ed: Edge = Edge()
                ed.start = node.attrib['id']
                cond = ''
                if 'cond' in propTrans.attrib:
                    cond = propTrans.attrib['cond']

                if 'target' in propTrans.attrib:
                    ed.target = propTrans.attrib['target']
                    event: str = reduTransEvnt(propTrans.attrib['event'])
                    ed.add_event(event, cond)
                    eventsCatched.append(event)
                    ed.color = 'blue'
                    self.internalEdges.append(ed)
                else:
                    for send_evnt in propTrans:
                        if not send_evnt.tag == 'send':
                            continue
                        event: str = send_evnt.attrib['event']
                        ed.add_event(event, cond)
                        eventsCatched.append(event)
                        self.outGoingEdges.append(ed)
                        break

                debug_print('attribs for source transitions (' + node.attrib['id'] + '): ' + str(propTrans.attrib))
        eventsNotInCatchedEvents: List[str] = [event for event in events if
                                               event not in eventsCatched and '*' not in eventsCatched]
        if len(eventsNotInCatchedEvents) > 0:
            print('Warning: Events catched and events thrown of sourced statemachine in state ' + node.attrib[
                'id'] + ' do not match!\n' + str(set(eventsNotInCatchedEvents)) + ' (not in catched events)\n' + str(
                set(events)) + ' (send events) VS \n' + str(set(eventsCatched)) + ' (catched events)')

    def handleNormalState(self, node: ET.Element) -> None:
        self.states.append(node.attrib['id'])
        for each in node:
            if each.tag == 'transition':
                # case: regular state transition
                if 'target' in each.attrib:
                    ed: Edge = Edge()
                    ed.start = node.attrib['id']
                    ed.target = each.attrib['target']
                    if 'event' in each.attrib:
                        ed.add_event(reduTransEvnt(each.attrib['event']), '')
                        ed.color = self.detEdgeColor(each.attrib['event'])
                    else:
                        print('Warning: State ' + node.attrib['id'] + ' lacks a event in a transition. Sad.')
                    if 'cond' in each.attrib:
                        ed.events[-1] = ed.events[-1][0], each.attrib['cond']
                    self.internalEdges.append(ed)
                # case: send event transition
                else:
                    for every in each:
                        if every.tag == 'send':
                            ed: Edge = Edge()
                            ed.start = node.attrib['id']
                            ed.add_event(every.attrib['event'], '')
                            if 'cond' in each.attrib:
                                ed.events[-1] = ed.events[-1][0], each.attrib['cond']
                            self.outGoingEdges.append(ed)
            elif each.tag == 'send':  # dead code?
                ed: Edge = Edge()
                ed.start = node.attrib['id']
                ed.add_event(each.attrib['event'], '')
                self.outGoingEdges.append(ed)

    def redirectInitialEdges(self) -> None:
        for edge in self.internalEdges:
            currentStatemachine: Statemachine = self
            while edge.target in [x.rootnode.attrib['id'] for x in
                                  currentStatemachine.compoundStates]:
                for x in currentStatemachine.compoundStates:
                    if x.rootnode.attrib['id'] == edge.target:
                        edge.target = x.rootnode.attrib['initial']
                        currentStatemachine = x

    def redirectNonInternalEdges(self) -> None:
        new_internalEdges: List[Edge] = []
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
        self.internalEdges = combine_events(self.internalEdges)
        self.outGoingEdges = combine_events(self.outGoingEdges)

        for each in self.internalEdges:
            self.addEdge(each)

        for each in self.outGoingEdges:
            if not each.target:
                each.target = 'Finish'
                each.fontcolor = 'blue'
            self.addEdge(each)

    def addEdge(self, edge: Edge):
        """Will add an Edge to this Graph.

        Args:
            edge: The Edge which will be added.

        Returns:
            Nothing. But will modify the graph of this statemachine.
        """
        labelevent: str = edge.get_label()
        self.graph.edge(edge.start, edge.target, color=edge.color, label=labelevent, fontcolor=edge.fontcolor)


def resolve_initial(statemachine: Statemachine) -> str:
    initial: str = statemachine.rootnode.attrib['initial']
    currentStatemachine: Statemachine = statemachine
    while initial in [x.rootnode.attrib['id'] for x in currentStatemachine.compoundStates]:
        for x in currentStatemachine.compoundStates:
            if x.rootnode.attrib['id'] == initial:
                initial = x.rootnode.attrib['initial']
                currentStatemachine = x
    return currentStatemachine.rootnode.attrib['initial']


def get_all_states(statemachine: Statemachine) -> List[str]:
    states = []
    states.extend(statemachine.states)
    for machine in statemachine.compoundStates + statemachine.parallelStates:
        states.extend(get_all_states(machine))
    return states


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[2] == '-debug':
        debug = True
    file: str = sys.argv[1]
    node = readGraph(file)
    statemachine = Statemachine(node, file)
    try:
        statemachine.iterateThroughNodes()
    except Exception as e:
        print('Got an error iterating through the nodes: ' + str(e))
        print('Exact Exception: ' + str(traceback.format_exc()))
        sys.exit(0)

    # Stuff for top level
    statemachine.graph.body.append('fontsize=20')
    statemachine.graph.node('Start', shape='Mdiamond')
    statemachine.graph.node('Finish', shape='Msquare')
    startingEdge: Edge = Edge(start='Start')
    startingEdge.target = resolve_initial(statemachine)
    statemachine.addEdge(startingEdge)

    trailingEdge: Edge = Edge(target='Finish')
    for node in statemachine.rootnode:
        if 'final' in node.attrib or ('id' in node.attrib and node.attrib['id'] == 'End'):
            trailingEdge.start = node.attrib['id']
    if trailingEdge.start:
        statemachine.addEdge(trailingEdge)

    for edge in statemachine.outGoingEdges:
        debug_print(edge)
        edge.target = 'Finish'

    debug_print('Edges: ' + str(statemachine.internalEdges))

    # draw
    try:
        statemachine.drawIteravely()
    except Exception as e:
        print('Got an error drawing the statemachine: ' + str(e))
        print('Exact Exception: ' + str(traceback.format_exc()))
        sys.exit(0)

    # render
    try:
        statemachine.graph.render(filename=file.replace('.xml', ''), cleanup=not debug)
    except Exception as e:
        print('Got an error rendering the statemachine: ' + str(e))
        print('Exact Exception: ' + str(traceback.format_exc()))
        sys.exit(0)

    sys.exit(0)
