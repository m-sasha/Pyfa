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

        self.HideRowLabels()  # Hide the index column
        self.HideColLabels()  # Hide the column names
        self.EnableGridLines(False)  # Hide grid lines
        self.DisableDragGridSize()  # Disable resizing of rows/columns by dragging
        self.DisableDragColMove() # Disable reordering of columns by dragging
        self.SetCellHighlightPenWidth(0)  # Disable the highlight around the "current" cell
        self.SetCellHighlightROPenWidth(0)  # Disable the highlight around the "current" read-only cell
        self.SetSelectionMode(wx.grid.Grid.SelectRows)  # Select the entire row

        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self._onCellSelected)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self._onCellChanging)
        self.Bind(wx.EVT_SIZE, self._onResized)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self._showContextMenu)


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


    def _isSetupRow(self, row):
        return row < len(self._setups)


    def _updateSetupRow(self, row, setup: Setup):
        self.SetCellValue(row, 0, setup.name)


    def _insertAddSetupRow(self, row):
        self.AppendRows()
        self.SetCellValue(row, 0, "<New Setup>")


    def _onCellSelected(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        col = event.GetCol()
        self.SelectBlock(row, col, row, col)
        if self._isSetupRow(row):
            self._owner.onSetupSelected(row)
        else:
            self._owner.onNoSetupSelected()


    def _onCellChanging(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        if self._isSetupRow(row):
            self._onRenameSetup(event)
        else:
            self._onAddSetup(event)


    def _onRenameSetup(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        setup = self._setups[event.GetRow()]
        setup.name = event.GetString()
        self._updateSetupRow(row, setup)


    def _onAddSetup(self, event: wx.grid.GridEvent):
        setup = Setup(name = event.GetString())
        self._setups.append(setup)
        row =  event.GetRow()
        self._updateSetupRow(row, setup)
        self._insertAddSetupRow(row + 1)
        self._onCellSelected(event)


    def _showContextMenu(self, event: wx.grid.GridEvent):
        row = event.GetRow()
        if not self._isSetupRow(row):
            return

        if not row in self.SelectedRows:
            self.SelectRow(row)

        if not hasattr(self, "removeSetupId"):
            self.removeSetupId = wx.NewId()

        menu = wx.Menu()

        removeSetupItem : wx.MenuItem = menu.Append(self.removeSetupId, "Remove Setup(s)")
        self.Bind(wx.EVT_MENU, lambda _ : self._onRemoveSetups(self.SelectedRows), removeSetupItem)

        self.PopupMenu(menu)
        menu.Destroy()


    def _onRemoveSetups(self, rows):
        confirmDialog = wx.MessageDialog(self, "Delete %d setup(s)?" % len(rows), "Delete Setup(s)", style=wx.YES|wx.NO)
        confirmDialog.SetYesNoLabels("Delete Setup(s)", "Cancel")
        if confirmDialog.ShowModal() != wx.ID_YES:
            return

        for row in reversed(rows):
            del self._setups[row]
        self.showSetups(self._setups)
        self.ClearSelection()