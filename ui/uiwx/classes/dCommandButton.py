import wx
from dControlMixin import dControlMixin

class dCommandButton(wx.Button, dControlMixin):
    def __init__(self, parent, name="dCommandButton", label=""):
        wx.Button.__init__(self, parent, -1, label)
        self.SetName(name)
        self.SetSize((80,-1))
        dControlMixin.__init__(self, name)
        
    def initEvents(self):
        # init the common events:
        dControlMixin.initEvents(self)
        
        # init the widget's specialized event(s):
        wx.EVT_BUTTON(self, self.GetId(), self.onEvent)
        
    # Event callback methods (override in subclasses):
    def OnButton(self, event): pass

              
               
if __name__ == "__main__":
    import test
    class c(dCommandButton):
        def OnButton(self, event): print "Button!"

    test.Test().runTest(c)
