import urllib.request
import json
import config

BASE_URL = "https://esi.evetech.net"

class Endpoints:
    CHARACTER = "/v4/characters/{character_id}/"
    CORP_HISTORY = "/v1/characters/{character_id}/corporationhistory/"
    CORPORATION = "/v4/corporations/{corporation_id}/"
    ALLIANCE = "/v3/alliances/{alliance_id}/"
    ALLIANCE_HISTORY = "/v2/corporations/{corporation_id}/alliancehistory/"


_cache = dict()

def _fetchAsJson(endpoint, **kwargs):
    endpoint = endpoint.format(**kwargs)
    url = BASE_URL + endpoint
    if url in _cache:
        return _cache[url]

    headers = {"Accept" : "text/html",
               "User-Agent": "PyfaAT v{}".format(config.version)}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read())
        _cache[url] = data
        return data

def fetchCharacterInfo(characterId):
    return _fetchAsJson(Endpoints.CHARACTER, character_id=characterId)


def fetchCorpHistory(characterId):
    return _fetchAsJson(Endpoints.CORP_HISTORY, character_id=characterId)


def fetchCorpInfo(corpId):
    return _fetchAsJson(Endpoints.CORPORATION, corporation_id=corpId)


def fetchAllianceInfo(allianceId):
    return _fetchAsJson(Endpoints.ALLIANCE, alliance_id=allianceId)


def fetchAllianceHistory(corpId):
    return _fetchAsJson(Endpoints.ALLIANCE_HISTORY, corporation_id=corpId)