import wx, dabo, dabo.ui

if __name__ == "__main__":
	dabo.ui.loadUI("wx")

import dControlMixin as cm

class dGauge(wx.Gauge, cm.dControlMixin):
	""" Allows the creation of progress bars.
	"""
	def __init__(self, parent, id=-1, style=0, properties=None, *args, **kwargs):

		self._baseClass = dGauge
		properties = self.extractKeywordProperties(kwargs, properties)
		name, _explicitName = self._processName(kwargs, self.__class__.__name__)

		pre = wx.PreGauge()
		self._beforeInit(pre)
		
		pre.Create(parent, id, 100, style=style|pre.GetWindowStyle(), *args, **kwargs)

		self.PostCreate(pre)

		cm.dControlMixin.__init__(self, name, _explicitName=_explicitName)
		
		self.setProperties(properties)
		self._afterInit()


	def initEvents(self):
		#dGauge.doDefault()
		super(dGauge, self).initEvents()

	# Property get/set/del methods follow. Scroll to bottom to see the property
	# definitions themselves.
	def _getRange(self):
		return self.GetRange()
			
	def _setRange(self, value):
		self.SetRange(value)
		
	def _getOrientation(self):
		if self.IsVertical():
			return "Vertical"
		else:
			return "Horizontal"
			
	def _setOrientation(self, value):
		self.delWindowStyleFlag(wx.GA_HORIZONTAL)
		self.delWindowStyleFlag(wx.GA_VERTICAL)
		if value.lower()[:1] == "h":
			self.addWindowStyleFlag(wx.GA_HORIZONTAL)
		else:
			self.addWindowStyleFlag(wx.GA_VERTICAL)

	def _getOrientationEditorInfo(self):
		return {"editor": "list", "values": ["Horizontal", "Vertical"]}

	def _getValue(self):
		return super(dGauge, self)._getValue()
		
	def _setValue(self, value):
		super(dGauge, self)._setValue(int(value))
		
	# Property definitions:
	Orientation = property(_getOrientation, _setOrientation, None, 
			"Specifies whether the gauge is displayed as Horizontal or Vertical.")
	Range = property(_getRange, _setRange, None, 
			"Specifies the maximum value for the gauge.")
	Value = property(_getValue, _setValue, None, 
			"Specifies the state of the gauge, relative to max value.")


if __name__ == "__main__":
	import test
	class c(dGauge):
		def afterInit(self):
			self.Value = 75
	test.Test().runTest(c)
