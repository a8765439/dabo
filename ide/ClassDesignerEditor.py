# -*- coding: utf-8 -*-
import re
import dabo
dabo.ui.loadUI("wx")
dui = dabo.ui
import dabo.dEvents as dEvents
from dabo.dLocalize import _
import ClassDesignerMenu


class EditorControl(dui.dEditor):
	"""We need to override some behaviors in order to get the editor to work
	in a code snippet environment rather than the usual single script file.
	"""
	def initProperties(self):
		self._object = None
		self._originalText = ""
		self._method = ""

	
	def afterInit(self):
		self.Language = "Python"
		key = self.Application.getUserSetting("autoCompleteKey", "F5")
		self.bindKey(key, self.autoComplete)
		
	
	def _getTextSource(self):
		return self.Form.getAllText()


	def _getRuntimeObject(self, runtimeObjectName):
		obj = self.Form.getEditedObject()
		if runtimeObjectName == "self.Form":
			return obj.Form
		if runtimeObjectName == "self.Parent":
			return obj.Parent
		else:
			return super(EditorControl, self)._getRuntimeObject(runtimeObjectName)
			

	def _makeContainingClassIntoSelf(self):
		"""Override the default behavior. Get the 'self' class from the form."""
		obj = self.Form.getEditedObject()
		if not obj:
			# Should never happen!
			dabo.ErrorLog.write(_("Bad object ref returned to _makeContainingClassIntoSelf()"))
			return None
		try:
			args = "dabo.ui.%s" % str(obj.BaseClass).split("'")[1].split(".")[-1]
			classdef = "import dabo\nclass self(%s): pass" % args
			exec classdef in self._namespaces
		except:
			# Couldn't fake the reference
			pass


	def _namespaceHacks(self):
		"""We'll want to be able to use 'dabo.' and 'dui.' to bring up
		intellisense for those two modules. We also want to add any class-wide
		import statements into the namespace.
		"""
		exec "import dabo\ndui = dabo.ui" in self._namespaces
		imp = self.Controller.getImportDict()
		if imp:
			exec imp in self._namespaces


	def _getController(self):
		try:
			return self._controller
		except AttributeError:
			self._controller = self.Application
			return self._controller

	def _setController(self, val):
		if self._constructed():
			self._controller = val
		else:
			self._properties["Controller"] = val


	def _getObject(self):
		return self._object

	def _setObject(self, val):
		if self._constructed():
			self._object = val
		else:
			self._properties["Object"] = val


	def _getOriginalText(self):
		return self._originalText

	def _setOriginalText(self, val):
		if self._constructed():
			self._originalText = val
		else:
			self._properties["OriginalText"] = val


	def _getMethod(self):
		return self._method

	def _setMethod(self, val):
		if self._constructed():
			self._method = val
		else:
			self._properties["Method"] = val


	Controller = property(_getController, _setController, None,
			_("Object to which this one reports events  (object (varies))"))
	
	Object = property(_getObject, _setObject, None,
			_("Reference to the object whose code is being edited  (obj)"))
	
	OriginalText = property(_getOriginalText, _setOriginalText, None,
			_("Stores a copy of the contents of the editor when first invoked  (str)"))
	
	Method = property(_getMethod, _setMethod, None,
			_("Name of the method of the object being edited  (str)"))
	


