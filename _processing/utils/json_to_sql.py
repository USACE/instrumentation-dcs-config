#!/usr/bin/env python3

import os, json
from datetime import datetime
import uuid
import argparse
import requests
#######################################
def capitalize_name(name):
    exceptions = ['ph']
    name_parts = name.split('-')

    if len(name_parts) == 1:
        if name not in exceptions:
            return name.capitalize()
        else:
            return name
    else:
        new_name = ''
        for part in name_parts:
            new_name += part.capitalize()+'-'
        
        if new_name[-1] == '-':
            new_name = new_name[:-1]
        
        return new_name
#######################################
def create_slug(name, unique_slugs):
    # print(f'create_slug() received name: {name}')
    bad_chars = [' ', '_', ',', '(', ')', '.']
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
        if slug[-1] == '-': slug = slug[:-1]
        if slug[0] == '-': slug = slug[1:]
    else:
        slug = name.strip().lower()

    if slug in unique_slugs:
        slug = f"{slug}_{str(uuid.uuid4()).split('-')[1]}"
        print(f'slug conflict - generating unique slug: {slug}')
    
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
def lookup_midas_param_info(configsensor_obj, midas_units, midas_params):
    # print('\n\nConfigSensor Object')
    # print(configsensor_obj)

    # print(midas_units)
    # for unit in midas_units:
    #     print(unit)
    '''
    {'id': 'a0be2c0a-e6e7-41c1-9417-91f6a4d2f8ea', 'name': 'Watt-hours', 
    'abbreviation': 'Wh', 'unit_family_id': 'c9f3b6d2-3136-4330-a330-66e402b4ee04', 
    'unit_family': 'univ', 'measure_id': '3ce398f2-985f-4ed4-93f6-23595d1849b7', 
    'measure': 'energy'}
    '''

    cs = configsensor_obj
    param = cs['Code'].lower().strip()
    unit_abbrev = cs['ToUnitsAbbr'].lower().strip()

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

     
    
    param_name = None
    # Find the parameter name based on possible codes used in DECODES
    for k,v in param_lookup.items():
        if param in v:
            param_name = k
            # print(param)

    # print(f'param_name is: {param_name}')

    param_id = None
    # If param_name was found
    if param_name:
        # search midas params for a match
        for item in midas_params:
            if item['value'] == param_name:
                # print('found param') 
                # print(item['id'])
                param_id = item['id']

    unit_id = None
    # print(f'unit_abbrev is: {unit_abbrev}')

    # search midas units for a match
    for item in midas_units:
        # print(f"checking {unit_abbrev} against {item['name'].lower()} and {item['abbreviation'].lower()}")
        if item['name'].lower() == unit_abbrev or item['abbreviation'].lower() == unit_abbrev:
            unit_id = item['id']


    return_dict = {}
    if param_id is not None and unit_id is not None and 'uuid' in cs.keys():
        return_dict['name'] = capitalize_name(param_name)
        return_dict['slug'] = param_name.lower().replace(' ', '-')
        return_dict['parameter_id'] = param_id
        return_dict['unit_id'] = unit_id
        return_dict['uuid'] = cs['uuid']
    elif 'uuid' in cs.keys():
        # print(f'Setting TS to Unknown Param or Unit')
        return_dict['name'] = f"Unknown {cs['Code']}"
        return_dict['slug'] = return_dict['name'].lower().replace(' ', '-')
        return_dict['parameter_id'] = '2b7f96e1-820f-4f61-ba8f-861640af6232' #unknown
        return_dict['unit_id'] = '4a999277-4cf5-4282-93ce-23b33c65e2c8' #unknown
        return_dict['uuid'] = cs['uuid']
    else:
        print(f'WARNING: Unable to map param: {param} or unit {unit_abbrev}')
        pass
    
    # print(f"returning {return_dict}")
    return return_dict

