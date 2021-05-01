import unittest

import terminal
import tanmatsu
import widgets


class ChildWidget(widgets.TextBox):
	class Meta:
		lines = ["Child Widget"]


class ParentWidget(widgets.FlexBox):
	child1 = ChildWidget()
	child2 = ChildWidget()
	child3 = ChildWidget()
	child4 = ChildWidget()
	child5 = ChildWidget()


class RootWidget(widgets.FlexBox):
	parent1 = ParentWidget()
	parent2 = ParentWidget()


class TestFocusSwitching(unittest.TestCase):
	def setUp(self):
		self.term = terminal.Terminal()
		self.tanm = tanmatsu.Tanmatsu()
		
		self.root_widget = RootWidget()
		self.tanm.set_root_widget(self.root_widget)
	
	def tearDown(self):
		self.term.__exit__(None, None, None)
	
	def test_forward(self):
		self.assertEqual(self.tanm.get_current_focused_widget(), self.root_widget)
		
		for i in range(0, 8):
			self.tanm.tab()
		
		self.assertEqual(self.tanm.get_current_focused_widget(), self.root_widget.parent2.child1)
	
	def test_backward(self):
		self.assertEqual(self.tanm.get_current_focused_widget(), self.root_widget)
		
		for i in range(0, 8):
			self.tanm.tab(reverse=True)
