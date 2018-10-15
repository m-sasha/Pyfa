import urllib3
import certifi
import json
import config

BASE_URL = "https://esi.evetech.net"

class Endpoints:
    CHARACTER = "/v4/characters/{character_id}/"
    CORP_HISTORY = "/v1/characters/{character_id}/corporationhistory/"
    CORPORATION = "/v4/corporations/{corporation_id}/"
    ALLIANCE = "/v3/alliances/{alliance_id}/"
    ALLIANCE_HISTORY = "/v2/corporations/{corporation_id}/alliancehistory/"
    KILLMAIL = "/v1/killmails/{killmail_id}/{killmail_hash}/"


http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
_cache = dict()

def _fetchAsJson(endpoint, **kwargs):
    endpoint = endpoint.format(**kwargs)
    url = BASE_URL + endpoint
    if url in _cache:
        return _cache[url]

    headers = {"Accept" : "text/html",
               "User-Agent": "PyfaAT v{}".format(config.version),
               "Accept-Encoding": "gzip"}
    response = http.request('GET', url, headers=headers)
    data = json.loads(response.data.decode('utf-8'))
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

def fetchKillmail(killmail_id, killmail_hash):
    return _fetchAsJson(Endpoints.KILLMAIL, killmail_id=killmail_id, killmail_hash=killmail_hash)
