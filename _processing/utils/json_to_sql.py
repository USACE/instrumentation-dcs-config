#!/usr/bin/env python3

import os, json
from datetime import datetime
import uuid
import argparse
import requests
#######################################
def create_slug(name):
    # print(f'create_slug() received name: {name}')
    bad_chars = [' ', '_', ',', '(', ')']
    if any((bc in bad_chars) for bc in name):
        slug = name
        for bc in bad_chars:
            if bc in name:
                # print(f'Replacing char {bc}')
                slug = slug.strip().replace(bc, '-').lower()

        # replacing multiple bad chars next to each other could result in 
        # two hyphens together - handle it
        slug = slug.strip().replace('--', '-')
        # If first or last char results in '-', remove it
        if slug[-1] == '-':slug = slug[:-1]
    else:
        slug = name.strip().lower()
    
    return slug
#######################################
def get_usgs_name(usgs_id):

    print(f'Looking up name for USGS ID: {usgs_id}')

    if usgs_id.isdigit():
        r = requests.get(f'https://waterservices.usgs.gov/nwis/iv/?format=json&sites={usgs_id}&siteStatus=all')
        try:
            name = r.json()['value']['timeSeries'][0]['sourceInfo']['siteName']           
            
        except Exception as e:
            print(e)
            print(f'Unable to retrieve {usgs_id} from USGS web service.')
            return usgs_id

        print(f'USGS web service name: {name}')
        # remove anything after first comma encountered
        # name = name.split(',')[0]
        # if ' NEAR ' in name.upper():
        #     # reformat/parse name using the word 'NEAR'
        #     _parts = name.split(' NEAR ')
        #     name = f'{_parts[1].strip()} ({_parts[0].strip()})'
        # elif ' AT ' in name.upper():
        #     _parts = name.split(' AT ')
        #     name = f'{_parts[1].strip()} ({_parts[0].strip()})'       
        
        return name
    else:
        # USGS ID is not a number, return original value
        return usgs_id
#######################################
def lookup_midas_param_info(configsensor_obj):
    '''
    This function will attempt to scan through through the config
    sensor object for CWMS, SHEF-PE codes and map to MIDAS params/units
    exmaple object will look like:
    {'Standard': 'CWMS', 'Code': 'Stage', 'Name': 'CWMS:Stage'}
    {'Standard': 'SHEF-PE', 'Code': 'YU', 'Name': 'SHEF-PE:YU'}
    '''

    midas = {
        'air-temperature':{
            'name': 'Air Temperature',
            'slug': 'air-temperature',
            'parameter_id': 'de6112da-8489-4286-ae56-ec72aa09974d',
            'unit_id': '10e05b5c-7e96-434b-9182-a547333e1c52'
        },
        'conductivity':{
            'name': 'Conductivity',
            'slug': 'conductivity',
            'parameter_id': '377ecec0-f785-46ab-b0e2-5fd8c682dfea',
            'unit_id': '633bd96c-5bdb-436f-b464-f18d90b7d736'
        },
        'dissolved-oxygen':{
            'name': 'Dissolved Oxygen',
            'slug': 'dissolved-oxygen',
            'parameter_id': '98007857-d027-4524-9a63-d07ae93e5fa2',
            'unit_id': '67d75ccd-6bf7-4086-a970-5ed65a5c30f3'
        },
        'elevation':{
            'name': 'Elevation',
            'slug': 'elevation',
            'parameter_id': '83b5a1f7-948b-4373-a47c-d73ff622aafd',
            'unit_id': 'f777f2e2-5e32-424e-a1ca-19d16cd8abce'
        },
        'stage':{
            'name': 'Stage',
            'slug': 'stage',
            'parameter_id': 'b49f214e-f69f-43da-9ce3-ad96042268d0',
            'unit_id': 'f777f2e2-5e32-424e-a1ca-19d16cd8abce'
        },
        'ph':{
            'name': 'pH', 
            'slug': 'ph',
            'parameter_id': '5d0b2c85-6a4c-4d82-aed3-193b066349f1',
            'unit_id': 'cfac3e61-64e1-456d-890e-0655038e8218'
        },
        'precipitation':{
            'name': 'Precipitation', 
            'slug': 'precipitation',
            'parameter_id': '0ce77a5a-8283-47cd-9126-c440bcec4ef6',
            'unit_id': '4ee79a3d-a053-41b8-85b5-bb2eea3c9d1a'
        },
        'power-generation-discharge':{
            'name': 'Power Generation Discharge',
            'slug': 'power-generation-discharge',
            'parameter_id': 'a63a3202-3115-4ad4-9e5b-3d35f94647d2',
            'unit_id': '67d3c3f0-ae76-4807-8cdd-4e29fa8d8b39'
        },
        'turbidity':{
            'name': 'Turbidity', 
            'slug': 'turbidity',
            'parameter_id': 'de6112da-8489-4286-ae56-ec72aa09974d',
            'unit_id': 'e65274a5-3d42-4b96-8db6-696d65d92a8d'
        },
        'voltage':{
            'name': 'Voltage',
            'slug': 'voltage',
            'parameter_id': '430e5edb-e2b5-4f86-b19f-cda26a27e151',
            'unit_id': '6b5bd788-8c78-43bb-b5a3-ad544b858a64'
        },        
        'water-temperature':{
            'name': 'Water Temperature',
            'slug': 'water-temperature',
            'parameter_id': 'de6112da-8489-4286-ae56-ec72aa09974d',
            'unit_id': '10e05b5c-7e96-434b-9182-a547333e1c52'
        },
        'water-velocity':{
            'name': 'Water Velocity',
            'slug': 'water-velocity',
            'parameter_id': '06189199-a25f-4101-b8bd-991c6a5a7ab3',
            'unit_id': 'c96294dc-f238-4d4d-8705-0a1b2d3f9b55'
        },
        'wind-speed':{
            'name': 'Wind Sspeed',
            'slug': 'wind-speed',
            'parameter_id': 'e46deb1d-e7e4-4d49-a874-18306991ecfe',
            'unit_id': 'e142d705-9eb6-4965-91d0-af55739189b0'
        }
        

    }

    cs = configsensor_obj
    param = cs['Code'].lower()

    # keys should equal keys above
    # values in list are possible params in xml
    param_lookup = {
        'air-temperature': ['temp-air', 'te', 'ta'],
        'conductivity': ['cond', 'wc'],
        'dissolved-oxygen': ['conc-do', 'do', 'wo', '00300', '00299'],
        'elevation': ['elevation', 'elev', 'elev-tail', 'hp', 'ht'],
        'precipitation': ['precipitation', 'precip', 'pc', 'pp', '00045'],
        'ph': ['ph', 'wp', '00400', '00403', '00406'],
        'power-generation-discharge': ['qg'],
        'stage': ['stage', 'stage-tail', 'stage-tailwater', 'hg', '00065', '00072'],
        'turbidity': ['wt'],        
        'voltage': ['voltage', 'volt', 'volts', 'vb', 'battvolt', 'batt', 'battery', 'bl', '70969'],        
        'water-temperature': ['water-temp', 'temp-water', 'water-temperature', 'tw'],
        'water-velocity': ['wv'],
        'wind-speed': ['us', 'wind-speed', 'speed-wind']        
    }

    for k,v in param_lookup.items():
        if param in v:
            return midas[k]

    print(f'WARNING: Unknown Param {cs}')
    return {}


    # if param in ['stage', 'stage-tail', 'stage-tailwater', 'hg']:
    #     return midas['stage']
    # elif param in ['elevation', 'elev', 'elev-tail', 'hp']:
    #     return midas['elevation']
    # elif param in ['voltage', 'volt', 'volts', 'vb', 'battvolt']:
    #     return midas['voltage']
    # elif param in ['precipitation', 'precip', 'pc', 'pp']:
    #     return midas['precipitation']
    # elif param in ['water-temp', 'temp-water', 'water-temperature', 'tw']:
    #     return midas['water-temperature']
    # else:
    #     print(f'WARNING: Unknown Param {cs}')
    #     return {}

    
