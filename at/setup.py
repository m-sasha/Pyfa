from typing import List
from service.settings import SettingsProvider


class SetupShip(object):


    def __init__(self, shipId, fitId=None, active=True) -> None:
        super().__init__()
        self.shipId = shipId
        self.fitId = fitId
        self.active = active


    def toggleActive(self):
        self.active = not self.active


class Setup(object):

    def __init__(self, name: str):
        super().__init__()
        self.name : str = name
        self.ships : List[SetupShip] = []


class StoredSetups:

    _settings = SettingsProvider.getInstance().getSettings("pyfaSetups", {
        "setups": []
    })

    @staticmethod
    def loadSetups() -> List[Setup]:
        setups = StoredSetups._settings["setups"]
        return setups

    @staticmethod
    def addSetup(setup: Setup) -> None:
        setups = StoredSetups.loadSetups()
        setups.append(setup)
        StoredSetups._settings["setups"] = setups

