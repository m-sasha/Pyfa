import eos.gamedata


def isGroupAllowed(group: eos.gamedata.Group):
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
