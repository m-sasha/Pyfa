import wx
from at.setup import Setup
import eos.db
import at.rules
from service.fit import Fit


class SetupPanel(wx.ListCtrl):


    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)

        self.InsertColumn(0, "Ship")
        self.InsertColumn(1, "Fit")
        self.InsertColumn(2, "Points", format=wx.LIST_FORMAT_RIGHT)


    def showSetup(self, setup : Setup):
        self.DeleteAllItems()

        sFit = Fit.getInstance()
        for i,setupShip in enumerate(setup.ships):
            ship = eos.db.getItem(setupShip.shipId)
            fit = sFit.getFit(setupShip.fitId, basic=True)

            self.InsertStringItem(i, ship.name)
            self.SetStringItem(i, 1, fit.name)
            self.SetStringItem(i, 2, str(at.rules.shipPointValue(ship)))
