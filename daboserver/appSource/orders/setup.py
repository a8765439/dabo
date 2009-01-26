#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob
from distutils.core import setup
import py2exe
import dabo.icons
from App import App


daboDir = os.path.split(dabo.__file__)[0]


# Find the location of the dabo icons:
iconDir = os.path.split(dabo.icons.__file__)[0]
iconSubDirs = []
def getIconSubDir(arg, dirname, fnames):
	if ".svn" not in dirname and dirname[-1] != "\\":
		icons = glob.glob(os.path.join(dirname, "*.png"))
		if icons:
			subdir = (os.path.join("resources", dirname[len(arg)+1:]), icons)
			iconSubDirs.append(subdir)
os.path.walk(iconDir, getIconSubDir, iconDir)

# locales:
localeDir = "%s%slocale" % (daboDir, os.sep)
#locales = [("dabo.locale", (os.path.join(daboDir, "locale", "dabo.pot"),))]
locales = []
def getLocales(arg, dirname, fnames):
  if ".svn" not in dirname and dirname[-1] != "\\":
    #po_files = tuple(glob.glob(os.path.join(dirname, "*.po")))
    mo_files = tuple(glob.glob(os.path.join(dirname, "*.mo")))
    if mo_files:
      subdir = os.path.join("dabo.locale", dirname[len(arg)+1:])
      locales.append((subdir, mo_files))
os.path.walk(localeDir, getLocales, localeDir)

# The applications App object contains all the meta info:
app = App(MainFormClass=None)
app.setup()

_appName = app.getAppInfo("appName")
_appVersion = app.getAppInfo("appVersion")
_appDescription = app.getAppInfo("appDescription")
_copyright = app.getAppInfo("copyright")
_authorName = app.getAppInfo("authorName") 
_authorEmail = app.getAppInfo("authorEmail")
_authorURL = app.getAppInfo("authorURL")
_authorPhone = app.getAppInfo("authorPhone")


_appComments = ("This is custom software by %s.\r\n"
		"\r\n"
		"%s\r\n" 
		"%s\r\n" 
		"%s\r\n") % (_authorName, _authorEmail, _authorURL, _authorPhone)

# Set your app icon here:
_appIcon = None
#_appIcon = "./resources/stock_addressbook.ico"

_script = "orders.py"


class Target:
	def __init__(self, **kw):
		self.__dict__.update(kw)
		# for the versioninfo resources
		self.version = _appVersion
		self.company_name = _authorName
		self.copyright = _copyright
		self.name = _appName
		self.description = _appDescription
		self.comments = _appComments

		self.script=_script
		self.other_resources=[]
		if _appIcon is not None:
			self.icon_resources=[(1, _appIcon)]


data_files=[(".", ("orders.exe.manifest",)),
		("db", ["db/default.cnxml"]),
		("resources", glob.glob(os.path.join(iconDir, "*.ico"))),
		("resources", glob.glob("resources/*")),
		("reports", glob.glob("reports/*"))]
data_files.extend(iconSubDirs)
data_files.extend(locales)

if sys.platform == "win32":
	import py2exe
	setup(name=_appName,
			version=_appVersion,
			description=_appDescription,
			author=_authorName,
			author_email=_authorEmail,
			url=_authorURL,
			options={"py2exe": {"packages": ["wx.gizmos", "wx.lib.calendar"],
					"optimize": 2,
					"excludes": ["Tkconstants","Tkinter","tcl", 
					"_imagingtk", "PIL._imagingtk",
					"ImageTk", "PIL.ImageTk", "FixTk"]}},
			packages=["ui", "biz", "db"],
			zipfile=None,
			windows=[Target()],
			data_files=data_files
	)

elif sys.platform == "darwin":
	import py2app
	setup(options={"py2app": {iconfile: _appIcon, packages: ['wx', 'wx.gizmos', 'wx.lib.calendar'],
			site_packages: True, resources: [],
			plist: dict(
					CFBundleName               = "MyAppName",
					CFBundleShortVersionString = "0.2.5",     # must be in X.X.X format
					CFBundleGetInfoString      = "MyAppName 0.2.5",
					CFBundleExecutable         = "MyAppName",
					CFBundleIdentifier         = "com.example.myappname",
			),
		},
	app: [_script]}
	)
