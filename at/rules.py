import eos.gamedata


# Point values
PIRATE_FACTION_BS = 23
MARAUDER = 22
NAVY_FACTION_BS = 21
BLACK_OPS = 20
BATTLESHIP = 19
COMMAND_SHIP = 18
PRAXIS = 17
LOGISTICS_CRUISER = 17
STRATEGIC_CRUISER = 15
NAVY_FACTION_BC = 15
COMBAT_BC = 13
HIC = 13
T1_SUPPORT_CRUISER = 11
ATTACK_BC = 11
GNOSIS = 11
RECON = 11
HAC = 11
PIRATE_FACTION_CRUISER = 10
NAVY_FACTION_CRUISER = 8
COMMAND_DESTROYER = 6
T1_DISRUPTION_CRUISER = 6
TACTICAL_DESTROYER = 5
EAF = 5
ASSAULT_FRIGATE = 5
CRUISER = 4
PIRATE_FACTION_FRIGATE = 4
COVERT_OPS = 4
INTERDICTOR = 4
LOGISTICS_FRIGATE = 3
NAVY_FACTION_FRIGATE = 3
T1_DISRUPTION_FRIGATE = 3
STEALTH_BOMBER = 3
INTERCEPTOR = 3
DESTROYER = 3
T1_INDUSTRIAL = 2
FRIGATE = 2
PIRATE_FACTION_ROOKIE = 2
T1_SUPPORT_FRIGATE = 1
SUNESIS = 1
ROOKIE_SHIP = 1


_allowedShipGroups = {
    'Combat Recon Ship',
    'Frigate',
    'Cruiser',
    'Battleship',
    'Industrial',
    'Command Ship',
    'Interdictor',
    'Tactical Destroyer',
    'Combat Battlecruiser',
    'Destroyer',
    'Attack Battlecruiser',
    'Covert Ops',
    'Interceptor',
    'Logistics',
    'Force Recon Ship',
    'Stealth Bomber',
    'Strategic Cruiser',
    'Assault Frigate',
    'Black Ops',
    'Heavy Assault Cruiser',
    'Logistics Frigate',
    'Electronic Attack Ship',
    'Heavy Interdiction Cruiser',
    'Limited Issue Ships',
    'Command Destroyer',
    'Marauder'
}


def isShipGroupAllowed(group: eos.gamedata.Group):
    return group.name in _allowedShipGroups


_disallowedShips = {
    "Nestor", "Marshal", "Enforcer", "Pacifier", "Monitor"
}


_exceptionalShipPointValues = [
    ({"Bantam", "Burst", "Inquisitor", "Navitas"},  T1_SUPPORT_FRIGATE),
    ({"Griffin", "Vigil", "Crucifier", "Maulus"}, T1_DISRUPTION_FRIGATE),
    ({"Scythe", "Augoror", "Osprey", "Exequror"}, T1_SUPPORT_CRUISER),
    ({"Bellicose", "Arbitrator", "Blackbird", "Celestis"}, T1_DISRUPTION_CRUISER),
    ({"Oracle", "Naga", "Talos", "Tornado"}, ATTACK_BC),
    ({"Praxis"}, PRAXIS),
    ({"Gnosis"}, GNOSIS),
    ({"Sunesis"}, SUNESIS),
    ({"Immolator", "Echo", "Hematos", "Taipan", "Violator"}, PIRATE_FACTION_ROOKIE)

]


