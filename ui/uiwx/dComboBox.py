import wx, dabo, dabo.ui
import dabo.dEvents as dEvents
if __name__ == "__main__":
	dabo.ui.loadUI("wx")
import dDataControlMixin as dcm
from dabo.dLocalize import _

class dComboBox(wx.ComboBox, dcm.dDataControlMixin):
	""" Allows presenting a list of items for the user to choose from, as
	well as a textbox where they can enter their own value.
	"""
	def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, 
			choices=["Dabo", "Default"], style=0, properties=None, *args, **kwargs):
		
		self._baseClass = dComboBox
		properties = self.extractKeywordProperties(kwargs, properties)
		name, _explicitName = self._processName(kwargs, self.__class__.__name__)

		pre = wx.PreComboBox()
		self._beforeInit(pre)
		style=style|pre.GetWindowStyle()
		pre.Create(parent, id, pos=pos, size=size, choices=choices, *args, **kwargs)

		self.PostCreate(pre)

		dcm.dDataControlMixin.__init__(self, name, _explicitName=_explicitName)
		
		self.setProperties(properties)
		self._afterInit()


	def initEvents(self):
		#dComboBox.doDefault()
		super(dComboBox, self).initEvents()
		
		# catch the wx events and raise the dabo event:
		self.bindEvent(wx.EVT_COMBOBOX, self._onWxHit)
		self.bindEvent(wx.EVT_TEXT, self._onWxHit)

	# Property get/set/del methods follow. Scroll to bottom to see the property
	# definitions themselves.

if __name__ == "__main__":
	import test
	test.Test().runTest(dComboBox)
