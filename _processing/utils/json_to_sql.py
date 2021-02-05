#!/usr/bin/env python3

import os, json
from datetime import datetime
import uuid
import argparse
#######################################
def create_slug(name):
    slug = name.replace(' ', '-').lower()
    slug = slug.replace('_', '-')
    
    return slug
#######################################
parser = argparse.ArgumentParser(description='Adds converts the JSON file to SQL insert statements')
parser.add_argument('-i', '--input', type=str, required=True, 
                    help='Input file located in the output/json directory')
args = parser.parse_args()

script_dir = os.path.dirname(os.path.realpath(__file__))
source_dir = os.path.abspath(os.path.join(script_dir, '..', 'output', 'json'))
infile = f'{source_dir}/{args.input}'

outfile_contents = ''

with open(infile) as f:
  data = json.load(f)

unique_sites = []
valid_medium_types = ['goes', 'goes-self-timed', 'goes-random', 'iridium']
telemetry_types = {
    'goes-self-timed':'10a32652-af43-4451-bd52-4980c5690cc9',
    'iridium':'c0b03b0d-bfce-453a-b5a9-636118940449'
    }

instrument_sql = 'INSERT INTO public.instrument(' \
    'id, deleted, slug, name, formula, geometry, station, station_offset, create_date, update_date,' \
    'type_id, project_id, creator, updater)\n VALUES \n'

instrument_status_sql = 'INSERT INTO public.instrument_status(id, instrument_id, status_id, "time")\n' \
	'VALUES \n'

telemetry_obj = {}

for d in data:

    #print(d['description'])
    # print(type(d))
    _uuid = d['site']['sitenames']['uuid'] 

    if 'transportmedium' not in d.keys():
        print(f'Ignoring {_uuid}, no transportmedium found..')
        continue

    if d['transportmedium']['mediumtype'].lower() not in valid_medium_types:
        print(f"Ignoring {d['transportmedium']['mediumtype']} - {d['transportmedium']['mediumid']}...")
        continue       

    

    # telemetry info for each platform
    telemetry_data = {}  

          
    _sitenames = d['site']['sitenames']
    if 'cwms' in _sitenames.keys():
        name = _sitenames['cwms']
    elif 'local' in _sitenames.keys():
        name = _sitenames['local']
    elif 'nwshb5' in _sitenames.keys():
        name = _sitenames['nwshb5']
    else:
        print(f'Site with UUID: {_uuid} does not have a proper alias/name.  Ignoring...')
        continue

    slug = create_slug(name)
    formula = 'null'
    
    try:
        _lat = round(float(d['site']['latitude']), 4)
        _lon = round(float(d['site']['longitude']), 4)
    except:
        _lat = 0
        _lon = 0
    
    deleted = False 
    geometry = f"ST_GeomFromText('POINT({_lon} {_lat})',4326)"
    station = 'null'
    station_offset = 'null'
    create_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    update_date = 'null'
    type_id = '98a61f29-18a8-430a-9d02-0f53486e0984' #Instrument
    project_id = 'a6e542eb-41bc-45b3-aab7-7f45004ad8d3'
    creator = 'a26d1ef8-acaf-411d-90c1-695bf4c21bf7'
    updater = 'null'

    if name not in unique_sites:
        instrument_sql += f"('{_uuid}', {deleted}, '{slug}', '{name}', {formula}, {geometry}, {station}, {station_offset}, "
        instrument_sql += f"'{create_date}', {update_date}, '{type_id}', '{project_id}', '{creator}', {updater}),\n"
        instrument_status_sql += f"('{uuid.uuid4()}', '{_uuid}', 'e26ba2ef-9b52-4c71-97df-9e4b6cf4174d', '{create_date}'),\n"
        unique_sites.append(name)

        transport_medium_type = d['transportmedium']['mediumtype'].lower()

        # Add to the telemetry object for progressing down below
        if transport_medium_type in telemetry_types.keys():            
            telemetry_data['telemetry_type_id'] = telemetry_types[transport_medium_type]   
            telemetry_data['mediumtype'] = transport_medium_type
            telemetry_data['mediumid'] = d['transportmedium']['mediumid']

            telemetry_obj[_uuid] = telemetry_data            

    else:
        outfile_contents += f'\n--Ignoring {name} site/instrument, already in instruments unique list'

    if d['platform_sensors']:
        for ps in d['platform_sensors']:           
            
                       
            ps_uuid = ps['sitenames']['uuid']
              
            if 'cwms' in ps['sitenames'].keys():
                ps_name = ps['sitenames']['cwms']
            elif 'local' in ps['sitenames'].keys():
                ps_name = ps['sitenames']['local']
            elif 'nwshb5' in ps['sitenames'].keys():
                ps_name = ps['sitenames']['nwshb5']
            else:
                print(f'Site with UUID: {_uuid} does not have a proper alias/name.  Ignoring...')
                continue

            ps_deleted = deleted          
            ps_slug = create_slug(ps_name)
            ps_formula = 'null'
            try:
                _lat = round(float(ps['latitude']), 4)
                _lon = round(float(ps['longitude']), 4)
            except:
                _lat = 0
                _lon = 0
            
            ps_geometry = f"ST_GeomFromText('POINT({_lon} {_lat})',4326)"           
            ps_station = 'null'
            ps_station_offset = 'null'
            ps_create_date = create_date
            ps_update_date = 'null'
            ps_type_id = type_id #Instrument
            ps_project_id = project_id
            ps_creator = creator
            ps_updater = 'null'

            if ps_name not in unique_sites:
                instrument_sql += f"('{ps_uuid}', {ps_deleted}, '{ps_slug}', '{ps_name}', {ps_formula}, {ps_geometry}, {ps_station}, {ps_station_offset}, "
                instrument_sql += f"'{ps_create_date}', {ps_update_date}, '{ps_type_id}', '{ps_project_id}', '{ps_creator}', {ps_updater}),\n"
                instrument_status_sql += f"('{uuid.uuid4()}', '{ps_uuid}', 'e26ba2ef-9b52-4c71-97df-9e4b6cf4174d', '{ps_create_date}'),\n"
                unique_sites.append(ps_name)
            else:
                outfile_contents += f'\n--Ignoring {ps_name} platform sensor site/instrument, already in instruments unique list'