_pointValuesByMarketGroupName = {
    "Ships": {
        "Frigates": {
            "Standard Frigates": FRIGATE,
            "Precursor Frigates": FRIGATE,
            "Faction Frigates": {
                "Pirate Faction": PIRATE_FACTION_FRIGATE,
                "Navy Faction": NAVY_FACTION_FRIGATE,
            },
            "Advanced Frigates": {
                "Interceptors": INTERCEPTOR,
                "Covert Ops": COVERT_OPS,
                "Assault Frigates": ASSAULT_FRIGATE,
                "Electronic Attack Frigates": EAF,
                "Logistics Frigates": LOGISTICS_FRIGATE,
            },
        },
        "Cruisers": {
            "Standard Cruisers": CRUISER,
            "Precursor Cruisers": CRUISER,
            "Advanced Cruisers": {
                "Logistics": LOGISTICS_CRUISER,
                "Heavy Assault Cruisers": HAC,
                "Recon Ships": RECON,
                "Heavy Interdiction Cruisers": HIC,
                "Strategic Cruisers": STRATEGIC_CRUISER,
            },
            "Faction Cruisers": {
                "Navy Faction": NAVY_FACTION_CRUISER,
                "Pirate Faction": PIRATE_FACTION_CRUISER,

            }
        },
        "Destroyers": {
            "Standard Destroyers": DESTROYER,
            "Advanced Destroyers": {
                "Interdictors": INTERDICTOR,
                "Tactical Destroyers": TACTICAL_DESTROYER,
                "Command Destroyers": COMMAND_DESTROYER,
            }
        },
        "Battlecruisers": {
            "Standard Battlecruisers": COMBAT_BC,
            "Advanced Battlecruisers": {
                "Command Ships": COMMAND_SHIP
            },
            "Faction Battlecruisers": {
                "Navy Faction": NAVY_FACTION_BC
            }
        },
        "Battleships": {
            "Standard Battleships": BATTLESHIP,
            "Precursor Battleships": BATTLESHIP,
            "Advanced Battleships": {
                "Black Ops": BLACK_OPS,
                "Marauders": MARAUDER,
                "Faction Battleships": {
                    "Navy Faction": NAVY_FACTION_BS,
                    "Pirate Faction": PIRATE_FACTION_BS
                }
            }
        },
        "Industrial Ships": {
            "Standard Industrial Ships": T1_INDUSTRIAL
        },
        "Corvettes" : ROOKIE_SHIP,
        "Special Edition Ships": {
            "Special Edition Heavy Assault Cruisers": HAC,
            "Special Edition Assault Frigates": ASSAULT_FRIGATE,
            "Special Edition Logistics": LOGISTICS_CRUISER,
            "Special Edition Recon Ships": RECON,
            "Special Edition Covert Ops": COVERT_OPS,
            "Special Edition Interceptors": INTERCEPTOR,
            "Special Edition Heavy Interdiction Cruisers": HIC,
        }
    }
}


def shipPointValue(ship: eos.gamedata.Item):
    shipName = ship.name

    if shipName in _disallowedShips:
        return None

    for names,value in _exceptionalShipPointValues:
        if shipName in names:
            return value

    # List all the market groups of the ship, from most specific to least specific
    marketGroup = ship.marketGroup
    marketGroups = []
    while not (marketGroup is None):
        marketGroups.append(marketGroup)
        marketGroup = marketGroup.parent

    # Walk the ships market groups, from least specific, to most specific, until _pointValuesByMarketGroupName defines
    # a specific point value for it, or we find nothing
    value = _pointValuesByMarketGroupName
    for marketGroup in reversed(marketGroups):
        value = value.get(marketGroup.name, None)
        if (value is None) or isinstance(value, int):
            return value


def isShipAllowed(ship: eos.gamedata.Item):
    return shipPointValue(ship) is not None


_disallowedModules = {
    "Micro Jump Field Generator",
    "Bastion Module I",
    "Target Spectrum Breaker",
}


_disallowedModuleGroups = {
    "Cloaking Device"
}


def _isInMarketGroup(item: eos.gamedata.Item, groupName):
    itemGroup = item.marketGroup
    while itemGroup is not None:
        if itemGroup.name == groupName:
            return True
        itemGroup = itemGroup.parent
    return False


def _isInAnyMarketGroup(item: eos.gamedata.Item, groupNames):
    return any(_isInMarketGroup(item, marketGroup) for marketGroup in groupNames)


def isTech2(item: eos.gamedata.Item):
    metaGroup = item.metaGroup
    return (metaGroup is not None) and (metaGroup.name == "Tech II")