#######################################
def lookup_midas_param_info2(configsensor_obj):
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
            'unit_id': 'b4ea8385-48a3-4e95-82fb-d102dfcbcb54'
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
            'unit_id': '6462733b-5b42-46a2-ad44-882a5332eafc'
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
def get_hads_data():
    # Get the midas units lookup data from MIDAS API
    r = requests.get('https://hads.ncep.noaa.gov/USGS/ALL_USGS-HADS_SITES.txt')

    try:
        data = r.text   
    except Exception as e:
        print(e)
        print(f'Unable to retrieve HADS Data.')
        return {}

    hads = {}

    for idx, line in enumerate(data.splitlines()):
        
        #ignore headers
        if idx <=3:
            continue

        parts = line.split('|')
       
        nwshb5 = parts[0].strip()
        usgsid = str(parts[1].strip())
        nesdis = parts[2].strip()
        lat = parts[4].strip()
        lon = parts[5].strip()

        lat_deg = int(lat.split()[0])
        lat_min = int(lat.split()[1])
        lat_sec = float(lat.split()[2])
        lat_dd = round(lat_deg+(lat_min/60)+(lat_sec/3600), 4)

        lon_deg = int(lon.split()[0])
        lon_min = int(lon.split()[1])
        lon_sec = float(lon.split()[2])
        lon_dd = round(lon_deg+(lon_min/60)+(lon_sec/3600), 4)
        # Force to negative value
        if lon_dd > 0:
            lon_dd = lon_dd*-1

        name = parts[6].strip()

        hads[nesdis] = {'nwshb5':nwshb5, 'usgsid':usgsid, 'lat':lat_dd, 'lon':lon_dd, 'name':name}

    return hads

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

# Get the midas units lookup data from MIDAS API
r = requests.get('https://midas-api.rsgis.dev/units')
# r = requests.get('http://localhost/instrumentation/units')
try:
    midas_units = r.json()    
except Exception as e:
    print(e)
    print(f'Unable to retrieve MIDAS API Data.')
    exit(1)

# Get the midas domains (for params)
r = requests.get('https://midas-api.rsgis.dev/domains')
try:
    midas_params = []
    _temp_response = r.json()
    for item in _temp_response:
        if item['group'] == 'parameter':
            midas_params.append(item)
except Exception as e:
    print(e)
    print(f'Unable to retrieve MIDAS API Data.')
    exit(1)


outfile_contents = ''

with open(infile) as f:
  data = json.load(f)

unique_sites = []
valid_medium_types = ['goes', 'goes-self-timed', 'goes-random', 'iridium']
telemetry_types = {
    'goes-self-timed':'10a32652-af43-4451-bd52-4980c5690cc9',
    'iridium':'c0b03b0d-bfce-453a-b5a9-636118940449'
    }

instrument_sql = 'INSERT INTO instrument(' \
    'id, deleted, slug, name, formula, geometry, station, station_offset, ' \
    'create_date, update_date, type_id, project_id, creator, updater, usgs_id)\n VALUES \n'

instrument_status_sql = 'INSERT INTO instrument_status(id, instrument_id, ' \
    'status_id, "time")\n VALUES \n'

telemetry_obj = {}
timeseries_data = {}

unique_slugs = []

try:
    r = requests.get(f'http://localhost/instruments')          
    
except:
    print('Unable to connect to local API, trying rsgis.dev')
    r = requests.get(f'https://midas-api.rsgis.dev/instruments')

for i in r.json():
    unique_slugs.append(i['slug'])


hads_data = get_hads_data()




