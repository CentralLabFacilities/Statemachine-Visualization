import xml.etree.ElementTree as ET
from graphviz import Digraph
import sys
import os.path
import os

"""object oriented statemachine renderer
"""

class Statemachine(object):
	"""docstring for Statemachine"""
	def __init__(self):
		super(Statemachine, self).__init__()

	__inEdges__ = []
	"""
	"""

	__outEdges__ = []
	"""
	"""

	__substatemachines__ = []
	"""
	"""

	__graph__ = 0
	"""
	"""

	__level__ = 0
	"""
	"""

	__body__ = []
	"""
	"""



	def draw(self):
		pass