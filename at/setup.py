from typing import List
from service.settings import SettingsProvider


class SetupShip(object):

    def __init__(self, shipId, fitId=None) -> None:
        super().__init__()
        self.shipId = shipId
        self.fitId = fitId


class Setup(object):

    def __init__(self, name: str):
        super().__init__()
        self.name : str = name
        self.ships : List[SetupShip] = []


class StoredSetups:

    _settings = SettingsProvider.getInstance().getSettings("pyfaSetups", {})

    @staticmethod
    def loadSetups() -> List[Setup]:
        setups = StoredSetups._settings["setups"]
        return setups if not setups is None else []

    @staticmethod
    def addSetup(setup: Setup) -> None:
        setups = StoredSetups.loadSetups()
        setups.append(setup)
        StoredSetups._settings["setups"] = setups