for d in data:

    hads_site_data = None

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

    if 'goes' in d['transportmedium']['mediumtype'].lower() and d['transportmedium']['mediumid'] in hads_data.keys():
        # print('found hads data')
        hads_site_data = hads_data[d['transportmedium']['mediumid']]
    
    if name.isdigit() and hads_site_data:
        name = hads_site_data['name']
    
    slug = create_slug(name, unique_slugs)
    unique_slugs.append(slug)
    formula = 'null'  

    
    try:
        _lat = round(float(d['site']['latitude']), 4)
        _lon = round(float(d['site']['longitude']), 4)
    except:        
        _lat = 0
        _lon = 0

    # Try to get GPS from HADS lookup if possible
    if _lat == 0 and hads_site_data:
        print('Setting GPS from HADS')
        _lat = hads_site_data['lat']
        _lon = hads_site_data['lon']
        print(f'lat/lon: {_lat}/{_lon}')

    
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
    usgs_id = 'null'
    if 'usgs' in _sitenames.keys() and _sitenames['usgs'].isdigit():
        usgs_id = f"\'{_sitenames['usgs']}\'"
    else:
        if hads_site_data:
            print(f"Setting USGS_ID: {hads_site_data['usgsid']} from HADS for {name}")
            usgs_id = f"\'{hads_site_data['usgsid']}\'"

    if name not in unique_sites:
        instrument_sql += f"('{_uuid}', {deleted}, '{slug}', '{name}', {formula}, {geometry}, {station}, {station_offset}, "
        instrument_sql += f"'{create_date}', {update_date}, '{type_id}', '{project_id}', '{creator}', {updater}, {usgs_id}),\n"
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
                if bool(cs_obj):
                    _param = lookup_midas_param_info(cs_obj, midas_units, midas_params)
                    if _param.keys():
                        # print(f'\n_param is: {_param}\n')
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
            ps_slug = create_slug(ps_name, unique_slugs)
            unique_slugs.append(ps_slug)
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
            ps_usgs_id = 'null'
            if 'usgs' in ps['sitenames'].keys() and ps['sitenames']['usgs'].isdigit():
                ps_usgs_id = f"\'{ps['sitenames']['usgs']}\'"                

            if ps_name not in unique_sites:
                instrument_sql += f"('{ps_uuid}', {ps_deleted}, '{ps_slug}', '{ps_name}', {ps_formula}, {ps_geometry}, {ps_station}, {ps_station_offset}, "
                instrument_sql += f"'{ps_create_date}', {ps_update_date}, '{ps_type_id}', '{ps_project_id}', '{ps_creator}', {ps_updater}, {ps_usgs_id}),\n"
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

instrument_telemetry_sql = 'INSERT INTO instrument_telemetry (instrument_id, ' \
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
    telemetry_goes_sql = ''
    for tg in telemetry_goes:
        telemetry_goes_sql += f"INSERT INTO telemetry_goes (id, nesdis_id) select '{tg[0]}', '{tg[1]}' where not exists (select 1 from telemetry_goes where nesdis_id = '{tg[1]}');\n"
    # Replace the last line ending comma with semi-colon
    # telemetry_goes_sql = telemetry_goes_sql[:-2]+';\n'
    outfile_contents += telemetry_goes_sql

if telemetry_iridium:
    outfile_contents += f'\n--INSERT TELEMETRY_IRIDIUM--COUNT:{len(telemetry_iridium)}\n'
    telemetry_iridium_sql = ''
    for ti in telemetry_iridium:
        telemetry_iridium_sql += f"INSERT INTO telemetry_iridium (id, imei) select '{ti[0]}', '{ti[1]}' where not exists (select 1 from telemetry_iridium where imei = '{ti[1]}');\n"
    # Replace the last line ending comma with semi-colon
    # telemetry_iridium_sql = telemetry_iridium_sql[:-2]+';\n'
    outfile_contents += telemetry_iridium_sql


# Timeseries SQL Prep
timeseries_sql = 'INSERT INTO timeseries(id, slug, name, instrument_id, ' \
    'parameter_id, unit_id) \nVALUES\n'
for instrument_id, obj in timeseries_data.items():
    for param, param_obj in obj.items():
        # print(param_obj)
        timeseries_sql += f"('{param_obj['uuid']}','{param_obj['slug']}','{param_obj['name']}',"
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