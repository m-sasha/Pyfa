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
_ACTIVE_COL = 5
_TOTAL_COLS = 6

class SetupPanel(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent)

        grid = Grid(self)

        grid.CreateGrid(0, _TOTAL_COLS)

        grid.HideRowLabels() # Hide the index column
        grid.EnableGridLines(False)  # Hide grid lines
        grid.DisableDragGridSize()  # Disable resizing of rows/columns by dragging
        grid.DisableDragColMove() # Disable reordering of columns by dragging
        grid.SetCellHighlightPenWidth(0)  # Disable the highlight around the "current" cell
        grid.SetCellHighlightROPenWidth(0)  # Disable the highlight around the "current" read-only cell
        grid.SetSelectionMode(wx.grid.Grid.SelectRows)  # Select the entire row

        grid.SetColLabelValue(_SHIP_COL, "Ship")
        grid.SetColLabelValue(_FIT_COL, "Fit")
        grid.SetColLabelValue(_POINTS_COL, "Points")
        grid.SetColLabelValue(_EHP_COL, "EHP")
        grid.SetColLabelValue(_DPS_COL, "DPS")
        grid.SetColLabelValue(_ACTIVE_COL, "Active?")

        grid.SetColFormatBool(_ACTIVE_COL)

        grid.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self._onCellChanging)
        grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self._showContextMenu)
        grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self._onCellLeftClick)
        gui.mainFrame.MainFrame.getInstance().Bind(GE.FIT_CHANGED, self._onFitChanged)


        shipCountLabel = wx.StaticText(self)
        pointCountLabel = wx.StaticText(self)
        dpsLabel = wx.StaticText(self)
        ehpLabel = wx.StaticText(self)

        infoPanelSizer = wx.FlexGridSizer(2, 0, 16)
        infoPanelSizer.Add(wx.StaticText(self, label="Ships"), flag=wx.ALIGN_CENTER)
        infoPanelSizer.Add(wx.StaticText(self, label="Points"), flag=wx.ALIGN_CENTER)
        infoPanelSizer.Add(shipCountLabel, flag=wx.ALIGN_CENTER)
        infoPanelSizer.Add(pointCountLabel, flag=wx.ALIGN_CENTER)
        infoPanelSizer.AddSpacer(12)
        infoPanelSizer.AddSpacer(12)
        infoPanelSizer.Add(wx.StaticText(self, label="Total DPS"), flag=wx.ALIGN_CENTER)
        infoPanelSizer.Add(wx.StaticText(self, label="Total EHP"), flag=wx.ALIGN_CENTER)
        infoPanelSizer.Add(dpsLabel, flag=wx.ALIGN_CENTER)
        infoPanelSizer.Add(ehpLabel, flag=wx.ALIGN_CENTER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        sizer.Add(infoPanelSizer, 0, wx.EXPAND | wx.ALL, border=8)
        self.SetSizer(sizer)

        self._grid = grid
        self.shipCountLabel = shipCountLabel
        self.pointCountLabel = pointCountLabel
        self.dpsLabel = dpsLabel
        self.ehpLabel = ehpLabel
        self._setup : Setup = None


    def showSetup(self, setup : Setup or None):
        grid = self._grid
        rowCount = grid.GetNumberRows()
        if rowCount > 0:
            grid.DeleteRows(0, rowCount)

        self._setup = setup

        if setup is None:
            return

        shipCount = len(setup.ships)
        grid.AppendRows(shipCount)
        for i,setupShip in enumerate(setup.ships):
            self._updateShipRow(i, updateShipInfo=False)
        self._insertAddShipRow()

        self._updateSetupInfo()


    @property
    def _shipCount(self):
        return len(self._setup.ships) if self._setup else 0


    def _isShipRow(self, row):
        return 0 <= row < self._shipCount


    def _getShip(self, row):
        return self._setup.ships[row] if self._setup is not None else None


    @property
    def _addShipRowIndex(self):
        return self._shipCount


    @property
    def _totalsRowIndex(self):
        return self._shipCount + 1


    def _rowOfFit(self, fitId):
        if self._setup is None:
            return None

        for i,ship in enumerate(self._setup.ships):
            if fitId == ship.fitId:
                return i
        return None


    def _updateShipRow(self, row, updateShipInfo=True):
        setupShip = self._getShip(row)
        grid = self._grid
        sFit = Fit.getInstance()
        ship = eos.db.getItem(setupShip.shipId)
        fitId = setupShip.fitId
        fit = sFit.getFit(setupShip.fitId, basic=False) if fitId is not None else None

        grid.SetCellSize(row, _SHIP_COL, 1, 1)  # Fix what may have been set by _insertAddShipRow
        grid.SetCellValue(row, _SHIP_COL , ship.name)
        grid.SetCellValue(row, _POINTS_COL, str(at.rules.shipPointValue(ship)))
        if fit is not None:
            grid.SetCellValue(row, _FIT_COL, fit.name)
            grid.SetCellValue(row, _EHP_COL, formatAmount(fit.totalEHP, 3, 0, 9))
            grid.SetCellValue(row, _DPS_COL, formatAmount(fit.totalDPS, 3, 0, 0))
        grid.SetCellValue(row, _ACTIVE_COL, "1" if setupShip.active else "0")

        grid.SetReadOnly(row, _POINTS_COL)
        grid.SetReadOnly(row, _EHP_COL)
        grid.SetReadOnly(row, _DPS_COL)
        grid.SetReadOnly(row, _ACTIVE_COL)

        grid.SetCellAlignment(row, _POINTS_COL, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        grid.SetCellAlignment(row, _EHP_COL, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        grid.SetCellAlignment(row, _DPS_COL, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        grid.SetCellAlignment(row, _ACTIVE_COL, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        if updateShipInfo:
            self._updateSetupInfo()


    def _insertAddShipRow(self):
        row = self._addShipRowIndex
        grid = self._grid
        grid.AppendRows()
        grid.SetCellValue(row, _SHIP_COL, "<Add Ship>")
        grid.SetCellSize(row, _SHIP_COL, 1, _TOTAL_COLS)


    def _updateSetupInfo(self):
        sFit = Fit.getInstance()
        activeShips = [ship for ship in self._setup.ships if ship.active]
        activeFits = [sFit.getFit(ship.fitId, basic=False) for ship in activeShips]
        self.shipCountLabel.SetLabelText(str(len(activeShips)))
        self.pointCountLabel.SetLabelText(str(sum([at.rules.shipPointValue(eos.db.getItem(ship.shipId)) for ship in activeShips])))
        self.ehpLabel.SetLabelText(formatAmount(sum([fit.totalEHP if fit else 0 for fit in activeFits]), 3, 0, 9))
        self.dpsLabel.SetLabelText(formatAmount(sum([fit.totalDPS if fit else 0 for fit in activeFits]), 3, 0, 0))


    def _onCellChanging(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        col = event.GetCol()
        if col == _SHIP_COL:
            if row == self._addShipRowIndex:  # <Add Ship>
                self._onAddShip(event)
            elif self._isShipRow(row):
                self._onShipChanging(event)
        elif col == _FIT_COL:
            self._onChoosingFit(event)
        elif col == _ACTIVE_COL:
            self._getShip(row).toggleActive()
            self._updateShipRow(row)


    def _onAddShip(self, event: wx.grid.GridEvent):
        shipName = event.GetString()

        sMarket = Market.getInstance()
        newShip = sMarket.getShipByName(shipName)
        if newShip is None:
            event.Veto()
            return

        ship = SetupShip(newShip.typeID)
        self._setup.ships.append(ship)
        self._updateShipRow(event.GetRow())
        self._insertAddShipRow()

        pass


    def _onShipChanging(self, event: wx.grid.GridEvent):
        shipName = event.GetString()

        sMarket = Market.getInstance()
        newShip = sMarket.getShipByName(shipName)
        if newShip is None:
            event.Veto()
            return

        row = event.GetRow()
        ship = self._getShip(row)
        ship.shipId = newShip.typeID
        ship.fitId = None
        self._updateShipRow(row)


    def _onChoosingFit(self, event: wx.grid.GridEvent):
        name = event.GetString()
        fit = Fit.getInstance().getFitByName(name)
        if fit is None:
            event.Veto()
            return

        fitId, shipId = fit[0], fit[2]
        ship = self._getShip(event.GetRow())
        if ship.shipId != shipId:
            event.Veto()
            return

        ship.fitId = fitId
        self._updateShipRow(event.GetRow())


    def _onFitChanged(self, event):
        row = self._rowOfFit(event.fitID)
        if row is None:
            return

        self._updateShipRow(row)
        event.Skip()


    def _showContextMenu(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        if not self._isShipRow(row):
            return

        self._grid.SelectRow(row)
        fitId = self._getShip(row).fitId

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


    def _onCellLeftClick(self, event: wx.grid.GridEvent):
        if self._setup is None:
            return

        row = event.GetRow()
        col = event.GetCol()
        if col == _ACTIVE_COL and self._isShipRow(row):
            self._getShip(row).toggleActive()
            self._updateShipRow(row)
        event.Skip()


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
