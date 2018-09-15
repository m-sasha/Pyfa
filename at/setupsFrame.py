from logbook import Logger
import wx
import eos.db
from service.settings import SettingsProvider
from wx import ListBox
from at.setup import Setup, StoredSetups, SetupShip
import at.rules
from service.fit import Fit


pyfalog = Logger(__name__)

class SetupsFrame(wx.Frame):
    __instance = None

    @classmethod
    def getInstance(cls) -> 'SetupsFrame':
        return cls.__instance if cls.__instance is not None else SetupsFrame()

    def __init__(self, title="Setups"):
        pyfalog.debug("Initialize SetupsFrame")
        self.title = title
        wx.Frame.__init__(self, None, wx.ID_ANY, self.title)

        SetupsFrame.__instance = self

        self._frameAttribs = None
        self.LoadFrameAttribs()

        self.setups = StoredSetups.loadSetups()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Create the UI
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        setupsListBox = wx.ListBox(self, size = (200,-1), style = wx.LB_SINGLE)
        if self.setups:
            setupsListBox.InsertItems(list([setup.name for setup in self.setups]), 0)

        setupDisplay = wx.ListCtrl(self, style = wx.LC_REPORT | wx.LC_SINGLE_SEL)
        setupDisplay.InsertColumn(0, "Ship")
        setupDisplay.InsertColumn(1, "Fit")
        setupDisplay.InsertColumn(2, "Points", format=wx.LIST_FORMAT_RIGHT)

        mainSizer.Add(setupsListBox, 0, wx.EXPAND)
        mainSizer.Add(setupDisplay, 1, wx.EXPAND)

        self.SetSizer(mainSizer)

        self.setupsListBox = setupsListBox
        self.setupDisplay = setupDisplay

        self.Bind(wx.EVT_LISTBOX, self.onSetupSelected, setupsListBox)

        # from service.fit import Fit
        # sFit = Fit.getInstance()
        # absolution = sFit.searchFits("BSOD")[0]
        # drake = sFit.searchFits("Drake")[0]
        # setup = Setup("Mattarrush")
        # setup.ships.append(SetupShip(fitId=absolution[0], shipId=absolution[2]))
        # setup.ships.append(SetupShip(fitId=drake[0], shipId=drake[2]))
        # StoredSetups.addSetup(setup)


    def onSetupSelected(self, event):
        table = self.setupDisplay
        table.DeleteAllItems()
        if not event.IsSelection():
            return

        sFit = Fit.getInstance()
        index = event.GetSelection()
        setup = self.setups[index]
        for i,setupShip in enumerate(setup.ships):
            ship = eos.db.getItem(setupShip.shipId)
            fit = sFit.getFit(setupShip.fitId, basic=True)

            table.InsertStringItem(i, ship.name)
            table.SetStringItem(i, 1, fit.name)
            table.SetStringItem(i, 2, str(at.rules.shipPointValue(ship)))


    def LoadFrameAttribs(self):
        defaultAttribs = {"wnd_size": (1000, 700),
                          "wnd_position": None,
                          "wnd_maximized": False}
        self._frameAttribs = SettingsProvider.getInstance().getSettings("pyfaSetupsWindowAttribs", defaultAttribs)

        isMaximized = self._frameAttribs["wnd_maximized"]
        if isMaximized:
            size = defaultAttribs["wnd_size"]
        else:
            size = self._frameAttribs["wnd_size"]

        self.SetSize(size)

        pos = self._frameAttribs["wnd_position"]
        if pos is not None:
            self.SetPosition(pos)

        if isMaximized:
            self.Maximize()


    def UpdateFrameAttribs(self):
        if self.IsIconized():
            return

        self._frameAttribs["wnd_size"] = self.GetSize()
        self._frameAttribs["wnd_position"] = self.GetPosition()
        self._frameAttribs["wnd_maximized"] = self.IsMaximized()


    def OnClose(self, event):
        self.UpdateFrameAttribs()


    def OnAppExit(self):
        self.Close()

