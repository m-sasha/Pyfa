from service.market import Market
from eos.saveddata.module import Module, Slot
from service.fit import Fit
import at.rules
from simanneal import Annealer
import random


HIGH_SLOT_MODULES = list()
MED_SLOT_MODULES = list()
LOW_SLOT_MODULES = list()
RIGS = list([list(), list(), list()])

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


class FitOptimizer(Annealer):

    def __init__(self, fit: Fit):
        super(FitOptimizer, self).__init__(fit)
