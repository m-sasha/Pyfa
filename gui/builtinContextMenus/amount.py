from gui.contextMenu import ContextMenu
from eos.saveddata.fit import Fit as es_Fit
import gui.mainFrame
import gui.globalEvents as GE
# noinspection PyPackageRequirements
import wx
import re
from service.fit import Fit
from eos.saveddata.drone import Drone
from eos.saveddata.cargo import Cargo as es_Cargo
from eos.saveddata.fighter import Fighter as es_Fighter
from service.settings import ContextMenuSettings
import gui.fitCommands as cmd


class ChangeAmount(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()
        self.settings = ContextMenuSettings.getInstance()

    def display(self, srcContext, selection):
        if not self.settings.get('amount'):
            return False

        return srcContext in ("droneItem", "projectedDrone", "cargoItem", "projectedFit", "fighterItem", "projectedFighter")

    def getText(self, itmContext, selection):
        return u"Change {0} Quantity".format(itmContext)

    def activate(self, fullContext, selection, i):
        thing = selection[0]
        mainFrame = gui.mainFrame.MainFrame.getInstance()
        fitID = mainFrame.getActiveFit()
        srcContext = fullContext[0]
        if isinstance(thing, es_Fit):
            value = thing.getProjectionInfo(fitID).amount
        else:
            value = thing.amount

        dlg = AmountChanger(self.mainFrame, value)
        if dlg.ShowModal() == wx.ID_OK:

            if dlg.input.GetLineText(0).strip() == '':
                return

            sFit = Fit.getInstance()
            fit = sFit.getFit(fitID)
            cleanInput = re.sub(r'[^0-9.]', '', dlg.input.GetLineText(0).strip())

            if isinstance(thing, es_Cargo):
                self.mainFrame.command.Submit(cmd.GuiChangeCargoQty(fitID, fit.cargo.index(thing), int(float(cleanInput))))
                return  # no need for post event here
            elif isinstance(thing, Drone):
                if srcContext == "droneItem":
                    self.mainFrame.command.Submit(cmd.GuiChangeDroneQty(fitID, fit.drones.index(thing), int(float(cleanInput))))
                else:
                    self.mainFrame.command.Submit(cmd.GuiChangeProjectedDroneQty(fitID, fit.projectedDrones.index(thing), int(float(cleanInput))))
            elif isinstance(thing, es_Fit):
                self.mainFrame.command.Submit(cmd.GuiChangeProjectedFitQty(fitID, thing.ID, int(float(cleanInput))))
                return
            elif isinstance(thing, es_Fighter):
                self.mainFrame.command.Submit(cmd.GuiChangeFighterQty(fitID, fit.fighters.index(thing), int(float(cleanInput))))
                return

            wx.PostEvent(mainFrame, GE.FitChanged(fitID=fitID))


ChangeAmount.register()


class AmountChanger(wx.Dialog):
    def __init__(self, parent, value):
        wx.Dialog.__init__(self, parent, title="Change Amount")
        self.SetMinSize((346, 156))

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(self, wx.ID_ANY, "New Amount:")
        bSizer2.Add(text, 0)

        bSizer1.Add(bSizer2, 0, wx.ALL, 10)

        self.input = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.input.SetValue(str(value))
        self.input.SelectAll()

        bSizer1.Add(self.input, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 15)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)
        bSizer3.Add(wx.StaticLine(self, wx.ID_ANY), 0, wx.BOTTOM | wx.EXPAND, 15)

        bSizer3.Add(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND)
        bSizer1.Add(bSizer3, 0, wx.ALL | wx.EXPAND, 10)

        self.input.SetFocus()
        self.input.Bind(wx.EVT_CHAR, self.onChar)
        self.input.Bind(wx.EVT_TEXT_ENTER, self.processEnter)
        self.SetSizer(bSizer1)
        self.CenterOnParent()
        self.Fit()

    def processEnter(self, evt):
        self.EndModal(wx.ID_OK)

    # checks to make sure it's valid number
    @staticmethod
    def onChar(event):
        key = event.GetKeyCode()

        acceptable_characters = "1234567890"
        acceptable_keycode = [3, 22, 13, 8, 127]  # modifiers like delete, copy, paste
        if key in acceptable_keycode or key >= 255 or (key < 255 and chr(key) in acceptable_characters):
            event.Skip()
            return
        else:
            return False
