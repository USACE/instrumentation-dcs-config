import re
import json
from typing import NamedTuple
import requests

c44_names = {'C44D1A-L1': 'C44D1A-SW-L1',
'C44D1B-L1': 'C44D1B-SW-L1',
'C44E4D-L1': 'C44E4D-SW-L1',
'C44E4A-L1': 'C44E4A-SW-L1',
'C44E2A-L1': 'C44E2A-SW-L1',
'C44E1A-G1': 'C44E1A-GW-1L',
'C44E1A-G2': 'C44E1A-GW-2L',
'C44E1A-G3': 'C44E1A-GW-3L',
'C44E1A-G4': 'C44E1A-GW-4L',
'C44E1A-G5': 'C44E1A-GW-5L',
'C44E1A-G6': 'C44E1A-GW-6L',
'C44E1A-G7': 'C44E1A-GW-7L',
'C44E1A-G8': 'C44E1A-GW-8L',
'C44E1A-G9': 'C44E1A-GW-9L',
'C44E1A-G10': 'C44E1A-GW-10L',
'C44S1B-L1': 'C44S1B-SW-L1',
'C44E1B-G1': 'C44E1B-GW-1L',
'C44E1B-G2': 'C44E1B-GW-2L',
'C44E1B-G3': 'C44E1B-GW-3L',
'C44E1B-G4': 'C44E1B-GW-4L',
'C44E1B-G5': 'C44E1B-GW-5L',
'C44E1B-G6': 'C44E1B-GW-6L',
'C44E1B-G7': 'C44E1B-GW-7L',
'C44E1B-G8': 'C44E1B-GW-8L',
'C44E1B-G9': 'C44E1B-GW-9L',
'C44E1B-G10': 'C44E1B-GW-10L',
'C44E2B-G1': 'C44E2B-GW-1L',
'C44E2B-G2': 'C44E2B-GW-2L',
'C44E2B-G3': 'C44E2B-GW-3L',
'C44E2B-G4': 'C44E2B-GW-4L',
'C44E2B-G5': 'C44E2B-GW-5L',
'C44E2B-G6': 'C44E2B-GW-6L',
'C44E2B-G7': 'C44E2B-GW-7L',
'C44E2B-G8': 'C44E2B-GW-8L',
'C44E2B-G9': 'C44E2B-GW-9L',
'C44E2B-G10': 'C44E2B-GW-10L',
'C44S2C-L1': 'C44S2C-SW-L1',
'C44E2C-G5': 'C44E2C-GW-5L',
'C44E2C-G6': 'C44E2C-GW-6L',
'C44E2C-G7': 'C44E2C-GW-7L',
'C44E2C-G8': 'C44E2C-GW-8L',
'C44E2C-G9': 'C44E2C-GW-9L',
'C44E2C-G10': 'C44E2C-GW-10L',
'C44E3A-G1': 'C44E3A-GW-1L',
'C44E3A-G2': 'C44E3A-GW-2L',
'C44E3A-G3': 'C44E3A-GW-3L',
'C44E3A-G4': 'C44E3A-GW-4L',
'C44E3A-G5': 'C44E3A-GW-5L',
'C44E3A-G6': 'C44E3A-GW-6L',
'C44E3A-G7': 'C44E3A-GW-7L',
'C44E3A-G8': 'C44E3A-GW-8L',
'C44E3A-G9': 'C44E3A-GW-9L',
'C44E3A-G10': 'C44E3A-GW-10L',
'C44S4D-L1': 'C44S4D-SW-L1',
'C44E4D-G1': 'C44E4D-GW-1L',
'C44E4D-G2': 'C44E4D-GW-2L',
'C44E4D-G3': 'C44E4D-GW-3L',
'C44E4D-G4': 'C44E4D-GW-4L',
'C44E4D-G5': 'C44E4D-GW-5L',
'C44E4D-G6': 'C44E4D-GW-6L',
'C44E4D-G7': 'C44E4D-GW-7L',
'C44E4D-G8': 'C44E4D-GW-8L',
'C44E4D-G9': 'C44E4D-GW-9L',
'C44E4D-G10': 'C44E4D-GW-10L',
'C44E4C-G1': 'C44E4C-GW-1L',
'C44E4C-G2': 'C44E4C-GW-2L',
'C44E4C-G3': 'C44E4C-GW-3L',
'C44E4C-G4': 'C44E4C-GW-4L',
'C44E4C-G5': 'C44E4C-GW-5L',
'C44E4C-G6': 'C44E4C-GW-6L',
'C44E4C-G7': 'C44E4C-GW-7L',
'C44E4C-G8': 'C44E4C-GW-8L',
'C44E4C-G9': 'C44E4C-GW-9L',
'C44E4C-G10': 'C44E4C-GW-10L',
'C44E4B-G5': 'C44E4B-GW-5L',
'C44E4B-G6': 'C44E4B-GW-6L',
'C44E4B-G7': 'C44E4B-GW-7L',
'C44E4B-G8': 'C44E4B-GW-8L',
'C44E4B-G9': 'C44E4B-GW-9L',
'C44E4B-G10': 'C44E4B-GW-10L',
'C44E4A-G5': 'C44E4A-GW-5L',
'C44E4A-G6': 'C44E4A-GW-6L',
'C44E4A-G7': 'C44E4A-GW-7L',
'C44E4A-G8': 'C44E4A-GW-8L',
'C44E4A-G9': 'C44E4A-GW-9L',
'C44E4A-G10': 'C44E4A-GW-10L',
'C44E2A-G5': 'C44E2A-GW-5L',
'C44E2A-G6': 'C44E2A-GW-6L',
'C44E2A-G7': 'C44E2A-GW-7L',
'C44E2A-G8': 'C44E2A-GW-8L',
'C44E2A-G9': 'C44E2A-GW-9L',
'C44E2D-G5': 'C44E2D-GW-5L',
'C44E2D-G6': 'C44E2D-GW-6L',
'C44E2D-G7': 'C44E2D-GW-7L',
'C44E2D-G8': 'C44E2D-GW-8L',
'C44E2D-G9': 'C44E2D-GW-9L',
'C44B8A-G1': 'C44B8A-GW-1L',
'C44B8A-G2': 'C44B8A-GW-2L',
'C44B8A-G3': 'C44B8A-GW-3L',
'C44B8A1-PC': 'C44B8A1-PC',
'C44B1A1': 'C44B1A-GW-1L',
'C44B1B-G1': 'C44B1B-GW-1L',
'C44B1B-G2': 'C44B1B-GW-2L',
'C44B1B1-PC': 'C44B1B1-PC',
'C44B8D-G1': 'C44B8D-GW-1L',
'C44B8D-G2': 'C44B8D-GW-2L',
'C44B8D-G3': 'C44B8D-GW-3L',
'C44B8D1-PC': 'C44B8D1-PC',
'C44B8C-G1': 'C44B8C-GW-1L',
'C44B8C-G2': 'C44B8C-GW-2L',
'C44B8B-G1': 'C44B8B-GW-1L',
'S403-HP': 'S403-U-L1',
'S401-HW': 'S-401-U-L1',
'S401-TW': 'C44E2D-SW-L1'}

