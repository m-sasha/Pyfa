# shipMissileHeavyAssaultVelocityABC2
#
# Used by:
# Ship: Damnation
type = "passive"


def handler(fit, ship, context):
    fit.modules.filteredChargeBoost(lambda mod: mod.charge.requiresSkill("Heavy Assault Missiles"),
                                    "maxVelocity", ship.getModifiedItemAttr("shipBonusABC2"),
                                    skill="Amarr Battlecruiser")
