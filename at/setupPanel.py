import wx
from wx.grid import Grid
from wx import Panel
from at.setup import Setup, SetupShip
import eos.db
import at.rules
from service.fit import Fit
from service.market import Market
from gui.utils.numberFormatter import formatAmount
import gui.mainFrame
import gui.globalEvents as GE
from gui.builtinShipBrowser.events import FitSelected


_SHIP_COL = 0
_FIT_COL = 1
_POINTS_COL = 2
_EHP_COL = 3
_DPS_COL = 4
_TOTAL_COLS = 5

class SetupPanel(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent)

        grid = Grid(self)

        grid.CreateGrid(0, _TOTAL_COLS)

        grid.SetRowLabelSize(0)  # Hide the index column
        grid.EnableGridLines(False)  # Hide grid lines
        grid.DisableDragGridSize()  # Disable resizing of rows/columns by dragging
        grid.DisableDragColMove() # Disable reordering of columns by dragging
        grid.SetCellHighlightPenWidth(0)  # Disable the highlight around the "current" cell
        grid.SetSelectionMode(wx.grid.Grid.SelectRows)  # Select the entire row

        grid.SetColLabelValue(_SHIP_COL, "Ship")
        grid.SetColLabelValue(_FIT_COL, "Fit")
        grid.SetColLabelValue(_POINTS_COL, "Points")
        grid.SetColLabelValue(_EHP_COL, "EHP")
        grid.SetColLabelValue(_DPS_COL, "DPS")

        grid.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self._onCellChanging)
        grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self._showContextMenu)
        gui.mainFrame.MainFrame.getInstance().Bind(GE.FIT_CHANGED, self._onFitChanged)


        shipCountLabel = wx.StaticText(self)
        pointCountLabel = wx.StaticText(self)
        dpsLabel = wx.StaticText(self)
        ehpLabel = wx.StaticText(self)

        infoPanelSizer = wx.FlexGridSizer(2, 8, 0)
        infoPanelSizer.Add(wx.StaticText(self, label="Ships:"), flag=wx.ALIGN_RIGHT)
        infoPanelSizer.Add(shipCountLabel)
        infoPanelSizer.Add(wx.StaticText(self, label="Points:"), flag=wx.ALIGN_RIGHT)
        infoPanelSizer.Add(pointCountLabel)
        infoPanelSizer.Add(wx.StaticText(self, label="Total DPS:"), flag=wx.ALIGN_RIGHT)
        infoPanelSizer.Add(dpsLabel)
        infoPanelSizer.Add(wx.StaticText(self, label="Total EHP:"), flag=wx.ALIGN_RIGHT)
        infoPanelSizer.Add(ehpLabel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        sizer.Add(infoPanelSizer, 0, wx.EXPAND | wx.ALL, border=8)
        self.SetSizer(sizer)

        self.grid = grid
        self.shipCountLabel = shipCountLabel
        self.pointCountLabel = pointCountLabel
        self.dpsLabel = dpsLabel
        self.ehpLabel = ehpLabel
        self._setup : Setup = None

    def showSetup(self, setup : Setup or None):
        grid = self.grid
        rowCount = grid.GetNumberRows()
        if rowCount > 0:
            grid.DeleteRows(0, rowCount)

        self._setup = setup

        if setup is None:
            return

        shipCount = len(setup.ships)
        grid.AppendRows(shipCount)
        for i,setupShip in enumerate(setup.ships):
            self._updateShipRow(i, setupShip)
        self._insertAddShipRow(shipCount)


    def _updateShipRow(self, row, setupShip: SetupShip):
        grid = self.grid
        sFit = Fit.getInstance()
        ship = eos.db.getItem(setupShip.shipId)
        fitId = setupShip.fitId
        fit = sFit.getFit(setupShip.fitId, basic=False) if fitId is not None else None
        grid.SetCellValue(row, _SHIP_COL , ship.name)
        grid.SetCellValue(row, _POINTS_COL, str(at.rules.shipPointValue(ship)))
        if fit is not None:
            grid.SetCellValue(row, _FIT_COL, fit.name)
            grid.SetCellValue(row, _EHP_COL, formatAmount(fit.totalEHP, 3, 0, 9))
            grid.SetCellValue(row, _DPS_COL, formatAmount(fit.totalDPS, 3, 0, 0))

        grid.SetReadOnly(row, _POINTS_COL)
        grid.SetReadOnly(row, _EHP_COL)
        grid.SetReadOnly(row, _DPS_COL)

        grid.SetCellAlignment(row, _POINTS_COL, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        grid.SetCellAlignment(row, _EHP_COL, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        grid.SetCellAlignment(row, _DPS_COL, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)


    def _insertAddShipRow(self, row):
        grid = self.grid
        grid.AppendRows()
        grid.SetCellValue(row, _SHIP_COL, "<Add Ship>")
        grid.SetReadOnly(row, _FIT_COL)
        grid.SetReadOnly(row, _POINTS_COL)


    def _onCellChanging(self, event: wx.grid.GridEvent):
        col = event.GetCol()
        if col == _SHIP_COL:
            if event.GetRow() == len(self._setup.ships):  # <Add Ship>
                self._onAddShip(event)
            else:
                self._onShipChanging(event)
        elif col == _FIT_COL:
            self._onChoosingFit(event)


    def _onAddShip(self, event: wx.grid.GridEvent):
        shipName = event.GetString()

        sMarket = Market.getInstance()
        newShip = sMarket.getShipByName(shipName)
        if newShip is None:
            event.Veto()
            return

        ship = SetupShip(newShip.typeID)
        self._setup.ships.append(ship)
        self._updateShipRow(event.GetRow(), ship)
        self._insertAddShipRow(event.GetRow()+1)

        pass


    def _onShipChanging(self, event: wx.grid.GridEvent):
        shipName = event.GetString()

        sMarket = Market.getInstance()
        newShip = sMarket.getShipByName(shipName)
        if newShip is None:
            event.Veto()
            return

        ship = self._setup.ships[event.GetRow()]
        ship.shipId = newShip.typeID
        ship.fitId = None
        self._updateShipRow(event.GetRow(), ship)


    def _onChoosingFit(self, event: wx.grid.GridEvent):
        name = event.GetString()
        fit = Fit.getInstance().getFitByName(name)
        if fit is None:
            event.Veto()
            return

        fitId, shipId = fit[0], fit[2]
        ship = self._setup.ships[event.GetRow()]
        if ship.shipId != shipId:
            event.Veto()
            return

        ship.fitId = fitId
        self._updateShipRow(event.GetRow(), ship)


    def _rowOfFit(self, fitId):
        for i,ship in enumerate(self._setup.ships):
            if fitId == ship.fitId:
                return i
        return None


    def _onFitChanged(self, event):
        row = self._rowOfFit(event.fitID)
        if row is None:
            return

        self._updateShipRow(row, self._setup.ships[row])
        event.Skip()


    def _showContextMenu(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        if row >= len(self._setup.ships):
            return

        self.grid.SelectRow(row)
        fitId = self._setup.ships[row].fitId

        if not hasattr(self, "openFitId"):
            self.openFitId = wx.NewId()
            self.openFitInNewTabId = wx.NewId()
            self.deleteFitId = wx.NewId()

        menu = wx.Menu()

        openFitItem : wx.MenuItem = menu.Append(self.openFitId, "Open Fit")
        self.Bind(wx.EVT_MENU, lambda _ : self._onOpenFit(fitId, False), openFitItem)

        openFitInNewTabItem: wx.MenuItem = menu.Append(self.openFitInNewTabId, "Open Fit In New Tab")
        self.Bind(wx.EVT_MENU, lambda _: self._onOpenFit(fitId, True), openFitInNewTabItem)

        removeFromSetupItem : wx.MenuItem = menu.Append(self.deleteFitId, "Remove From Setup")
        self.Bind(wx.EVT_MENU, lambda _ : self._onRemoveFitFromSetup(fitId), removeFromSetupItem)

        self.PopupMenu(menu)
        menu.Destroy()


    @staticmethod
    def _onOpenFit(fitId, inNewTab):
        mainFrame = gui.mainFrame.MainFrame.getInstance()
        if not fitId is None:
            if inNewTab:
                wx.PostEvent(mainFrame, FitSelected(fitID=fitId, startup=2))
            else:
                wx.PostEvent(mainFrame, FitSelected(fitID=fitId))


    def _onRemoveFitFromSetup(self, event):
        pass
