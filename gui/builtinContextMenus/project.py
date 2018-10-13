import gui.fitCommands as cmd
import gui.mainFrame
from gui.contextMenu import ContextMenu
# noinspection PyPackageRequirements
from service.fit import Fit
from service.settings import ContextMenuSettings


class Project(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()
        self.settings = ContextMenuSettings.getInstance()

    def display(self, srcContext, selection):
        if not self.settings.get('project'):
            return False

        if srcContext not in ("marketItemGroup", "marketItemMisc") or self.mainFrame.getActiveFit() is None:
            return False

        sFit = Fit.getInstance()
        fitID = self.mainFrame.getActiveFit()
        fit = sFit.getFit(fitID)

        if fit.isStructure:
            return False

        item = selection[0]
        return item.isType("projected")

    def getText(self, itmContext, selection):
        return "Project {0} onto Fit".format(itmContext)

    def activate(self, fullContext, selection, i):
        fitID = self.mainFrame.getActiveFit()
        self.mainFrame.command.Submit(cmd.GuiAddProjectedCommand(fitID, selection[0].ID, 'item'))

        # trigger = sFit.project(fitID, selection[0])
        # if trigger:
        #     wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
        #     self.mainFrame.additionsPane.select("Projected")


Project.register()