def c44_midas():
    url = 'https://midas-api.rsgis.dev/projects/6c56c7b0-2d9f-4a1b-9173-b969942dacb5/instruments'
    req = requests.get(url=url)
    instruments = req.json()

    flip_c44_names = {
        v: k
        for k, v in c44_names.items()
    }

    
    d = dict()
    for instrument in instruments:
        name = instrument['name']
        new_name = flip_c44_names[name]

        d[new_name] = {'name': instrument['name'], 'coords': instrument['geometry']['coordinates']}

        # name_parts = name.split('-')

        # if len(name_parts) == 3:
        #     num = re.compile(r'\d+')
        #     match = num.match(name_parts[-1])
        #     if match:
        #         new_name = name_parts[0] + str(match.group())

                # d[new_name] = {'name': instrument['name'], 'coords': instrument['geometry']['coordinates']}
    
    return d

def main():
    midas_locations = c44_midas()
    
    

    ucpattern = re.compile(r'^.*(C44[A-Z0-9]+-[A-Z0-9]+).*$')
    sql = '/Users/rdcrljsg/projects/instrumentation-dcs-config/_processing/output/sql/p.sad.saj.sql'
    sql_new = '/Users/rdcrljsg/projects/instrumentation-dcs-config/_processing/output/sql/p.sad.saj.mod.sql'
    with open(sql, 'r') as fpin, open(sql_new, 'w') as fpout:
        for line in fpin.readlines():
            match = ucpattern.search(line)
            if match:
                line_ = match.group(0) + '\n'
                src = match.group(1)
                dst = midas_locations[src]['name']
                line = line_.replace(src, dst).replace(src.lower(), dst.lower()).replace('POINT(0 0)', 'POINT({} {})'.format(midas_locations[src]['coords'][0], midas_locations[src]['coords'][1]))

            #     try:
            #         dst = midas_locations[src]['name']
            #         line = line_.replace(src, dst).replace(src.lower(), dst.lower()).replace('POINT(0 0)', 'POINT({} {})'.format(midas_locations[src]['coords'][0], midas_locations[src]['coords'][1]))
            #     except:
            #         print(src + ' not found')

            fpout.write(line)


if __name__ == '__main__':
    main()