import wx
from wx.grid import Grid
from at.setup import Setup, SetupShip
import eos.db
import at.rules
from service.fit import Fit
from service.market import Market

_SHIP_COL = 0
_FIT_COL = 1
_POINTS_COL = 2

class SetupPanel(Grid):

    def __init__(self, parent):
        Grid.__init__(self, parent)

        self.CreateGrid(0, 3)

        self.SetRowLabelSize(0)  # Hide the index column
        self.EnableGridLines(False)  # Hide grid lines

        self.SetColLabelValue(0, "Ship")
        self.SetColLabelValue(1, "Fit")
        self.SetColLabelValue(2, "Points")

        self.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self.onCellChanging)

        self.setup : Setup = None

    def showSetup(self, setup : Setup):
        rowCount = self.GetNumberRows()
        if rowCount > 0:
            self.DeleteRows(0, rowCount)

        shipCount = len(setup.ships)
        self.AppendRows(shipCount)
        for i,setupShip in enumerate(setup.ships):
            self._updateShipRow(i, setupShip)
        self._insertAddShipRow(shipCount)

        self.setup = setup

    def _updateShipRow(self, row, setupShip: SetupShip):
        sFit = Fit.getInstance()
        ship = eos.db.getItem(setupShip.shipId)
        fitId = setupShip.fitId
        fit = sFit.getFit(setupShip.fitId, basic=True) if fitId is not None else None
        self.SetCellValue(row, _SHIP_COL , ship.name)
        self.SetCellValue(row, _FIT_COL, fit.name if fit is not None else "")
        self.SetCellValue(row, _POINTS_COL, str(at.rules.shipPointValue(ship)))

        self.SetReadOnly(row, _POINTS_COL)
        self.SetCellAlignment(row, _POINTS_COL, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)


    def _insertAddShipRow(self, row):
        self.AppendRows()
        self.SetCellValue(row, _SHIP_COL, "<Add Ship>")
        self.SetReadOnly(row, _FIT_COL)
        self.SetReadOnly(row, _POINTS_COL)


    def onCellChanging(self, event: wx.grid.GridEvent):
        col = event.GetCol()
        if col == _SHIP_COL:
            if event.GetRow() == len(self.setup.ships):  # <Add Ship>
                self._onAddShip(event)
            else:
                self._onShipChanging(event)
        elif col == _FIT_COL:
            self._onFitChanging(event)


    def _onAddShip(self, event: wx.grid.GridEvent):
        shipName = event.GetString()

        sMarket = Market.getInstance()
        newShip = sMarket.getShipByName(shipName)
        if newShip is None:
            event.Veto()
            return

        ship = SetupShip(newShip.typeID)
        self.setup.ships.append(ship)
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

        ship = self.setup.ships[event.GetRow()]
        ship.shipId = newShip.typeID
        ship.fitId = None
        self._updateShipRow(event.GetRow(), ship)


    def _onFitChanging(self, event):
        name = event.GetString()
        fit = Fit.getInstance().getFitByName(name)
        if fit is None:
            event.Veto()
            return

        fitId, shipId = fit[0], fit[2]
        ship = self.setup.ships[event.GetRow()]
        if ship.shipId != shipId:
            event.Veto()
            return

        ship.fitId = fitId
        self._updateShipRow(event.GetRow(), ship)