class EditorForm(dui.dForm):
	def afterInit(self):
		self._defaultLeft = 30
		self._defaultTop = 620
		self._defaultWidth = 800
		self._defaultHeight = 260
		self._methodNamePat = re.compile(r"^def ([^\(]+)\(")
		self._syntaxLinePat = re.compile(r"([^\(]+) \(.*, line (\d+)\)")

		self._objHierarchy = []
		pnl = dabo.ui.dPanel(self)
		self.Sizer.append1x(pnl)
		sz = pnl.Sizer = dabo.ui.dSizer("v")

		dui.dLabel(pnl, Caption=_("Object:"), RegID="lblObj")
		dui.dDropdownList(pnl, RegID="ddObject", OnHit=self.onHitDDObject)
		dui.dLabel(pnl, Caption=_("Method:"), RegID="lblMethod")
		dui.dDropdownList(pnl, RegID="ddMethod", OnHit=self.onHitDDMethod)
		hs = dui.dSizer("h", DefaultBorder=8, DefaultBorderTop=True,
				DefaultBorderBottom=True)
		hs.appendSpacer(8)
		hs.append(self.lblObj, 0, valign="middle")
		hs.appendSpacer(2)
		hs.append(self.ddObject, 0)
		hs.appendSpacer(8)
		hs.append(self.lblMethod, 0, valign="middle")
		hs.appendSpacer(2)
		hs.append(self.ddMethod, 0)
		hs.appendSpacer(4)
		dui.dBitmapButton(pnl, Picture="checkMark", RegID="btnCheckSyntax", 
				ToolTipText=_("Check Syntax"), OnHit=self.onCheckSyntax)
		dui.dButton(pnl, Caption=_("super"), RegID="btnSuperCode", Enabled=False, 
				ToolTipText=_("Show Superclass Code"), OnHit=self.onSuperCode)
		dui.dButton(pnl, Caption=_("New"), RegID="btnNewMethod", 
				ToolTipText=_("Create New Method"), OnHit=self.onNewMethod)
		hs.append(self.btnCheckSyntax, 0, border=3, valign="middle")
		hs.appendSpacer(4)
		hs.append(self.btnSuperCode, 0)
		hs.appendSpacer(8)
		hs.append(self.btnNewMethod, 0)
		hs.appendSpacer(8)
		hs.append(dui.dLine(pnl, Height=self.btnNewMethod.Height, Width=2),
				valign="middle")
		hs.appendSpacer(8)
		dui.dButton(pnl, Caption=_("Manage Imports"), RegID="btnImports",
				ToolTipText=_("Manage Class-wide imports"), OnHit=self.onManageImports)
		hs.append(self.btnImports, 0)

		sz.append(hs, 0, "x")
		EditorControl(pnl, RegID="editor")
		sz.append1x(self.editor)
		dabo.ui.callAfter(self.refreshStatus)


	def afterSetMenuBar(self):
		ClassDesignerMenu.mkDesignerMenu(self)
		fmn = self.MenuBar.append(_("Font"))
		fmn.append(_("Increase Font Size"), HotKey="Ctrl++", OnHit=self.fontIncrease)
		fmn.append(_("Decrease Font Size"), HotKey="Ctrl+-", OnHit=self.fontDecrease)
		self._autoAutoItem = fmn.append(_("Automa&tic AutoComplete"), 
				OnHit=self.onAutoAutoComp, bmp="", help=_("Toggle Automatic Autocomplete"), 
				menutype="check")


	def fontIncrease(self, evt):
		self.editor.changeFontSize("+1")


	def fontDecrease(self, evt):
		self.editor.changeFontSize("-1")


	def onMenuOpen(self, evt):
		self.Controller.menuUpdate(evt, self.MenuBar)


	def onAutoAutoComp(self, evt):
		ed = self.editor
		ed.AutoAutoComplete = not ed.AutoAutoComplete	


	def getAllText(self):
		cr = self.CodeRepository
		codeDict = cr.values()
		cd = [self.editor.Value]
		for dct in codeDict:
			cd += dct.values()
		return " ".join(cd)
		
		
	def _getMethodBase(self, mthd, isEvt):
		cd = ("def %s(self):\n\t" % mthd, "def %s(self, evt):\n\t" % mthd)
		if isEvt is None:
			return cd
		else:
			return cd[isEvt]


	def refreshCode(self):
		"""When an external event modified an object's code, this will update the 
		code displayed in the editor.
		"""
		self.edit(self.ddObject.KeyValue, discardChanges=True)
		

	def edit(self, obj, mthd=None, nonEvent=None, discardChanges=False):
		"""Opens an editor for the specified object and method."""
		if mthd is None:
			self.ddObject.KeyValue = obj
			self.populateMethodList()
			self.ddMethod.PositionValue = 0
			mthd = self.ddMethod.StringValue
		mthd = mthd.replace("*", "")
		rep = self.CodeRepository
		ed = self.editor
		if not discardChanges:
			self.updateText()
		objCode = rep.get(obj)
		mvPointer = False
		txt = ""
		if objCode:
			txt = objCode.get(mthd, "")
		superCode = ""
		if hasattr(obj, "classID"):
			superCode = self.Controller._getClassMethod(obj.classID, mthd)
		self.btnSuperCode.Enabled = bool(superCode)
		if not txt:
			mvPointer = True
			if nonEvent is None:
				nonEvent = mthd not in self.Controller.getClassEvents(obj._baseClass)
			txt = self._getMethodBase(mthd, not (nonEvent is True))
		if ed.Value != txt:
			ed.Value = txt
			ed._clearDocument(clearText=False)
		ed.OriginalText = txt
		ed.Object = obj
		ed.Method = mthd
		if mvPointer:
			ed.moveToEnd()
		dui.callAfter(self.setEditorCaption)
		self.ddObject.KeyValue = obj
		self.populateMethodList()
		try:
			self.ddMethod.StringValue = mthd
		except:
			# See if the method name is prepended with '*'
			try:
				self.ddMethod.StringValue = "*%s" % mthd
			except:
				# Add it!
				chc = self.ddMethod.Choices
				chc.append(mthd)
				self.ddMethod.Choices = chc
				self.ddMethod.StringValue = mthd


	def setEditorCaption(self):
		obj = self.ddObject.KeyValue
		if obj is None:
			nm = _("No object")
		else:
			nm = obj.Name
		mthd = self.ddMethod.StringValue
		if not mthd:
			mthd = _("no method")
		self.Caption = _("Editing: %s, %s") % (nm, mthd)


	def onDeactivate(self, evt):
		"""Make sure that any changes are saved."""
		self.updateText()


	def onCheckSyntax(self, evt):
		ed = self.editor
		txt = ed.Value
		try:
			compile(txt.strip(), "", "exec")
			dabo.ui.exclaim(_("No syntax errors found!"), _("Compilation Succeeded"))
		except SyntaxError, e:
			errMsg = "%s" % e
			try:
				msg, num = self._syntaxLinePat.findall(errMsg)[0]
			except (ValueError, IndexError):
				msg = errMsg
				num = None
			if num is not None:
				num = int(num)
				disp = _("Error: %s\nLine: %s") % (msg, num)
				ed.LineNumber = num-3
				ed.showCurrentLine()
				ed.hiliteLine(num-1)
			else:
				disp = msg
			dabo.ui.stop(disp, _("Compilation Failed"))


	def onHitDDObject(self, evt):
		self.refreshStatus()


	def onHitDDMethod(self, evt):
		self.updateText()
		dui.callAfter(self.setEditorCaption)
		self.edit(self.ddObject.KeyValue, self.ddMethod.StringValue.replace("*", ""))


	def onSuperCode(self, evt):
		self.Controller.onShowSuper(self.ddObject.KeyValue.classID, 
				self.ddMethod.StringValue)
	
	
	def onNewMethod(self, evt):
		nm = dabo.ui.getString(_("Name of method?"))
		if nm:
			# Make sure that it's legal
			nm = nm.strip()
			if not re.match("[a-zA-Z_][a-zA-Z_0-9]*", nm):
				dabo.ui.stop(_("Illegal name: %s") % nm, title=_("Illegal Name"))
				return

			# Default to the currently selected object
			obj = self.ddObject.KeyValue
			if obj is None:
				# Use the current selection
				obj = self.Controller._selection[0]
			self.edit(obj, nm, True)


	def onManageImports(self, evt):
		self.Controller.onDeclareImports(evt)


	def refreshStatus(self):
		dui.callAfter(self.setEditorCaption)
		self.populateMethodList()
		self.checkObjMethod()


	def populateMethodList(self):
		# Refresh the method list
		obj = self.ddObject.KeyValue
		if not obj:
			mthds = []
			code = {}
		else:
			mthds = self.Controller.getClassMethods(obj._baseClass)
			code = self.Controller.getCodeForObject(obj)
		chc = []
		if code is None:
			codeKeys = []
		else:
			codeKeys = code.keys()
			codeKeys.sort()
		# Add an asterisk to indicate that they have code
		for mthd in codeKeys:
			if code[mthd]:
				# There is code
				chc.append("*%s" % mthd)
				try:
					mthds.remove(mthd)
				except: pass
		
		# This may eventually be replaced by code that records your choices
		# and moves the most commonly selected methods to the top
		topMethods = ["onHit", "onContextMenu", "onKeyChar", "onMouseLeftClick", 
				"onMouseRightClick", "afterInit", "afterInitAll", "initProperties", "initEvents", 
				"validateRecord", "validateField"]
		for mthd in topMethods:
			if mthd in mthds:
				chc.append(mthd)
				mthds.remove(mthd)
		
		# Now add all the event methods
		evtMethods = [mthd for mthd in mthds
				if mthd.startswith("on")]
		for mthd in evtMethods:
			chc.append(mthd)
			mthds.remove(mthd)

		# Now add all the rest.
		for mthd in mthds:
			nm = mthd
			if nm in codeKeys:
				continue
			chc.append(nm)
		self.ddMethod.Choices = chc
		self.layout()


	def checkObjMethod(self):
		# Make sure that the current combination of the dropdowns
		# reflects the actual code being edited.
		obj = self.ddObject.KeyValue
		mthd = self.ddMethod.StringValue
		if not obj or not mthd:
			self.editor.Value = ""
			return
		self.edit(obj, mthd)


	def getEditedObject(self):
		"""Returns the object currently selected in the editor."""
		return self.ddObject.KeyValue


	def select(self, obj=None):
		"""Called when the selected object changes. 'obj' will
		be a list containing either a single object or multiple
		objects. We need to update the object dropdown in
		case any new objects were added
		"""
		fromInit = False
		if obj is None:
			obj = self.Controller.Selection
			fromInit = True
		self.refreshObjectList()
		currObj = self.ddObject.KeyValue
		if currObj is None:
			self.ddObject.PositionValue = 0
		else:
			try:
				if currObj in self.ddObject.Keys:
					self.ddObject.KeyValue = currObj
			except:
				try:
					self.ddObject.KeyValue = currObjs[0][1]
				except:
					self.ddObject.PositionValue = 0
		if currObj is not None:
			self.edit(currObj)


	def refreshObjectList(self, force=False):
		"""Update the object dropdown."""
		currObjs = self.Controller.getObjectHierarchy()
		if force or (currObjs != self._objHierarchy):
			pos = self.ddObject.PositionValue
			self._objHierarchy = currObjs
			chc = []
			keylist = []
			for lev, obj in self._objHierarchy:
				try:
					chc.append("%s %s" % ("-"*lev, obj.Name))
					keylist.append(obj)
				except:
					dabo.errorLog.write(_("Could not add to hierarchy: %s") % obj)
			self.ddObject.Choices = chc
			self.ddObject.Keys = keylist
			try:
				self.ddObject.PositionValue = pos
			except:
				pass
			self.checkObjMethod()


	def updateText(self):
		"""Called when an edited method is 'left'. Update the Controller info."""
		ed=self.editor
		rep = self.CodeRepository
		txt = ed.Value
		mthd = ed.Method
		mb = self._getMethodBase(mthd, None)
		isEmpty = (txt.strip() == "") or (txt in mb)
		obj = ed.Object
		objCode = rep.get(obj)
		if isEmpty:
			# No code. Delete the key if it is found in the repository
			if objCode is not None:
				try:
					del objCode[mthd]
				except KeyError:
					# Method hadn't been stored yet; no biggie
					pass
		else:
			# There is some text. First make sure that the name of the method wasn't changed
			try:
				codeMthd = self._methodNamePat.match(txt).groups()[0]
			except IndexError:
				codeMthd = None
			if codeMthd and (codeMthd != mthd):
				if objCode is not None:
					try:
						del objCode[mthd]
					except KeyError:
						# Method hadn't been stored yet; no biggie
						pass
				mthd = codeMthd

			# Add it to the repository.
			if hasattr(obj, "classID"):
				# Make sure that it differs from the base code for this class. If not, 
				# don't save it.
				cid = obj.classID
				cb = self._getClassMethod(cid, mthd)
				# This is dangerous! It is meant for when editing subclasses,
				# but was stripping code out of the base classes!!
