
from datetime import datetime
import time
from logbook import Logger
from service.fit import Fit as svcFit

from eos.saveddata.cargo import Cargo
from eos.saveddata.drone import Drone
from eos.saveddata.fighter import Fighter
from eos.saveddata.module import Module, State
from eos.saveddata.ship import Ship
from eos.saveddata.citadel import Citadel
from eos.saveddata.fit import Fit
from service.market import Market
from service.port.esi import INV_FLAG_CARGOBAY, INV_FLAG_FIGHTER, INV_FLAG_DRONEBAY
from service.port.shared import saveImportedFit


pyfalog = Logger(__name__)



def importZKillboard(killmail, fitNameFunction=lambda killmail, fit: fit.ship.item.name) -> Fit or None:
    """Parses a single killmail from the zkillboard API. The argument is an already parsed JSON"""
    sMkt = Market.getInstance()
    fit = Fit()
    victim = killmail["victim"]
    items = victim["items"]

    try:
        ship = victim["ship_type_id"]
        try:
            fit.ship = Ship(sMkt.getItem(ship))
        except ValueError:
            fit.ship = Citadel(sMkt.getItem(ship))
    except:
        pyfalog.warning("Caught exception in importZKillboard")
        return None

    fit.name = fitNameFunction(killmail, fit)

    items.sort(key=lambda k: k["flag"])

    moduleList = []
    moduleByFlag = {}
    chargeByFlag = {}
    for module in items:
        try:
            item = sMkt.getItem(module["item_type_id"], eager="group.category")
            if not item.published:
                continue
            flag = module["flag"]
            if flag == INV_FLAG_DRONEBAY:
                d = Drone(item)
                d.amount = module.get("quantity_destroyed", 0) + module.get("quantity_dropped", 0)
                fit.drones.append(d)
            elif flag == INV_FLAG_CARGOBAY:
                c = fit.cargo.findFirst(item)
                if c is None:
                    c = Cargo(item)
                    fit.cargo.append(c)
                c.amount += module.get("quantity_destroyed", 0) + module.get("quantity_dropped", 0)

            elif flag == INV_FLAG_FIGHTER:
                fighter = Fighter(item)
                fit.fighters.append(fighter)
            else:
                try:
                    m = Module(item)
                    moduleByFlag[flag] = m
                # When item can't be added to any slot (unknown item or just charge), ignore it
                except ValueError:
                    chargeByFlag[flag] = item
                    pyfalog.debug("Item can't be added to any slot (unknown item or just charge)")
                    continue
                # Add subsystems before modules to make sure T3 cruisers have subsystems installed
                if item.category.name == "Subsystem":
                    if m.fits(fit):
                        fit.modules.append(m)
                else:
                    if m.isValidState(State.ACTIVE):
                        m.state = State.ACTIVE

                    moduleList.append(m)

        except:
            pyfalog.warning("Could not process module.")
            continue

    # Recalc to get slot numbers correct for T3 cruisers
    svcFit.getInstance().recalc(fit)

    for flag in moduleByFlag.keys():
        module = moduleByFlag[flag]
        charge = chargeByFlag.get(flag, None)
        if (not charge is None) and module.isValidCharge(charge) and module.charge is None:
            module.charge = charge

    for module in moduleList:
        if module.fits(fit):
            fit.modules.append(module)

    km_time = datetime.strptime(killmail["killmail_time"], "%Y-%m-%dT%H:%M:%SZ")
    fit.timestamp = time.mktime(km_time.timetuple())
    fit.modified = fit.created = km_time

    return saveImportedFit(fit)
