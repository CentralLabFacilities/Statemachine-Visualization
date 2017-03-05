import graphviz
import os

class SMinit(object):
    """docstring for SMinit"""
    def __init__(self):
        super(SMinit, self).__init__()


    helptext = "\
    Usage: sm-viz.py your-statemachine.xml\n\
    Possible switches:\n\t\
    --h \t\t Displays this very helpful text. \n\t\
    --ex \t\t Exclude Substatemachines in the generated graph. Actually reduces them to single states. Use this to \
    make your graph more readable. \n\t\
    --reduce=n \t Exclude all Substatemachines below n levels. Use this to make your graph more readable without \
    sacrificing inormation. \n\t\
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

    substrecs = float('inf')
    """float: Amount of recursive steps to which substate machines will be included. Usage as int, but only float supports infty.
    """

    cmpcolor = "black"
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

    exclsubst = False
    """bool: Controls if compound states shall be rendered in full or as just one state.
    """

    def handleArguments(self, args):
        """Will initialize the variables and switches necessary to use all other funtions.

            Args:
                args (list[str]): The switches with which the generator shall be initialized.
        """
        if len(args) < 2:
            print(self.helptext)
            exit(0)

        for each in args:
            if each == "-h" or each == "--h" or each == "--help" or each == "-help":
                print(self.helptext)
                exit(0)
            elif each == "--ex":
                self.exclsubst = True
                #self.substrecs = 0
            elif each.startswith("--reduce="):
                self.substrecs = int(each.split("=")[1])
            elif each.startswith("--cmpstateclr="):
                self.cmpcolor = each.split("=")[1]
            elif each == "--bw":
                for each in self.colordict:
                    self.colordict[each] = "black"
                    self.sendevntcolor = "black"
            elif each.startswith("--eventclr="):
                tmp = each.split("=")[1]
                clrs = tmp.split(",")
                for each in clrs:
                    tup = each.split(":")
                    self.colordict[tup[0]] = tup[1]
            elif each.startswith("--format="):
                tmp = each.split("=")[1]
                if tmp in graphviz.FORMATS:
                    self.fmt = tmp
                else:
                    print("Specified format not known! Will now exit.\n")
                    exit()
            elif each.endswith(".xml"):
                self.inputName = each
            elif each == "--savegv":
                self.savegv = True
            elif each.startswith("--gvname="):
                self.gvname = each.split("=")[1]
            elif each.startswith("--rengine="):
                tmp = each.split("=")[1]
                if tmp in graphviz.ENGINES:
                    self.rengine = tmp
                else:
                    print("Specified engine not known! Will now exit.\n")
                    exit()
            elif each == "--nocmpstates":
                self.minisg = False
            elif each == __file__ or each == 'sm-viz-oo.py':
                pass
            else:
                print("Parameter \"" + each + "\" not recognized. Will now exit.\n")
                exit()


    def sanityChecks(self):
        """Will check the given parameters for their sanity. Will print an errormessage and exit on broken sanity.
        """

        # no input file
        if self.inputName == "":
            print("Input file is not an .xml or not specified! Will now exit.\n")
            exit()

        # gvname specified but not savegv
        if not self.gvname == "" and not self.savegv:
            print("gvname specified but not savegv! Will now exit.\n")
            exit()
        elif not self.gvname:
            self.gvname = self.inputName[:-4]

        # gvname does not end with ".gv"
        if not self.gvname.endswith(".gv"):
            self.gvname += ".gv"

        # input file does not exist
        if not os.path.isfile(self.inputName):
            print("The file \"" + self.inputName + "\" does not exist. Will now exit.\n")
            exit()
