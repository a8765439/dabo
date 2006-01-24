import string
from dabo.dLocalize import _


class PropertyHelperMixin(object):
	""" Helper functions for getting information on class properties.
	"""

	def _expandPropStringValue(self, value, propList):
		""" Called from various property setters: expand value into one of the
		accepted property values in propList. We allow properties to be set
		using case-insensitivity, and for properties with distinct first letters
		for user code to just set the property using the first letter.
		"""
		value = value.lower().strip()
		
		uniqueFirstLetter = True
		firstLetterCounts = {}
		firstLetters = {}
		lowerPropMap = {}
		for idx, prop in enumerate(propList):
			if prop is None:
				continue
			letter = prop[0:1].lower()
			firstLetterCounts[letter] = firstLetterCounts.get(letter, 0) + 1
			if firstLetterCounts[letter] > 1:
				uniqueFirstLetter = False
			firstLetters[letter] = propList[idx]
			lowerPropMap[prop.lower().strip()] = prop

		if uniqueFirstLetter:
			# just worry about the first letter in value:
			value = firstLetters.get(value[0:1])
		else:
			value = lowerPropMap.get(value)
		
		if value is None:
			if None not in propList:
				s = _("The only accepted values for this property are ")
				for idx, p in enumerate(propList):
					if idx == len(propList) - 1:
						s += """%s '%s'.""" % (_("and"), p)
					else:
						s += """'%s', """ % p
				raise ValueError, s
		return value


	def _extractKeywordProperties(self, kwdict, propdict):
		""" Called from __init__: puts any property keyword arguments into
		the property dictionary, so that __init__ can pass that dict to 
		setProperties() when appropriate (and so the property keywords are
		removed before sending **kwargs to the wx constructor).
		"""
		if propdict is None:
			propdict = {}
		props = self.getPropertyList()
		for arg in kwdict.keys():
			if arg in props:
				propdict[arg] = kwdict[arg]
				del kwdict[arg]
		return propdict
	
	
	def _extractKey(self, kwdict, key, defaultVal=None):
		""" If the supplied key is present in the kwdict, the associated
		value is returned, and that key's element is deleted from the
		dict. If the key doesn't exist, the default value is returned. If
		kwdict is a tuple/list, it will look in each element until a value
		is found.
		"""
		if not isinstance(kwdict, (tuple, list)):
			kwdict = (kwdict, )
		ret = defaultVal
		for dd in kwdict:
			if dd is None:
				continue
			try:
				ret = dd[key]
				del dd[key]
				break
			except KeyError:
				pass
		return ret
			
				
	def getProperties(self, propertySequence=(), propsToSkip=(),
			ignoreErrors=False, *propertyArguments):
		""" Returns a dictionary of property name/value pairs.
		
		If a sequence of properties is passed, just those property values
		will be returned. Otherwise, all property values will be returned.
		The sequence of properties can be a list, tuple, or plain string
		positional arguments. For instance, all of the following are
		equivilent:
			
			print self.getProperties("Caption", "FontInfo", "Form")
			print self.getProperties(["Caption", "FontInfo", "Form"])
			t = ("Caption", "FontInfo", "Form")
			print self.getProperties(t)
			print self.getProperties(*t)
			
		An exception will be raised if any passed property names don't 
		exist, aren't actual properties, or are not readable (do not have
		getter functions).
		
		However, if an exception is raised from the property getter function,
		the exception will get caught and used as the property value in the 
		returned property dictionary. This allows the property list to be 
		returned even if some properties can't be evaluated correctly by the 
		object yet.
		"""
		propDict = {}
		
		def _fillPropDict(_propSequence):
			for prop in _propSequence:
				if prop in propsToSkip:
					continue
				propRef = eval("self.__class__.%s" % prop)
				if type(propRef) == property:
					getter = propRef.fget
					if getter is not None:
						try:
							propDict[prop] = getter(self)
						except Exception, e:
							propDict[prop] = e
					else:
						if not ignoreErrors:
							raise ValueError, "Property '%s' is not readable." % prop
						pass
				else:
					raise AttributeError, "'%s' is not a property." % prop
					
		if isinstance(propertySequence, (list, tuple)):
			_fillPropDict(propertySequence)
		else:
			if isinstance(propertySequence, basestring):
				# propertySequence is actually a string property name:
				# append to the propertyArguments tuple.
				propertyArguments = list(propertyArguments)
				propertyArguments.append(propertySequence)
				propertyArguments = tuple(propertyArguments)
		_fillPropDict(propertyArguments)
		
		if len(propertyArguments) == 0 and len(propertySequence) == 0:
			# User didn't send a list of properties, so return all properties:
			_fillPropDict(self.getPropertyList())
			
		return propDict

	
	def setProperties(self, propDict={}, ignoreErrors=False, **propKw):
		""" Sets a group of properties on the object all at once.
			
		You have the following options for sending the properties:
			1) Property/Value pair dictionary
			2) Keyword arguments
			3) Both
	
		The following examples all do the same thing:
		self.setProperties(FontBold=True, ForeColor="Red")
		self.setProperties({"FontBold": True, "ForeColor": "Red"})
		self.setProperties({"FontBold": True}, ForeColor="Red")
		"""
		def _setProps(_propDict):
			for prop in _propDict.keys():
				propRef = eval("self.__class__.%s" % prop)
				if type(propRef) == property:
					setter = propRef.fset
					if setter is not None:
						setter(self, _propDict[prop])
					else:
						if not ignoreErrors:
							raise ValueError, "Property '%s' is read-only." % prop
				else:
					raise AttributeError, "'%s' is not a property." % prop
					
		# Set the props specified in the passed propDict dictionary:
		_setProps(propDict)
	
		# Set the props specified in the keyword arguments:
		_setProps(propKw)

			
	def setPropertiesFromAtts(self, propDict={}, ignoreExtra=True):
		""" Sets a group of properties on the object all at once. This
		is different from the regular setProperties() method because
		it only accepts a dict containing prop:value pairs, and it
		assumes that the value is always a string. It will convert
		the value to the correct type for the property, and then set
		the property to that converted value.
		"""
		for prop, val in propDict.items():
			if not hasattr(self, prop):
				# Not a valid property
				if ignoreExtra:
					# ignore
					continue
				else:
					raise AttributeError, "'%s' is not a property." % prop				
			try:
				exec("self.%s = %s" % (prop, val) )
			except:
				# If this is property holds strings, we need to quote the value.
				try:
					exec("self.%s = '%s'" % (prop, val) )
				except:
					raise ValueError, "Could not set property '%s' to value: %s" % (prop, val)
		
			
	def getPropertyList(cls, refresh=False):
		""" Returns the list of properties for this object (class or instance).
		"""
		try:
			propLists = cls._propLists
		except:
			propLists = None

		try:
			propList = cls._propLists[cls]
		except:
			propList = None

		if refresh:
			propList = None

		if isinstance(propList, list):
			## A prior call has already generated the propList
			return propList

		propList = []
		for c in cls.__mro__:
			for item in dir(c):
				if item[0] in string.uppercase:
					if c.__dict__.has_key(item):
						if type(c.__dict__[item]) == property:
							if propList.count(item) == 0:
								propList.append(item)
		propList.sort()
		if not hasattr(cls, "_propLists"):
			cls._propLists = {}
		cls._propLists[cls] = propList
		return propList
	getPropertyList = classmethod(getPropertyList)


	def getPropertyInfo(cls, name):
		""" Returns a dictionary of information about the passed property name.
		"""
		# cls can be either a class or self
		classRef = cls
		try:
			issubclass(cls, object)
		except TypeError:
			classRef = cls.__class__

		propRef = getattr(classRef, name)

		if type(propRef) == property:
			if propRef.fget is None:
				# With no getter, the property's value cannot be determined
				propVal = None
			else:
				try:
					propVal = propRef.fget(cls)
				except:
					# There are many reasons the propval may not be determined for now, 
					# such as not being a live instance.
					propVal = None
	
			d = {}
			d["name"] = name

			if propRef.fget:
				d["readable"] = True
			else:
				d["readable"] = False

			if propRef.fset:
				d["writable"] = True
			else:
				d["writable"] = False

			d["doc"] = propRef.__doc__

			dataType = d["type"] = type(propVal)

			d["definedIn"] = None			
			for o in classRef.__mro__:
				if o.__dict__.has_key(name):
					d["definedIn"] = o

			return d
		else:
			raise AttributeError, "%s is not a property." % name
	getPropertyInfo = classmethod(getPropertyInfo)
	
