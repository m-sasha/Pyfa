from service.market import Market
from eos.saveddata.module import Module, Slot, State
from eos.saveddata.fit import Fit
import service.fit
import at.rules
from simanneal import Annealer
import random
import copy


HIGH_SLOT_MODULES = list()
MED_SLOT_MODULES = list()
LOW_SLOT_MODULES = list()
RIGS = list((list(), list(), list()))

def init():
    market = Market.getInstance()
    modulesMarketGroup = market.getCategory("Module")
    for group in market.getGroupsByCategory(modulesMarketGroup):
        for item in group.items:
            if not at.rules.isModuleAllowed(item):
                continue
            try:
                module = Module(item)
            except ValueError:
                continue
            slot = module.slot
            if slot == Slot.HIGH:
                HIGH_SLOT_MODULES.append(module)
            elif slot == Slot.MED:
                MED_SLOT_MODULES.append(module)
            elif slot == Slot.LOW:
                LOW_SLOT_MODULES.append(module)
            elif slot == Slot.RIG:
                rigSize = int(item.attributes["rigSize"].value-1)
                RIGS[rigSize].append(module)

init()


class FitOptimizer(Annealer):

    def __init__(self, fit: Fit):
        super(FitOptimizer, self).__init__(fit)
        self.sFit = service.fit.Fit.getInstance()

    def changeModuleNoCommit(self, fit: Fit, position, module: Module):
        module.owner = fit
        fit.modules.toModule(position, module)
        if module.isValidState(State.ACTIVE):
            module.state = State.ACTIVE
        self.sFit.recalc(fit)
        self.sFit.checkStates(fit, module)

    def move(self):
        fit = self.state
        while True:
            position = random.randint(0, len(fit.modules) - 1)
            currentModule = fit.modules[position]
            slot = currentModule.slot
            if slot == Slot.HIGH:
                modules = HIGH_SLOT_MODULES
            elif slot == Slot.MED:
                modules = MED_SLOT_MODULES
            elif slot == Slot.LOW:
                modules = LOW_SLOT_MODULES
            elif slot == Slot.RIG:
                rigSize = int(currentModule.item.attributes["rigSize"].value)-1
                modules = RIGS[rigSize]
            else:
                continue

            newModule = copy.deepcopy(modules[random.randint(0, len(modules)-1)])
            self.changeModuleNoCommit(fit, position, newModule)
            break

    def energy(self):
        fit = self.state

        pass