outfile_contents += f'\n\n--INSERT INSTRUMENTS--COUNT:{len(unique_sites)}\n'

# Replace the last line ending comma with semi-colon
instrument_sql = instrument_sql[:-2]+';\n'
outfile_contents += instrument_sql

outfile_contents += '\n--INSERT INSTRUMENT STATUS--\n'

# Replace the last line ending comma with semi-colon
instrument_status_sql = instrument_status_sql[:-2]+';\n'
outfile_contents += instrument_status_sql

''' Create insert statements for telemetry_goes, telemetry_iridium, instrument_telemetry '''

telemetry_goes = []
telemetry_iridium = []

instrument_telemetry_sql = 'INSERT INTO public.instrument_telemetry (instrument_id, telemetry_type_id, telemetry_id) \nVALUES\n'

for id, obj in telemetry_obj.items():

    telemetry_id = uuid.uuid4()
    if 'goes' in obj['mediumtype']:
        telemetry_goes.append([telemetry_id, obj['mediumid']])
    if 'iridium' in obj['mediumtype']:
        telemetry_iridium.append([telemetry_id, obj['mediumid']])

    instrument_telemetry_sql += f"('{id}', \'{obj['telemetry_type_id']}\', '{telemetry_id}'),\n"

if telemetry_goes:
    outfile_contents += f'\n--INSERT TELEMETRY_GOES--COUNT:{len(telemetry_goes)}\n'
    telemetry_goes_sql = 'INSERT INTO public.telemetry_goes (id, nesdis_id) \nVALUES\n'
    for tg in telemetry_goes:
        telemetry_goes_sql += f"('{tg[0]}', '{tg[1]}'),\n"
    # Replace the last line ending comma with semi-colon
    telemetry_goes_sql = telemetry_goes_sql[:-2]+';\n'
    outfile_contents += telemetry_goes_sql

if telemetry_iridium:
    outfile_contents += f'\n--INSERT TELEMETRY_IRIDIUM--COUNT:{len(telemetry_iridium)}\n'
    telemetry_iridium_sql = 'INSERT INTO public.telemetry_iridium (id, imei) \nVALUES\n'
    for ti in telemetry_iridium:
        telemetry_iridium_sql += f"('{ti[0]}', '{ti[1]}'),\n"
    # Replace the last line ending comma with semi-colon
    telemetry_iridium_sql = telemetry_iridium_sql[:-2]+';\n'
    outfile_contents += telemetry_iridium_sql

outfile_contents += f'\n--INSERT INSTRUMENT_TELEMETRY--COUNT:{len(telemetry_obj.keys())}\n'
# Replace the last line ending comma with semi-colon
instrument_telemetry_sql = instrument_telemetry_sql[:-2]+';\n'
outfile_contents += instrument_telemetry_sql


outfile_sql = os.path.abspath(os.path.join(script_dir, '..', 'output', 'sql', f'{os.path.basename(infile)}'))
outfile_sql = outfile_sql.replace('.json', '.sql')
print(f'Saving sql output to: {outfile_sql}')
with open(outfile_sql, 'w') as sql_file:
    sql_file.write(outfile_contents)