def isCapitalRig(rig: eos.gamedata.Item):
    return rig.attributes["rigSize"].value > 3


def isModuleAllowed(module: eos.gamedata.Item):
    if module.name in _disallowedModules:
        return False
    elif module.group.groupName in _disallowedModuleGroups:
        return False
    elif _isInMarketGroup(module, "Rigs") and (isTech2(module) or isCapitalRig(module)):
        return False
    return True


_disallowedScriptGroups = {
    'Tracking Disruption Script',
    'Sensor Dampener Script',
    'Guidance Disruption Script',
    'Structure ECM script',
    'Flex Armor Hardener Script',
    'Flex Shield Hardener Script',
    'Structure Warp Disruptor Script',
}


def isScriptAllowed(script: eos.gamedata.Item):
    return script.group.name not in _disallowedScriptGroups


_ammoMarketGroupNames = {
    'Hybrid Charges',
    'Projectile Ammo',
    'Frequency Crystals',
    'Missiles',
    'Exotic Plasma Charges',
}


def _isAmmo(charge: eos.gamedata.Item):
    return any(_isInMarketGroup(charge, marketGroup) for marketGroup in _ammoMarketGroupNames)


# Unfortunately, there is no item property that we can use to tell pirate ammo apart from regular faction ammo
_disallowedAmmoSubstrings = {
    "Arch Angel",
    "Domination",
    "Sanshas",
    "Blood",
    "Shadow",
    "Guardian",
    "Guristas"
}


# For some reason missiles don't have a "chargeSize" attribute, like turret ammo does
_capitalOrStructureMissileMarketGroups = {
    "Structure Antisubcapital Missiles",
    "Structure Anticapital Missiles",
    "XL Cruise Missiles",
    "XL Torpedoes"
}


def _isCapitalOrStructureAmmo(ammo: eos.gamedata.Item):
    if _isInAnyMarketGroup(ammo, _capitalOrStructureMissileMarketGroups):
        return True
    elif "chargeSize" in ammo.attributes:
        return ammo.attributes["chargeSize"].value > 3
    else:
        return False


def isAmmoAllowed(ammo: eos.gamedata.Item):
    if _isCapitalOrStructureAmmo(ammo):
        return False
    elif any(substring in ammo.name for substring in _disallowedAmmoSubstrings):
        return False
    return True


_disallowedChargeMarketGroups = {
    "Mining Crystals",
    "Probes",
    "Structure Guided Bombs"
}

def isChargeAllowed(charge: eos.gamedata.Item):
    marketGroup = charge.marketGroup
    if marketGroup is None:  # WTF? The "Civilian Scourge Light Missile" has no market group (and no other types of civilian missiles)
        return False
    elif _isInAnyMarketGroup(charge, _disallowedChargeMarketGroups):
        return False
    elif marketGroup.name == "Scripts":
        return isScriptAllowed(charge)
    elif _isAmmo(charge):
        return isAmmoAllowed(charge)
    return True


_disallowedDroneMarketGroups = {
    "Mining Drones",
    "Salvage Drones"
}

def isDroneAllowed(drone: eos.gamedata.Item):
    metaGroup = drone.metaGroup
    if metaGroup is not None:
        return False
    elif _isInAnyMarketGroup(drone, _disallowedDroneMarketGroups):
        return False
    return True


_disallowedItemCategories = {
    "Structure",
    "Fighter",
}


def isItemAllowed(item: eos.gamedata.Item):
    categoryName = item.category.name
    if categoryName in _disallowedItemCategories:
        return False
    if categoryName == "Ship":
        return isShipAllowed(item)
    elif categoryName == "Module":
        return isModuleAllowed(item)
    elif categoryName == "Charge":
        return isChargeAllowed(item)
    elif categoryName == "Drone":
        return isDroneAllowed(item)
    return True


def isGroupAllowed(group: eos.gamedata.Group):
    categoryName = group.category.name
    if categoryName == "Ship":
        return isShipGroupAllowed(group)
    return False