# 				if txt.rstrip() == cb.rstrip():
# 					# Identical; store nothing
# 					txt = ""
			if objCode:
				txt = self._extractImports(txt)
				objCode[mthd] = txt.rstrip() + "\n"
			else:
				rep[obj] = {}
				rep[obj][mthd] = txt
		# Update the editor
		if ed.Value != txt:
			ed.Value = txt
			ed.refresh()
			curr = self.StatusText
			self.StatusText = _("Code Updated")
			dabo.ui.setAfterInterval(4000, self, "StatusText", curr)


	def _getClassMethod(self, clsID, mthd):
		return self.Controller._getClassMethod(clsID, mthd)
		
		
	def _extractImports(self, cd):
		if not cd:
			return ""
		codeLines = cd.splitlines()
		for pos, ln in enumerate(codeLines):
			if ln.lstrip()[:4] == "def ":
				break
		if pos > 0:
			self.Controller.addToImportDict(codeLines[:pos])
			ret = "\n".join(codeLines[pos:])
		else:
			ret = "\n".join(codeLines)
		return ret


	def _getCodeRepository(self):
		return self.Controller.getCodeDict()


	def _getController(self):
		try:
			return self._controller
		except AttributeError:
			self._controller = self.Application
			return self._controller

	def _setController(self, val):
		if self._constructed():
			self._controller = val
		else:
			self._properties["Controller"] = val


	CodeRepository = property(_getCodeRepository, None, None,
			_("""Reference to the Controller dictionary of all objects and their
			method code  (dict)""") )

	Controller = property(_getController, _setController, None,
			_("Object to which this one reports events  (object (varies))"))



if __name__ == "__main__":
	print
	print "=" * 66
	print "This is the file that implements the Python editor for the Class Designer." + \
			"You cannot run it directly. Please run 'ClassDesigner.py' instead."
	print "=" * 66