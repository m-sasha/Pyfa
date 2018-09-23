import eos.gamedata
from eos.db.gamedata.queries import getGroup


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


_allowedShipGroupNames = {
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
    'Command Destroyer',
    'Marauder'
}


def isShipGroupAllowed(group: eos.gamedata.Group):
    # 'Limited Issue Ships' is a fake group which isn't present in the database, so we don't want to put it in the
    # allowed groups set, because we also query the database with these names to retrieve the groups themselves
    return (group.name in _allowedShipGroupNames) or (group.name == "Limited Issue Ships")



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


_disallowedModuleMarketGroups = {
    "Target Breaker",
    "Micro Jump Field Generators",
    "Cloaking Devices",
    "Interdiction Sphere Launchers",
    "Clone Vat Bays",
    "Cynosural Field Generators",
    "Jump Portal Generators",
    "Scriptable Armor Hardeners",
    "Scriptable Shield Hardeners",
    "Superweapons",
    "Burst Projectors",
    "Projected ECCM",
    "Siege Modules", # Includes Bastion
    "25000mm Armor Plate",
    "XL Launchers",
    "Rapid Torpedo Launchers",

    # Useless
    "Jump Economizers",
    "Warp Accelerators",
    "Harvest Equipment",
    "Warp Disruptors",
    "Analyzers",
    "Entosis Links",
    "Scan Probe Launchers",
    "Scanning Upgrades",
    "Survey Probe Launchers",
    "Survey Scanners",
    "Scanning Rigs",
    "Resource Processing Rigs",
    "Warp Core Stabilizers"
}


# Some items don't have a market group, or any other attribute except for their name, by which we can tell them apart
# from allowed (or useful) modules
_disallowedModuleNamePrefixes = {
    "Mining Foreman Link"
}


def _isUnderMarketGroup(group: eos.gamedata.MarketGroup, groupName):
    while group is not None:
        if group.name == groupName:
            return True
        group = group.parent
    return False



def _isInMarketGroup(item: eos.gamedata.Item, groupName):
    return _isUnderMarketGroup(item.marketGroup, groupName)


def _isInAnyMarketGroup(item: eos.gamedata.Item, groupNames):
    return any(_isInMarketGroup(item, marketGroup) for marketGroup in groupNames)


_disallowedModuleMetaGroupNames = {
    'Faction',
    'Deadspace',
    'Officer',
    'Storyline',
}


def _isAllowedModuleMeta(metaGroup: eos.gamedata.MetaGroup):
    return (metaGroup is None) or (metaGroup.name not in _disallowedModuleMetaGroupNames)


_allowedAnyMetaOnFlagshipModuleGroups = {
    'Energy Weapon',
    'Hybrid Weapon',
    'Precursor Weapon',
    'Projectile Weapon',
    'Missile Launcher Cruise',
    'Missile Launcher Heavy Assault',
    'Missile Launcher Heavy',
    'Missile Launcher Light',
    'Missile Launcher Rapid Heavy',
    'Missile Launcher Rapid Light',
    'Missile Launcher Rocket',
    'Missile Launcher Torpedo',

    'Smart Bomb',
    'Propulsion Module',

    'Warp Scrambler',
    'Stasis Grappler',
    'Target Painter',
    'Sensor Booster',
    'Signal Amplifier',
    'Overdrive Injector System',
    'Nanofiber Internal Structure',
    'Inertial Stabilizer',

    'Ballistic Control system',
    'Entropic Radiation Sink',
    'Gyrostabilizer',
    'Heat Sink',
    'Magnetic Field Stabilizer',
    'Missile Guidance Computer',
    'Missile Guidance Enhancer',
    'Remote Tracking Computer',
    'Tracking Computer',
    'Tracking Enhancer',
    'Drone Damage Modules',
    'Drone Navigation Computer',
    'Drone Tracking Modules',
    'Drone Tracking Enhancer',
    'Drone Control Range Module',

    'Armor Reinforcer',
    'Shield Extender',
    'Damage Control',

    'Shield Booster',
    'Armor Repair Unit',
}


def _isAnyMetaModuleAllowedOnFlagship(module: eos.gamedata.Item):
    marketGroupName = module.marketGroup.name
    # Non-BS weapons are allowed, but hardly useful on a Flagship
    if _isInAnyMarketGroup(module, {"Energy Turrets", "Hybrid Turrets", "Precursor Turrets", "Projectile Turrets"}) and (marketGroupName != "Large"):
        return False
    elif _isInMarketGroup(module, "Missile Launchers") and marketGroupName not in {"Cruise Launchers", "Rapid Heavy Missile Launchers", "Torpedo Launchers}"}:
        return False

    # Non-BS prop modules are allowed, but hardly useful on a Flagship
    elif (module.group.name == 'Propulsion Module') and (module.attributes["massAddition"].value < 10000000.0):
        return False

    return module.group.name in _allowedAnyMetaOnFlagshipModuleGroups


def isTech2(item: eos.gamedata.Item):
    metaGroup = item.metaGroup
    return (metaGroup is not None) and (metaGroup.name == "Tech II")


def isCapitalRig(rig: eos.gamedata.Item):
    return rig.attributes["rigSize"].value > 3


_allowedShipGroupsIds = {getGroup(shipGroupName).ID for shipGroupName in _allowedShipGroupNames}


# Copied from eos.saveddata.module
def isCapitalSizeModule(module: eos.gamedata.Item):
    volumeAttr = module.attributes.get("volume", None)
    return (volumeAttr is None) or (volumeAttr.value >= 4000)


