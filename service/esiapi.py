import urllib.request
import json
import config

BASE_URL = "https://esi.evetech.net"

class Endpoints:
    CHARACTER = "/v4/characters/{character_id}/"
    ALLIANCE = "/v3/alliances/{alliance_id}/"

def _fetchAsJson(endpoint, **kwargs):
    endpoint = endpoint.format(**kwargs)
    url = BASE_URL + endpoint
    headers = {"Accept" : "text/html",
               "User-Agent": "PyfaAT v{}".format(config.version)}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())

def fetchCharacterInfo(characterId):
    return _fetchAsJson(Endpoints.CHARACTER, character_id=characterId)


def fetchAllianceInfo(allianceId):
    return _fetchAsJson(Endpoints.ALLIANCE, alliance_id=allianceId)