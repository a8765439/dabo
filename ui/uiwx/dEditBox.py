import wx, dabo, dabo.ui

if __name__ == "__main__":
	dabo.ui.loadUI("wx")

import dDataControlMixin as dcm
import dabo.dEvents as dEvents
from dabo.dLocalize import _

# The EditBox is just a TextBox with some additional styles.

class dEditBox(wx.TextCtrl, dcm.dDataControlMixin):
	""" Allows editing of string or unicode data of unlimited length.
	"""
	_IsContainer = False
	
	def __init__(self, parent, properties=None, *args, **kwargs):
		self._baseClass = dEditBox
		preClass = wx.PreTextCtrl
		kwargs["style"] = wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_LINEWRAP
		dcm.dDataControlMixin.__init__(self, preClass, parent, properties, *args, **kwargs)


	def _initEvents(self):
		super(dEditBox, self)._initEvents()
		self.Bind(wx.EVT_TEXT, self._onWxHit)
		

	def selectAll(self):
		"""Each subclass must define their own selectAll method. This will 
		be called if SelectOnEntry is True when the control gets focus.
		"""
		self.SetSelection(-1, -1)
		
		
	# property get/set functions
	def _getAlignment(self):
		if self.hasWindowStyleFlag(wx.TE_RIGHT):
			return 'Right'
		elif self.hasWindowStyleFlag(wx.TE_CENTRE):
			return 'Center'
		else:
			return 'Left'

	def _getAlignmentEditorInfo(self):
		return {'editor': 'list', 'values': ['Left', 'Center', 'Right']}

	def _setAlignment(self, value):
		self.delWindowStyleFlag(wx.TE_LEFT)
		self.delWindowStyleFlag(wx.TE_CENTRE)
		self.delWindowStyleFlag(wx.TE_RIGHT)

		value = str(value).lower()

		if value == 'left':
			self.addWindowStyleFlag(wx.TE_LEFT)
		elif value == 'center':
			self.addWindowStyleFlag(wx.TE_CENTRE)
		elif value == 'right':
			self.addWindowStyleFlag(wx.TE_RIGHT)
		else:
			raise ValueError, ("The only possible values are "
							"'Left', 'Center', and 'Right'.")

	def _getReadOnly(self):
		return not self._pemObject.IsEditable()
	def _setReadOnly(self, value):
		self._pemObject.SetEditable(not value)
	
	def _getSelectOnEntry(self):
		try:
			return self._SelectOnEntry
		except AttributeError:
			return False
	def _setSelectOnEntry(self, value):
		self._SelectOnEntry = bool(value)

	# property definitions follow:
	Alignment = property(_getAlignment, _setAlignment, None,
		"""Specifies the alignment of the text.
		
		Left (default)
		Center
		Right
		""")
	
	ReadOnly = property(_getReadOnly, _setReadOnly, None, 
		"""Specifies whether or not the text can be edited.""")
	
	SelectOnEntry = property(_getSelectOnEntry, _setSelectOnEntry, None, 
		"""Specifies whether all text gets selected upon receiving focus.""")


if __name__ == "__main__":
	import test
	test.Test().runTest(dEditBox)
