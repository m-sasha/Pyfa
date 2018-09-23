from logbook import Logger
import wx
from service.settings import SettingsProvider
from at.setup import StoredSetups
from at.setupPanel import SetupPanel
from at.setupsList import SetupsList



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
        mainSplitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        setupsList = SetupsList(mainSplitter, self)
        setupPanel = SetupPanel(mainSplitter)

        mainSplitter.SplitVertically(setupsList, setupPanel)
        mainSplitter.SetSashPosition(150)

        mainSizer = wx.BoxSizer()
        mainSizer.Add(mainSplitter, 1, wx.EXPAND)
        self.SetSizer(mainSizer)

        self.setupsList = setupsList
        self.setupPanel = setupPanel

        setupsList.showSetups(self.setups)

        # from service.fit import Fit
        # sFit = Fit.getInstance()
        # absolution = sFit.searchFits("BSOD")[0]
        # drake = sFit.searchFits("Drake")[0]
        # setup = Setup("Mattarrush")
        # setup.ships.append(SetupShip(fitId=absolution[0], shipId=absolution[2]))
        # setup.ships.append(SetupShip(fitId=drake[0], shipId=drake[2]))
        # StoredSetups.addSetup(setup)


    def onSetupSelected(self, index):
        setup = self.setups[index]
        self.setupPanel.showSetup(setup)


    def onNoSetupSelected(self):
        self.setupPanel.showSetup(None)


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

