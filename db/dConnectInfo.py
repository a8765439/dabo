import dabo.common

class dConnectInfo(dabo.common.dObject):
	""" Holder for the properties for connecting to the backend.

	Each backend may have different names for properties, but this object
	tries to abstract that.

		ci = ConnectInfo('MySQL')
		ci.host = 'domain.com'
		ci.user = 'dabo'
		ci.password = 'dabo'
	"""
	def __init__(self, backendName=None, host=None, user=None, 
					password=None, dbName=None, port=None):
		self._baseClass = dConnectInfo
		dConnectInfo.doDefault(self)
		self.BackendName = backendName
		self.Host = host
		self.User = user
		self.Password = password
		self.DbName = dbName
		self.Port = port
		
		
	def getConnection(self):
		return self.BackendObject.getConnection(self)

	def getDictCursor(self):
		try:
			return self.BackendObject.getDictCursor()
		except TypeError:
			return None

	def _getBackendName(self): 
		try:
			return self._backendName
		except AttributeError:
			return None

			
	def _setBackendName(self, backendName):
		""" Set the backend type for the connection if valid. 
		"""
		
		# As other backends are coded into the framework, we will need 
		# to expand the if/elif list.
		
		if backendName is not None:
			# Evaluate each type of backend
			nm = backendName.lower()
			self._backendName = nm
			if nm == "mysql":
				import dbMySQL
				self._backendObject = dbMySQL.MySQL()
			elif nm == "gadfly":
				import dbGadfly
				self._backendObject = dbGadfly.Gadfly()
			elif nm == "sqlite":
				import dbSqlite
				self._backendObject = dbSqlite.Sqlite()
			elif nm == "firebird":
				import dbFirebird
				self._backendObject = dbFirebird.Firebird()
			else:
				self._backendName = None
				self._backendObject = None
		else:
			self._backendName = None
			self._backendObject = None

			
	def _getBackendObject(self):
		return self._backendObject

	def _getHost(self): 
		return self._host

	def _setHost(self, host): 
		self._host = host

	def _getUser(self): 
		return self._user

	def _setUser(self, user): 
		self._user = user

	def _getPassword(self): 
		return self._password

	def _setPassword(self, password): 
		self._password = password

	def _getDbName(self): 
		return self._dbName

	def _setDbName(self, dbName): 
		self._dbName = dbName

	def _getPort(self): 
		return self._port

	def _setPort(self, port): 
		self._port = port

	BackendName = property(_getBackendName, _setBackendName)
	Host = property(_getHost, _setHost, None, 
			'The host name or ip address. (str)')
	User = property(_getUser, _setUser, None,
			'The user name. (str)')
	Password = property(_getPassword, _setPassword, None,
			'The password of the user. (str)')
	DbName = property(_getDbName, _setDbName, None,
			'The database name to login to. (str)')
	BackendObject = property(_getBackendObject, None, None,
			'The object reference to the database api. (obj)')
	Port = property(_getPort, _setPort, None, 
			'The port to connect on (may not be applicable for all databases). (int)')

if __name__ == '__main__':
	test = dConnectInfo()
	print test.backendName
	test.backendName = "MySQL"
	print test.backendName
# 	test.backendName = "mssql"
# 	print test.backendName