def fitsOnLegalShips(module: eos.gamedata.Item):
    if isCapitalSizeModule(module):
        return False

    fitsOnGroupIds = set()
    for attr in list(module.attributes.keys()):
        if attr.startswith("canFitShipGroup"):
            shipGroupId = module.attributes[attr].value
            if shipGroupId is not None:
                fitsOnGroupIds.add(shipGroupId)

    return (len(fitsOnGroupIds) == 0) or not fitsOnGroupIds.isdisjoint(_allowedShipGroupsIds)



def isModuleAllowed(module: eos.gamedata.Item):
    if (module.marketGroup is not None) and (module.marketGroup.name in _disallowedModuleMarketGroups):
        return False
    elif not (_isAllowedModuleMeta(module.metaGroup) or _isAnyMetaModuleAllowedOnFlagship(module)):
        return False
    elif _isInMarketGroup(module, "Rigs") and (isTech2(module) or isCapitalRig(module)):
        return False
    elif any(module.name.startswith(prefix) for prefix in _disallowedModuleNamePrefixes):
        return False
    elif not fitsOnLegalShips(module):
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
    return _isInAnyMarketGroup(charge, _ammoMarketGroupNames)


# Unfortunately, there is no item property that we can use to tell pirate ammo apart from regular faction ammo
_disallowedAmmoNamePrefixes = {
    "Arch Angel",
    "Domination",
    "Sanshas",
    "True Sanshas",
    "Blood",
    "Dark Blood",
    "Shadow",
    "Guardian",
    "Guristas",
    "Dread Guristas"
}


def _isCapitalOrStructureAmmo(ammo: eos.gamedata.Item):
    if "chargeSize" in ammo.attributes:
        return ammo.attributes["chargeSize"].value > 3
    else:
        return False


def isAmmoAllowed(ammo: eos.gamedata.Item):
    if _isCapitalOrStructureAmmo(ammo):
        return False
    elif any(ammo.name.startswith(prefix) for prefix in _disallowedAmmoNamePrefixes):
        return False
    return True


_disallowedChargeMarketGroups = {
    "Mining Crystals",
    "Probes",
    "Structure Guided Bombs",
    "Orbital Strike",
    "Structure Anticapital Missiles",
    "Structure Antisubcapital Missiles",
    "XL Cruise Missiles",
    "XL Torpedoes",
    "Mining Foreman Burst Charges", # Useless

    # These are allowed and not entirely useless, but who would ever choose them over navy ammo?
    "Standard Crystals",
    "Standard Charges", # Hybrid
    "Standard Ammo", # Projectile
    "Standard Cruise Missiles",
    "Standard Heavy Assault Missiles",
    "Standard Heavy Missiles",
    "Standard Light Missiles",
    "Standard Rockets",
    "Standard Torpedoes",
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
    elif marketGroup.name == "Cap Booster Charges":
        return charge.metaGroup is not None # This filters out t1 cap boosters, because who would ever use them over navy?

    return True


_disallowedDroneMarketGroups = {
    "Mining Drones",
    "Salvage Drones",
    "Fighters"
}

def isDroneAllowed(drone: eos.gamedata.Item):
    metaGroup = drone.metaGroup
    if metaGroup is not None:
        return False
    elif _isInAnyMarketGroup(drone, _disallowedDroneMarketGroups):
        return False
    return True


_disallowedImplantMarketGroups = {
    "Attribute Enhancers",
    "Booster",
    "Cerebral Accelerators",
    "Industry Implants",
    "Resource Processing Implants",
    "Scanning Implants",
    "Science Implants",
    "Neural Enhancement Implants",
    "Faction Omega Implants"
}


def isImplantAllowed(implant: eos.gamedata.Item):
    if _isInAnyMarketGroup(implant, _disallowedImplantMarketGroups):
        return False
    elif implant.group.name == "Booster":  # Cerebral accelerators don't have a market group for some reason
        return False
    elif implant.group.name == "Cyber Leadership":
        return True
    else:
        return implant.name[-1] in {"1", "2", "3"}


_disallowedItemCategories = {
    "Structure",
    "Structure Module",
    "Fighter",
    "Deployable",

}


def isItemAllowed(item: eos.gamedata.Item):
    categoryName = item.category.name
    if categoryName in _disallowedItemCategories:
        return False
    elif categoryName == "Ship":
        return isShipAllowed(item)
    elif categoryName == "Module":
        return isModuleAllowed(item)
    elif categoryName == "Charge":
        return isChargeAllowed(item)
    elif categoryName == "Drone":
        return isDroneAllowed(item)
    elif categoryName == "Implant":
        return isImplantAllowed(item)
    return True


def isGroupAllowed(group: eos.gamedata.Group):
    categoryName = group.category.name
    if categoryName == "Ship":
        return isShipGroupAllowed(group)
    return False


_disallowedToplevelMarketGroups = {
    "Deployable Structures",
    "Structure Equipment",
    "Structure Modifications",
}

_disallowedMarketGroups = set().union(
    _disallowedImplantMarketGroups,
    _disallowedDroneMarketGroups,
    _disallowedChargeMarketGroups,
    _disallowedModuleMarketGroups,
    _disallowedToplevelMarketGroups,
)

def isMarketGroupAllowed(group: eos.gamedata.MarketGroup):
    if group.name in _disallowedMarketGroups:
        return False
    elif group.name == "Capital":
        return False
    elif (group.name == "Extra Large") and _isUnderMarketGroup(group, "Ammunition & Charges"):
        return False
    elif (group.name == "Extra Large") and _isUnderMarketGroup(group, "Turrets & Bays"):
        return False
    elif (group.name.startswith("Capital")) and _isUnderMarketGroup(group, "Rigs"):
        return False
    return True
