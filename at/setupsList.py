import wx
from wx.grid import Grid
from at.setup import Setup
from typing import List


class SetupsList(Grid):

    def __init__(self, parent, owner):
        Grid.__init__(self, parent, style=wx.BORDER_RAISED)

        self._owner = owner
        self._setups = []

        self.CreateGrid(0, 1)

        self.SetRowLabelSize(0)  # Hide the index column
        self.SetColLabelSize(0)  # Hide the column names
        self.EnableGridLines(False)  # Hide grid lines
        self.DisableDragGridSize()  # Disable resizing of rows/columns by dragging
        self.DisableDragColMove() # Disable reordering of columns by dragging
        self.SetCellHighlightPenWidth(0)  # Disable the highlight around the "current" cell
        self.SetSelectionMode(wx.grid.Grid.SelectRows)  # Select the entire row

        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self._onCellSelected)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self._onCellChanging)
        self.Bind(wx.EVT_SIZE, self._onResized)


    def _onResized(self, event):
        self.SetColSize(0, event.Size.width - self.GetWindowBorderSize().x)
        event.Skip()


    def showSetups(self, setups: List[Setup]):
        self._setups = setups

        rowCount = self.GetNumberRows()
        if rowCount > 0:
            self.DeleteRows(0, rowCount)

        setupCount = len(setups)
        self.AppendRows(setupCount, False)
        for i,setup in enumerate(setups):
            self._updateSetupRow(i, setup)
        self._insertAddSetupRow(setupCount)


    def _updateSetupRow(self, row, setup: Setup):
        self.SetCellValue(row, 0, setup.name)


    def _insertAddSetupRow(self, row):
        self.AppendRows()
        self.SetCellValue(row, 0, "<New Setup>")


    def _onCellSelected(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        col = event.GetCol()
        self.SelectBlock(row, col, row, col)
        if row < len(self._setups):
            self._owner.onSetupSelected(row)
        else:
            self._owner.onNoSetupSelected()


    def _onCellChanging(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        if row < len(self._setups):
            self._onRenameSetup(event)
        else:
            self._onAddSetup(event)

    def _onRenameSetup(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        setup = self._setups[event.GetRow()]
        setup.name = event.GetString()
        self._updateSetupRow(row)


    def _onAddSetup(self, event: wx.grid.GridEvent):
        setup = Setup(name = event.GetString())
        self._setups.append(setup)
        row =  event.GetRow()
        self._updateSetupRow(row, setup)
        self._insertAddSetupRow(row + 1)
        self._onCellSelected(event)