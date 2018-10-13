#!/usr/bin/env python
#======================================================================
# Copyright (C) 2012 Diego Duclos
#
# This file is part of eos.
#
# eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with eos.  If not, see <http://www.gnu.org/licenses/>.
#======================================================================

import functools
import os
import sys

# Add eos root path to sys.path so we can import ourselves
path = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(os.path.join(path, '..')))

import json
import argparse

CATEGORIES_TO_REMOVE = [
    30  # Apparel
]

def main(db, json_path):
    if os.path.isfile(db):
        os.remove(db)

    jsonPath = os.path.expanduser(json_path)

    # Import eos.config first and change it
    import eos.config
    eos.config.gamedata_connectionstring = db
    eos.config.debug = False

    # Now thats done, we can import the eos modules using the config
    import eos.db
    import eos.gamedata

    # Create the database tables
    eos.db.gamedata_meta.create_all()

    # Config dict
    tables = {
        'clonegrades': eos.gamedata.AlphaCloneSkill,
        'dgmattribs': eos.gamedata.AttributeInfo,
        'dgmeffects': eos.gamedata.Effect,
        'dgmtypeattribs': eos.gamedata.Attribute,
        'dgmtypeeffects': eos.gamedata.ItemEffect,
        'dgmunits': eos.gamedata.Unit,
        'evecategories': eos.gamedata.Category,
        'evegroups': eos.gamedata.Group,
        'invmetagroups': eos.gamedata.MetaGroup,
        'invmetatypes': eos.gamedata.MetaType,
        'evetypes': eos.gamedata.Item,
        'phbtraits': eos.gamedata.Traits,
        'phbmetadata': eos.gamedata.MetaData,
        'mapbulk_marketGroups': eos.gamedata.MarketGroup,
    }

    fieldMapping = {
        'dgmattribs': {
            'displayName': 'displayName'
        },
        'dgmeffects': {
            'displayName': 'displayName',
            'description': 'description'
        },
        'dgmunits': {
            'displayName': 'displayName'
        },
        #icons???
        'evecategories': {
            'categoryName': 'categoryName'
        },
        'evegroups': {
            'groupName': 'groupName'
        },
        'invmetagroups': {
            'metaGroupName': 'metaGroupName'
        },
        'evetypes': {
            'typeName': 'typeName',
            'description': 'description'
        },
        #phbtraits???
        'mapbulk_marketGroups': {
            'marketGroupName': 'marketGroupName',
            'description': 'description'
        }

    }

    rowsInValues = (
        'evetypes',
        'evegroups',
        'evecategories'
    )

    def convertIcons(data):
        new = []
        for k, v in list(data.items()):
            v['iconID'] = k
            new.append(v)
        return new

    def convertClones(data):
        newData = []

        # December, 2017 - CCP decided to use only one set of skill levels for alpha clones. However, this is still
        # represented in the data as a skillset per race. To ensure that all skills are the same, we store them in a way
        # that we can check to make sure all races have the same skills, as well as skill levels

        check = {}

        for ID in data:
            for skill in data[ID]['skills']:
                newData.append({
                    'alphaCloneID': int(ID),
                    'alphaCloneName': 'Alpha Clone',
                    'typeID': skill['typeID'],
                    'level': skill['level']})
                if ID not in check:
                    check[ID] = {}
                check[ID][int(skill['typeID'])] = int(skill['level'])

        if not functools.reduce(lambda a, b: a if a == b else False, [v for _, v in check.items()]):
            raise Exception('Alpha Clones not all equal')

        newData = [x for x in newData if x['alphaCloneID'] == 1]

        if len(newData) == 0:
            raise Exception('Alpha Clone processing failed')

        return newData

    def convertTraits(data):

        def convertSection(sectionData):
            sectionLines = []
            headerText = '<b>{}</b>'.format(sectionData['header'])
            sectionLines.append(headerText)
            for bonusData in sectionData['bonuses']:
                prefix = '{} '.format(bonusData['number']) if 'number' in bonusData else ''
                bonusText = '{}{}'.format(prefix, bonusData['text'].replace('\u00B7', '\u2022 '))
                sectionLines.append(bonusText)
            sectionLine = '<br />\n'.join(sectionLines)
            return sectionLine

        newData = []
        for row in data:
            typeLines = []
            typeId = row['typeID']
            traitData = row['traits']
            for skillData in sorted(traitData.get('skills', ()), key=lambda i: i['header']):
                typeLines.append(convertSection(skillData))
            if 'role' in traitData:
                typeLines.append(convertSection(traitData['role']))
            if 'misc' in traitData:
                typeLines.append(convertSection(traitData['misc']))
            traitLine = '<br />\n<br />\n'.join(typeLines)
            newRow = {'typeID': typeId, 'traitText': traitLine}
            newData.append(newRow)
        return newData

    data = {}

    # Dump all data to memory so we can easely cross check ignored rows
    for jsonName, cls in tables.items():
        with open(os.path.join(jsonPath, '{}.json'.format(jsonName)), encoding='utf-8') as f:
            tableData = json.load(f)
        if jsonName in rowsInValues:
            tableData = list(tableData.values())
        if jsonName == 'icons':
            tableData = convertIcons(tableData)
        if jsonName == 'phbtraits':
            tableData = convertTraits(tableData)
        if jsonName == 'clonegrades':
            tableData = convertClones(tableData)
        data[jsonName] = tableData

    # Set with typeIDs which we will have in our database
    # Sometimes CCP unpublishes some items we want to have published, we
    # can do it here - just add them to initial set
    eveTypes = set()
    for row in data['evetypes']:
        if (row['published']
            or row['groupID'] == 1306  # group Ship Modifiers, for items like tactical t3 ship modes
            or row['typeName'].startswith('Civilian') # Civilian weapons
            or row['typeID'] in (41549, 41548, 41551, 41550)  # Micro Bombs (Fighters)
            or row['groupID'] in (
                        1882,
                        1975,
                        1971,
                        1983  # the "container" for the abyssal environments
                )  # Abyssal weather (environment)
        ):
            eveTypes.add(row['typeID'])

    # ignore checker
    def isIgnored(file, row):
        if file in ('evetypes', 'dgmtypeeffects', 'dgmtypeattribs', 'invmetatypes') and row['typeID'] not in eveTypes:
            return True
        return False

    # Loop through each json file and write it away, checking ignored rows
    for jsonName, table in data.items():
        fieldMap = fieldMapping.get(jsonName, {})
        tmp = []

        print('processing {}'.format(jsonName))

        for row in table:
            # We don't care about some kind of rows, filter it out if so
            if not isIgnored(jsonName, row):
                if jsonName == 'evetypes' and row['typeName'].startswith('Civilian'):  # Apparently people really want Civilian modules available
                    row['published'] = True

                instance = tables[jsonName]()
                # fix for issue 80
                if jsonName is 'icons' and 'res:/ui/texture/icons/' in str(row['iconFile']).lower():
                    row['iconFile'] = row['iconFile'].lower().replace('res:/ui/texture/icons/', '').replace('.png', '')
                    # with res:/ui... references, it points to the actual icon file (including it's size variation of #_size_#)
                    # strip this info out and get the identifying info
                    split = row['iconFile'].split('_')
                    if len(split) == 3:
                        row['iconFile'] = '{}_{}'.format(split[0], split[2])
                if jsonName is 'icons' and 'modules/' in str(row['iconFile']).lower():
                    row['iconFile'] = row['iconFile'].lower().replace('modules/', '').replace('.png', '')

                if jsonName is 'clonegrades':
                    if row['alphaCloneID'] not in tmp:
                        cloneParent = eos.gamedata.AlphaClone()
                        setattr(cloneParent, 'alphaCloneID', row['alphaCloneID'])
                        setattr(cloneParent, 'alphaCloneName', row['alphaCloneName'])
                        eos.db.gamedata_session.add(cloneParent)
                        tmp.append(row['alphaCloneID'])

                for k, v in row.items():
                    if isinstance(v, str):
                        v = v.strip()
                    setattr(instance, fieldMap.get(k, k), v)

                eos.db.gamedata_session.add(instance)

    # quick and dirty hack to get this data in
    with open(os.path.join(jsonPath, 'dynamicAttributes.json'), encoding='utf-8') as f:
        bulkdata = json.load(f)
        for mutaID, data in bulkdata.items():
            muta = eos.gamedata.DynamicItem()
            muta.typeID = mutaID
            muta.resultingTypeID = data['inputOutputMapping'][0]['resultingType']
            eos.db.gamedata_session.add(muta)

            for x in data['inputOutputMapping'][0]['applicableTypes']:
                item = eos.gamedata.DynamicItemItem()
                item.typeID = mutaID
                item.applicableTypeID = x
                eos.db.gamedata_session.add(item)

            for attrID, attrData in data['attributeIDs'].items():
                attr = eos.gamedata.DynamicItemAttribute()
                attr.typeID = mutaID
                attr.attributeID = attrID
                attr.min = attrData['min']
                attr.max = attrData['max']
                eos.db.gamedata_session.add(attr)

    eos.db.gamedata_session.commit()

    # CCP still has 5 subsystems assigned to T3Cs, even though only 4 are available / usable. They probably have some
    # old legacy requirement or assumption that makes it difficult for them to change this value in the data. But for
    # pyfa, we can do it here as a post-processing step
    eos.db.gamedata_engine.execute('UPDATE dgmtypeattribs SET value = 4.0 WHERE attributeID = ?', (1367,))

    eos.db.gamedata_engine.execute('UPDATE invtypes  SET published = 0 WHERE typeName LIKE \'%abyssal%\'')

    # fix for #1722 until CCP gets their shit together
    eos.db.gamedata_engine.execute('UPDATE invtypes SET typeName = \'Small Abyssal Energy Nosferatu\' WHERE typeID = ? AND typeName = ?', (48419, ''))

    print()
    for x in CATEGORIES_TO_REMOVE:
        cat = eos.db.gamedata_session.query(eos.gamedata.Category).filter(eos.gamedata.Category.ID == x).first()
        print ('Removing Category: {}'.format(cat.name))
        eos.db.gamedata_session.delete(cat)

    eos.db.gamedata_session.commit()
    eos.db.gamedata_engine.execute('VACUUM')

    print('done')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This scripts dumps effects from an sqlite cache dump to mongo')
    parser.add_argument('-d', '--db', required=True, type=str, help='The sqlalchemy connectionstring, example: sqlite:///c:/tq.db')
    parser.add_argument('-j', '--json', required=True, type=str, help='The path to the json dump')
    args = parser.parse_args()

    main(args.db, args.json)

