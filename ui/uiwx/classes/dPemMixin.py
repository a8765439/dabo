''' dPemMixin.py: Provide common PEM functionality '''
import wx, sys, types, dabo.common

class dPemMixin(dabo.common.DoDefaultMixin):
	''' Provide Property/Event/Method interfaces for dForms and dControls.

	Subclasses can extend the property sheet by defining their own get/set
	functions along with their own property() statements.
	'''
	def __getattr__(self, att):
		''' Try to resolve att to a child object reference.

		This allows accessing children with the style:
			self.mainPanel.txtName.Value = "test"
		'''
		try:
			ret = self.FindWindowByName(att)
		except TypeError:
			ret = None
		if not ret:
			raise AttributeError, "%s object has no attribute %s" % (
				self._name, att)
		else:
			return ret

	
	def beforeInit(self, preCreateObject):
		''' Called before the wx object is fully instantiated.

		Allows things like extra style flags to be set or XRC resources to
		be loaded. Subclasses can override this as necessary.
		'''
		self._name = '?'
		self._pemObject = preCreateObject
		self.initStyleProperties()
		self._pemObject = self


	def __init__(self, *args, **kwargs):
		if self.Position == (-1, -1):
			# The object was instantiated with a default position,
			# which ended up being (-1,-1). Change this to (0,0). 
			# This is completely moot when sizers are employed.
			self.Position = (0, 0)

		if self.Size == (-1, -1):
			# The object was instantiated with a default position,
			# which ended up being (-1,-1). Change this to (0,0). 
			# This is completely moot when sizers are employed.
			self.Size = (0, 0)

		if not wx.HelpProvider.Get():
			# The app hasn't set a help provider, and one is needed
			# to be able to save/restore help text.
			wx.HelpProvider.Set(wx.SimpleHelpProvider())


	def afterInit(self):
		''' Called after the wx object's __init__ has run fully.

		Subclasses should place their __init__ code here in this hook,
		instead of overriding __init__ directly.
		'''
		self.initProperties()


	def initProperties(self):
		''' Hook for subclasses.

		Dabo Designer will set properties here, such as:
			self.Name = "MyTextBox"
			self.BackColor = (192,192,192)
		'''
		pass


	def initStyleProperties(self):
		''' Hook for subclasses.

		Dabo Designer will set style properties here, such as:
			self.BorderStyle = "Sunken"
			self.Alignment = "Center"
		'''
		pass


	def getPropertyList(classOrInstance):
		''' Return the list of properties for this object (class or instance).
		'''
		propList = []
		for item in dir(classOrInstance):
			if type(eval('classOrInstance.%s' % item)) == property:
				propList.append(item)
		return propList
	getPropertyList = classmethod(getPropertyList)


	def getPropertyInfo(self, name):
		''' Return a dict of information about the passed property name.
		'''
		propRef = eval('self.__class__.%s' % name)
		propVal = eval('self.%s' % name)

		if type(propRef) == property:
			d = {}
			d['name'] = name

			# Hide some props in the designer:
			d['showInDesigner'] = not name in ('Size', 'Position', 'WindowHandle')

			# Some props need to be initialized early. Let the designer know:
			d['preInitProperty'] = name in ('Alignment', 'BorderStyle', 'PasswordEntry')

			if propRef.fget:
				d['showValueInDesigner'] = True
			else:
				d['showValueInDesigner'] = False

			if propRef.fset:
				d['editValueInDesigner'] = True
			else:
				d['editValueInDesigner'] = False

			d['doc'] = propRef.__doc__

			dataType = type(propVal)
			d['type'] = dataType

			try:
				d['editorInfo'] = eval('self._get%sEditorInfo()' % name)
			except:
				# There isn't an explicit editor setup, so let's derive it:
				if dataType in (type(str()), type(unicode())):
					d['editorInfo'] = {'editor': 'string', 'len': 256}
				elif dataType == type(bool()):
					d['editorInfo'] = {'editor': 'boolean'}
				elif dataType in (type(int()), type(long())):
					d['editorInfo'] = {'editor': 'integer', 'min': -65535, 'max': 65536}
			return d
		else:
			raise AttributeError, "%s is not a property." % name

	
	def addObject(self, classRef, name, *args, **kwargs):
		''' Instantiate object as a child of self.
		
		The class reference must be a Dabo object (must inherit dPemMixin).
		
		The name parameter will be used on the resulting instance, and additional 
		arguments received will be passed on to the constructor of the object.
		'''
		object = classRef(self, name=name, *args, **kwargs)
		return object

	
	def escapeQt(self, s):
		sl = "\\"
		qt = "\'"
		return s.replace(sl, sl+sl).replace(qt, sl+qt)
	

	def reCreate(self, child=None):
		''' Recreate self.
		'''
		if child:
			propDict = {}
			propList = child.getPropertyList()
			for prop in propList:
				propDict[prop] = eval('child.%s' % prop)
			style = child.GetWindowStyle()
			classRef = child.__class__
			name = child.Name
			child.Destroy()
			newObj = self.addObject(classRef, name, style=style)
			for prop in propList:
				try:
					sep = ""
					val = propDict[prop]
					if type(val) in (types.UnicodeType, types.StringType):
						sep = "'"
					try:
						exp = 'self.%s.%s = %s' % (name, prop, sep+self.escapeQt(str(val))+sep)
						exec(exp)
					except:
						#pass
						print "Re-Create: could not set property:", exp

				except:
					pass
			# Now set the props which require specific orders
			newObj.Left = propDict["Left"]
			newObj.Width = propDict["Width"]
			newObj.Top = propDict["Top"]
			newObj.Height = propDict["Height"]
			
			return newObj
		else:
			return self.Parent.reCreate(self)
		
					
	# The following 3 flag functions are used in some of the property
	# get/set functions.
	def hasWindowStyleFlag(self, flag):
		''' Return whether or not the flag is set. (bool)
		'''
		return (self._pemObject.GetWindowStyleFlag() & flag) == flag

	def addWindowStyleFlag(self, flag):
		''' Add the flag to the window style.
		'''
		self._pemObject.SetWindowStyleFlag(self._pemObject.GetWindowStyleFlag() | flag)

	def delWindowStyleFlag(self, flag):
		''' Remove the flag from the window style.
		'''
		self._pemObject.SetWindowStyleFlag(self._pemObject.GetWindowStyleFlag() & (~flag))


	# Scroll to the bottom to see the property definitions.

	# Property get/set/delete methods follow.
	def _getClass(self):
		try:
			return self.__class__
		except AttributeError:
			return None

	def _getBaseClass(self):
		try:
			return self._baseClass
		except AttributeError:
			return None

	def _getSuperClass(self):
		if self.BaseClass == self.Class:
			# Any higher up goes into the wx classes:
			return None
		else:
			return self.__class__.__base__


	def _getFont(self):
		return self._pemObject.GetFont()
	
	def _getFontEditorInfo(self):
		return {'editor': 'font'}
	
	def _setFont(self, font):
		self._pemObject.SetFont(font)

		
	def _getFontInfo(self):
		return self._pemObject.GetFont().GetNativeFontInfoDesc()

	def _getFontBold(self):
		return self._pemObject.GetFont().GetWeight() == wx.BOLD
	def _setFontBold(self, fontBold):
		font = self._pemObject.GetFont()
		if fontBold:
			font.SetWeight(wx.BOLD)
		else:
			font.SetWeight(wx.LIGHT)    # wx.NORMAL doesn't seem to work...
		self._pemObject.SetFont(font)

	def _getFontItalic(self):
		return self._pemObject.Font.GetStyle() == wx.ITALIC
	def _setFontItalic(self, fontItalic):
		font = self._pemObject.Font
		if fontItalic:
			font.SetStyle(wx.ITALIC)
		else:
			font.SetStyle(wx.NORMAL)
		self._pemObject.Font = font

	def _getFontFace(self):
		return self._pemObject.Font.GetFaceName()

	def _getFontSize(self):
		return self._pemObject.Font.GetPointSize()
	def _setFontSize(self, fontSize):
		font = self._pemObject.Font
		font.SetPointSize(int(fontSize))
		self._pemObject.Font = font

	def _getFontUnderline(self):
		return self._pemObject.Font.GetUnderlined()
	def _setFontUnderline(self, val):
		# underlining doesn't seem to be working...
		font = self._pemObject.Font
		font.SetUnderlined(bool(val))
		self._pemObject.Font = font


	def _getTop(self):
		return self._pemObject.GetPosition()[1]
	def _setTop(self, top):
		self.SetPosition((self._pemObject.Left, int(top)))

	def _getLeft(self):
		return self._pemObject.GetPosition()[0]
	def _setLeft(self, left):
		self._pemObject.SetPosition((int(left), self._pemObject.Top))

	def _getPosition(self):
		return self._pemObject.GetPosition()

	def _setPosition(self, position):
		self._pemObject.SetPosition(position)

	def _getBottom(self):
		return self._pemObject.Top + self._pemObject.Height
	def _setBottom(self, bottom):
		self._pemObject.Top = int(bottom) - self._pemObject.Height

	def _getRight(self):
		return self._pemObject.Left + self._pemObject.Width
	def _setRight(self, right):
		self._pemObject.Left = int(right) - self._pemObject.Width


	def _getWidth(self):
		return self._pemObject.GetSize()[0]

	def _getWidthEditorInfo(self):
		return {'editor': 'integer', 'min': 0, 'max': 8192}

	def _setWidth(self, width):
		self.SetSize((int(width), self._pemObject.Height))


	def _getHeight(self):
		return self._pemObject.GetSize()[1]

	def _getHeightEditorInfo(self):
		return {'editor': 'integer', 'min': 0, 'max': 8192}

	def _setHeight(self, height):
		self.SetSize((self._pemObject.Width, int(height)))


	def _getSize(self): 
		return self._pemObject.GetSize()

	def _setSize(self, size):
		self._pemObject.SetSize(size)


	def _getName(self):
		name = self._pemObject.GetName()
		self._name = name      # keeps name available even after C++ object is gone.
		return name
	def _setName(self, name):
		self._name = name      # keeps name available even after C++ object is gone.
		self._pemObject.SetName(str(name))


	def _getCaption(self):
		return self._pemObject.GetLabel()
	def _setCaption(self, caption):
		self._pemObject.SetLabel(str(caption))

		# Frames have a Title separate from Label, but I can't think
		# of a reason why that would be necessary... can you? 
		self._pemObject.SetTitle(str(caption))


	def _getEnabled(self):
		return self._pemObject.IsEnabled()
	def _setEnabled(self, value):
		self._pemObject.Enable(value)


	def _getBackColor(self):
		return self._pemObject.GetBackgroundColour()

	def _getBackColorEditorInfo(self):
		return {'editor': 'colour'}

	def _setBackColor(self, value):
		self._pemObject.SetBackgroundColour(value)


	def _getForeColor(self):
		return self._pemObject.GetForegroundColour()

	def _getForeColorEditorInfo(self):
		return {'editor': 'colour'}

	def _setForeColor(self, value):
		self._pemObject.SetForegroundColour(value)


	def _getMousePointer(self):
		return self._pemObject.GetCursor()
	def _setMousePointer(self, value):
		self._pemObject.SetCursor(value)


	def _getToolTipText(self):
		t = self._pemObject.GetToolTip()
		if t:
			return t.GetTip()
		else:
			return ''

	def _getToolTipTextEditorInfo(self):
		return {'editor': 'string', 'len': 8192}

	def _setToolTipText(self, value):
		t = self._pemObject.GetToolTip()
		if t:
			t.SetTip(value)
		else:
			t = wx.ToolTip(str(value))
			self._pemObject.SetToolTip(t)


	def _getHelpContextText(self):
		return self._pemObject.GetHelpText()
	def _setHelpContextText(self, value):
		self._pemObject.SetHelpText(str(value))


	def _getVisible(self):
		return self._pemObject.IsShown()
	def _setVisible(self, value):
		self._pemObject.Show(bool(value))

	def _getParent(self):
		return self._pemObject.GetParent()
	def _setParent(self, newParentObject):
		# Note that this isn't allowed in the property definition, however this
		# is how we'd do it *if* it were allowed <g>:
		self._pemObject.Reparent(newParentObject)

	def _getWindowHandle(self):
		return self._pemObject.GetHandle()

	def _getBorderStyle(self):
		if self.hasWindowStyleFlag(wx.RAISED_BORDER):
			return 'Raised'
		elif self.hasWindowStyleFlag(wx.SUNKEN_BORDER):
			return 'Sunken'
		elif self.hasWindowStyleFlag(wx.SIMPLE_BORDER):
			return 'Simple'
		else:
			return 'None'

	def _getBorderStyleEditorInfo(self):
		return {'editor': 'list', 'values': ['None', 'Simple', 'Sunken', 'Raised']}

	def _setBorderStyle(self, style):
		self.delWindowStyleFlag(wx.NO_BORDER)
		self.delWindowStyleFlag(wx.SIMPLE_BORDER)
		self.delWindowStyleFlag(wx.SUNKEN_BORDER)
		self.delWindowStyleFlag(wx.RAISED_BORDER)

		style = str(style)

		if style == 'None':
			self.addWindowStyleFlag(wx.NO_BORDER)
		elif style == 'Simple':
			self.addWindowStyleFlag(wx.SIMPLE_BORDER)
		elif style == 'Sunken':
			self.addWindowStyleFlag(wx.SUNKEN_BORDER)
		elif style == 'Raised':
			self.addWindowStyleFlag(wx.RAISED_BORDER)
		else:
			raise ValueError, ("The only possible values are 'None', "
							"'Simple', 'Sunken', and 'Raised.'")


	# Property definitions follow
	Name = property(_getName, _setName, None, 
					'The name of the object. (str)')
	Class = property(_getClass, None, None,
					'The class the object is based on. Read-only. (class)')
	BaseClass = property(_getBaseClass, None, None, 
					'The base class of the object. Read-only. (class)')
	SuperClass = property(_getSuperClass, None, None, 
					'The parent class of the object. Read-only. (class)')

	Parent = property(_getParent, None, None,
					'The containing object. Read-only. (obj)')

	WindowHandle = property(_getWindowHandle, None, None,
					'The platform-specific handle for the window. Read-only. (long)')

	Font = property(_getFont, _setFont, None,
					'The font properties of the object. (obj)')
	FontInfo = property(_getFontInfo, None, None,
					'Specifies the platform-native font info string. Read-only. (str)')
	FontBold = property(_getFontBold, _setFontBold, None,
					'Specifies if the font is bold-faced. (bool)')
	FontItalic = property(_getFontItalic, _setFontItalic, None,
					'Specifies whether font is italicized. (bool)')
	FontFace = property(_getFontFace, None, None,
					'Specifies the font face. (str)')
	FontSize = property(_getFontSize, _setFontSize, None,
					'Specifies the point size of the font. (int)')
	FontUnderline = property(_getFontUnderline, _setFontUnderline, None,
					'Specifies whether text is underlined. (bool)')

	Top = property(_getTop, _setTop, None, 
					'The top position of the object. (int)')
	Left = property(_getLeft, _setLeft, None,
					'The left position of the object. (int)')
	Bottom = property(_getBottom, _setBottom, None,
					'The position of the bottom part of the object. (int)')
	Right = property(_getRight, _setRight, None,
					'The position of the right part of the object. (int)')
	Position = property(_getPosition, _setPosition, None, 
					'The (x,y) position of the object. (tuple)')

	Width = property(_getWidth, _setWidth, None,
					'The width of the object. (int)')
	Height = property(_getHeight, _setHeight, None,
					'The height of the object. (int)')
	Size = property(_getSize, _setSize, None,
					'The size of the object. (tuple)')


	Caption = property(_getCaption, _setCaption, None, 
					'The caption of the object. (str)')

	Enabled = property(_getEnabled, _setEnabled, None,
					'Specifies whether the object (and its children) can get user input. (bool)')

	Visible = property(_getVisible, _setVisible, None,
					'Specifies whether the object is visible at runtime. (bool)')                    


	BackColor = property(_getBackColor, _setBackColor, None,
					'Specifies the background color of the object. (tuple)')

	ForeColor = property(_getForeColor, _setForeColor, None,
					'Specifies the foreground color of the object. (tuple)')

	MousePointer = property(_getMousePointer, _setMousePointer, None,
					'Specifies the shape of the mouse pointer when it enters this window. (obj)')

	ToolTipText = property(_getToolTipText, _setToolTipText, None,
					'Specifies the tooltip text associated with this window. (str)')

	HelpContextText = property(_getHelpContextText, _setHelpContextText, None,
					'Specifies the context-sensitive help text associated with this window. (str)')

	BorderStyle = property(_getBorderStyle, _setBorderStyle, None,
					'Specifies the type of border for this window. (int). \n'
					'     None \n'
					'     Simple \n'
					'     Sunken \n'
					'     Raised')


if __name__ == "__main__":
	o = dPemMixin()
	print o.BaseClass
	o.BaseClass = "dForm"
	print o.BaseClass
