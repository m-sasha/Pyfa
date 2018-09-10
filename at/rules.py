import eos.gamedata


def isShipGroupAllowed(group: eos.gamedata.Group):
    # noinspection PyUnresolvedReferences
    return group.category.name == "Ship" and group.name in {
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


disallowedShips = {
    "Nestor", "Marshal", "Enforcer", "Pacifier", "Monitor"
}

exceptionalShipPointValues = [
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

pointValuesByMarketGroupName = {
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


# noinspection PyUnresolvedReferences
def shipPointValue(ship: eos.gamedata.Item):
    shipName = ship.name

    if shipName in disallowedShips:
        return None

    for names,value in exceptionalShipPointValues:
        if shipName in names:
            return value

    marketGroup = ship.marketGroup
    marketGroups = []
    while not (marketGroup is None):
        marketGroups.append(marketGroup)
        marketGroup = marketGroup.parent

    value = pointValuesByMarketGroupName
    for marketGroup in reversed(marketGroups):
        value = value.get(marketGroup.name, None)
        if (value is None) or isinstance(value, int):
            return value


def isShipAllowed(ship: eos.gamedata.Item):
    # noinspection PyUnresolvedReferences
    return (ship.category.name == "Ship") and (not shipPointValue(ship) is None)