#######################################

parser = argparse.ArgumentParser(description='Adds converts the JSON file to SQL insert statements')
parser.add_argument('-i', '--input', type=str, required=True, 
                    help='Input file located in the output/json directory')
parser.add_argument('-p', '--projectuuid', type=str, required=True, 
                    help='Project UUID')
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
    'id, deleted, slug, name, formula, geometry, station, station_offset, ' \
    'create_date, update_date, type_id, project_id, creator, updater)\n VALUES \n'

instrument_status_sql = 'INSERT INTO public.instrument_status(id, instrument_id, ' \
    'status_id, "time")\n VALUES \n'

telemetry_obj = {}
timeseries_data = {}

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
    elif 'usgs' in _sitenames.keys():
        # name = _sitenames['usgs']
        name = get_usgs_name(_sitenames['usgs'])
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
    project_id = args.projectuuid
    creator = '00000000-0000-0000-0000-000000000000'
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

        # Build the timeseries object for processing down below        
       
        config_sensors = d['config_sensors']
        if config_sensors.keys():
            param_data = {}
            for label, cs_obj in config_sensors.items():
                # print(label, '-> ', cs_obj)
                _param = lookup_midas_param_info(cs_obj)
                if _param.keys():
                    param_data[_param['name']] = _param
                    # print(param_data)
                

            timeseries_data[_uuid] = param_data
            # print(timeseries_data[_uuid])

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

instrument_telemetry_sql = 'INSERT INTO public.instrument_telemetry (instrument_id, ' \
                            'telemetry_type_id, telemetry_id) \nVALUES\n'

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


# Timeseries SQL Prep
timeseries_sql = 'INSERT INTO public.timeseries(id, slug, name, instrument_id, ' \
    'parameter_id, unit_id) \nVALUES\n'
for instrument_id, obj in timeseries_data.items():
    for param, param_obj in obj.items():
        timeseries_sql += f"('{uuid.uuid4()}','{param_obj['slug']}','{param_obj['name']}',"
        timeseries_sql += f"'{instrument_id}', '{param_obj['parameter_id']}', '{param_obj['unit_id']}'),\n"


outfile_contents += f'\n--INSERT INSTRUMENT_TELEMETRY--COUNT:{len(telemetry_obj.keys())}\n'
# Replace the last line ending comma with semi-colon
instrument_telemetry_sql = instrument_telemetry_sql[:-2]+';\n'
outfile_contents += instrument_telemetry_sql

outfile_contents += f'\n--INSERT TIMESERIES--COUNT:{len(timeseries_data.keys())}\n'
# Replace the last line ending comma with semi-colon
timeseries_sql = timeseries_sql[:-2]+';\n'
outfile_contents += timeseries_sql



outfile_sql = os.path.abspath(os.path.join(script_dir, '..', 'output', 'sql', f'{os.path.basename(infile)}'))
outfile_sql = outfile_sql.replace('.json', '.sql')
print(f'Saving sql output to: {outfile_sql}')
with open(outfile_sql, 'w') as sql_file:
    sql_file.write(outfile_contents)