# -*- coding: utf-8 -*-
import datetime
import dabo
dabo.ui.loadUI("wx")
import dabo.dEvents as dEvents
from dabo.dLocalize import _


class TestPanel(dabo.ui.dPanel):
	def afterInit(self):
		sz = self.Sizer = dabo.ui.dSizer("v")
		sz.appendSpacer(25)
		
		hb = dabo.ui.dHtmlBox(self)
		sz.append(hb, 2, "x", border=10)
		sz.appendSpacer(10)
		
		lbl = dabo.ui.dLabel(self, FontBold=True, FontItalic=True, ForeColor="blue", WordWrap=True, 
				Caption="Edit the HTML below, and then press 'TAB' to have the HTML updated in the dHtmlBox above.")
		sz.append(lbl, halign="center")
		sz.appendSpacer(2)
		
		eb = dabo.ui.dEditBox(self)
		sz.append1x(eb, border=10, borderSides=["left", "right"])
		sz.appendSpacer(5)
		
		eb.DataSource = hb
		eb.DataField = "Source"
		eb.Value = """<html>
<body bgcolor="#ACAA60">
<center>
	<table bgcolor="#AACCFF" width="100%%" cellspacing="0" cellpadding="0" 
			border="1">
		<tr>
			<td align="center"><h1>dHtmlBox</h1></td>
		</tr>
	</table>
</center>
<p><b><font size="160%%" color="#FFFFFF">dHtmlBox</font></b> is a Dabo UI widget that is designed to display html text. 
Be careful, though, because the widget doesn't support advanced functions like 
Javascript parsing.</p>
<p>It's better to think of it as a way to display <b>rich text</b> using 
<font size="+1" color="#993300">HTML markup</font>, rather
than a web browser replacement.</p>

<p>&nbsp;</p>
<div align="center"><img src="daboIcon.ico"></div>

<p align="center"><b><a href="http://dabodev.com">Dabo</a></b> is brought to you by <b>Ed Leafe</b>, <b>Paul McNett</b>,
and others in the open source community. Copyright &copy; 2004-%s
</p>
</body>
</html>
""" % datetime.date.today().year


category = "Controls.dHtmlBox"

overview = """
<b>dHtmlBox</b> creates a scrolled panel that can load and display html pages

The Html Window can load any html text, file, or url that is fed to it. It is somewhat limited in the complexity of HTML that it can render; it doesn't understand CSS or JavaScript. It's best to think of this not as a web browser, but as a way to display rich text that happens to be formatted with HTML markup.
"""
