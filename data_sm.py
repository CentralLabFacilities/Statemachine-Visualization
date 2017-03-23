
"""Data storage classes for the statemachine vizualizer.
"""

class Node(object):    
    """Class to represent Nodes appropriately"""
    def __init__(self, label='', shape='', labelcolor='black', ID=-1, slots=[]):
        super(Node, self).__init__()
        self.label = label
        self.shape = shape
        self.labelcolor = labelcolor
        self.ID = ID
        self.slots = slots

    ID = -1
    """int: The ID of the node, to identify it. -1 means the ID has not been set yet. 
    """

    label = ''
    """str: The name of the node, what will be readable in the rendered graph.
    """

    shape = ''
    """str: The shape of the node.
    """

    labelcolor = 'black'
    """str: The color this node's label will have. 
    """

    slots = []
    """list[str]: The slots this node will use.
    """


class Edge(object):
    """Class to represent Edge appropriately"""

    def __init__(self, start='', target='', color='black', label='', fontcolor='black', cond=''):
        """Contructor of the Edge class.

        Args:
            start (str, optional): The node from which this edge starts.
            target (str, optional): The node to which this edge leads.
            color (str, optional): The color of the edge.
            label (str, optional): The writing which will appear near this edge.
            fontcolor (str, optional): The color in which the label will appear.
            cond (str, optional): The condition under which this edge stands.
        """
        super(Edge, self).__init__()
        self.start = start
        self.target = target
        self.color = color
        self.label = label
        self.fontcolor = fontcolor
        self.cond = cond

    def __repr__(self):
        """For printing the Edges humanly readable.
        """
        return self.start + ', ' + self.target + ', ' + self.label + ',' + self.cond + '\n'

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

    cond = ''
    """str: The condition under which this edge stands.
    """

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
                            each.cond == every.cond and \
                            each.fontcolor == every.fontcolor:
                break
        else:
            doubleless.append(each)
    return doubleless

def reduTransEvnt(event):
    # type: (str) -> str
    """Reduces a given event so its skills name is removed.

        Args:
            event (str): The event which shall be reduced.

        Returns:
            str: The event without its skills name.
    """
    return event[event.find('.') + 1:]

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


def detEdgeColor(event, init):
    """Determins the color of a edge, given a specific event.

        Args:
            event (str): The event which will determine the color of the edge.
            init (SMinit): The init file which holds information on the desired edge color.

        Returns:
            str: A string stating the color of the edge. EG: red, blue, green etc

    """
    edgecolor = 'black'
    for each in init.colordict:
        if event.__contains__(each):
            edgecolor = init.colordict[each]
            break
    return edgecolor



def detIfComplex(target, sm):
    """Determins whether a state is a compex state (aka sourced statemachine, compound or parallel state). If so will return the type. 
    
        Args:
            target (str): The name of the state that shall be checked.
            sm (Statemachine): The Statemachine of which the complex states shall be searched.

        Return:
            str: A string stating the . Is either 'cmp', 'subst' or 'par', for compound states, sourced substatemachines and parallel states, respectively.
    """
    ret = ''
    if target in sm.cmpstates and not sm.init.exclsubst:
        ret = 'cmp'
    if target in sm.substatemachines and sm.level < sm.init.substrecs:
        ret = 'subst'
    if target in sm.parallelstates and not sm.init.exclsubst:
        ret = 'par'
    return ret