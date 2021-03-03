#!/usr/bin/env python3

import os
import uuid
#using lxml to get 'standalone' option in write function
from lxml import etree as ET
import pprint, json
import argparse
from html import unescape, escape
import re
############################################################
def add_uuid_to_site(site_element):

    uuid_set = False
    last_index = 0
    
    # Check to see if UUID has already been added
    for idx, site_elem in enumerate(site_element):
        
        if site_elem.get('NameType') == 'uuid':            
            uuid_set = True 
            print(f'WARNING: UUID {site_elem.text.strip()} already set')
            return False
        else:
            # remove any weird spaces or newlines in current SiteName text
            site_elem.text = site_elem.text.strip()

        # Keep track of the index SiteName elements to determine 
        # where to insert new SiteName
        if site_elem.tag == 'SiteName':
            # print(f"{site_elem.get('NameType')} = {site_elem.text}")        
            last_index = idx

    # If UUID not added, append to the SiteName element list
    if not uuid_set:
        _uuid = uuid.uuid4()
        print(f'Adding UUID SiteName: {_uuid}')
        new_sitename = ET.Element('SiteName')
        new_sitename.text=str(_uuid)
        new_sitename.set('NameType', 'uuid')
        new_sitename.tail = '\n      '            

        site_element.insert(last_index+1, new_sitename)

        return str(_uuid)
############################################################
def get_platform_fields(platform_element):

    platform_fields = {}

    for elem in platform_element: 
        if elem.text is not None:
            platform_fields[elem.tag.lower()] = elem.text.strip()
        else:
            platform_fields[elem.tag.lower()] = elem.text
        
        print(elem.tag.lower(), '->', elem.text)

    return platform_fields
############################################################
def parse_coordinate(name, value):
    try:
        dd = round(float(value),4)
    except:
        print(f'{name}: {value} is not a proper coodinate format***')
        print('Attempting to convert...')
        '''
        Possible coord formats:
        36 19 23 N
        085 07 18 W
        36 05 30
        N 43&#176;05&apos;32&quot;
        '''
        value = value.lower().replace('n','').strip()
        value = value.lower().replace('w','').strip()
        # print(f'Value stripped of N or W is:{value}')
        '''
        Possible formats after N and W have been removed:
        36 17 49
        086  25 43
        36*10'02"
        35 27' 46"
        '''        
        # remove special chars to help with regex
        value = unescape(value)
        
        x = re.match(r"^(\d+)\W+(\d+)\W+(\d*\.?\d*)\W?$", value)                

        if x:
            degrees = int(x.groups()[0])
            minutes = int(x.groups()[1])
            seconds = float(x.groups()[2])
            dd = round(degrees+(minutes/60)+(seconds/3600), 4)
            if name == 'longitude':
                dd = dd*-1
            print(f'{name}: {dd}')

        else:
            print(f'No RegEx match for coordinate format: {value}')
            dd = 0,0
        
    return dd
############################################################
def get_site_fields(site_element):

    print('\n"Site" fields: ')

    site_fields = {}
    sitenames = {}

    for elem in site_element:
        if elem.attrib.items():
            for k,v in elem.attrib.items():
                if elem.tag == 'SiteName': 
                    sitenames[elem.get(k).lower()] = elem.text.strip()                 
                    print(elem.tag,':',elem.get(k).lower(), '->', tag_value)
        else:
            if elem.tag.lower().strip() in ('latitude', 'longitude'): 
                tag_value = parse_coordinate(elem.tag.lower(), elem.text.strip())
            else:
                tag_value = elem.text.strip()
            
            site_fields[elem.tag.lower()] = tag_value

    site_fields['sitenames'] = sitenames

    return site_fields
############################################################
def add_platform_sensor(sensor_number, parent_elem):

    print(f'Adding PlatformSensor element')

    print(f'SensorNumber: {sensor_number}')

    last_index = 0

    for idx, elem in enumerate(parent_elem):
        last_index = idx

    # print(parent_elem[0].getchildren().tag)
    _uuid = uuid.uuid4()
    new_elem = ET.Element('PlatformSensor')
    # new_elem.text=str(_uuid)
    new_elem.set('SensorNumber', str(sensor_number))
    new_elem.tail = '\n  '

    # new_sub_elem = ET.Element('PlatformSensorProperty')
    # new_sub_elem.set('PropertyName', 'uuid')
    # new_sub_elem.text=str(_uuid)

    # Adjust the tail of the prev platform child element to allow
    # proper indention of the new element
    parent_elem[last_index].tail = '\n    '

    parent_elem.insert(last_index+1, new_elem)

    return
############################################################
def add_platform_sensor_uuid_property(parent_elem):

    last_index = 0

    for idx, elem in enumerate(parent_elem):
        last_index = idx
        print(f'index is: {idx}')
        print(f'element is: {elem.tag}')

    _uuid = uuid.uuid4()
    new_elem = ET.Element('PlatformSensorProperty')
    new_elem.text=str(_uuid)
    new_elem.set('PropertyName', 'uuid')
    new_elem.tail = '\n    '

    if last_index > 0:
        # Adjust the tail of the prev platform child element to allow
        # proper indention of the new element
        parent_elem[last_index].tail = '\n      \n'

    print(f'Inserting uuid property inside element: {parent_elem.tag}')
    parent_elem.insert(last_index+1, new_elem)

############################################################
parser = argparse.ArgumentParser(description='Adds UUIDs to Platforms XML Export')
parser.add_argument('-i', '--input', type=str, required=True, 
                    help='Input file located in the original_exports directory')
parser.add_argument('--overwrite', type=str, default=False,
                    help='Yes to overwrite output file.')
args = parser.parse_args()

script_dir = os.path.dirname(os.path.realpath(__file__))
original_dir = os.path.abspath(os.path.join(script_dir, '../original_exports'))
infile = f'{original_dir}/{args.input}'
outfile_xml = os.path.abspath(os.path.join(script_dir, '../../', os.path.basename(infile)))

# Check for input file
if not os.path.isfile(infile):
    print(f'ERROR: Input file not found: {infile}')
    exit(1)

# Check for output file and warn about overwrite
if os.path.isfile(outfile_xml):
    print(f'WARNING: Output file is present: {outfile_xml}')
    if args.overwrite is False:
        user_input = input("Do you with to overwrite? (y) or (n):").lower()
        if user_input not in ('y', 'yes'):
            print('Exiting...')
            exit(0)

tree = ET.parse(infile)
root = tree.getroot()
platforms = root.findall('Platform')

print(f'Platform count: {len(platforms)}')

# Setup json container
platforms_list = []

for p in platforms:

    # Setup platform object
    platform_obj = {}

    print('-'*60)
    print(f"Platform Id: {p.get('PlatformId')}")
    
    # Check for expiration tag - usually means it's already expired
    expiration = p.find('Expiration')
    if expiration is not None:
        print('INFO: Platform has been marked "Expired".  Ignoring...')
        continue

    # Set IsProduction to True for all
    isProduction = p.find('IsProduction')
    if isProduction is not None and isProduction.text.strip() == 'false':
        print('NOTICE: Changing IsProduction value to "true"')
        isProduction.text = 'true'    

    # Set initial platform outer level values
    platform_obj = get_platform_fields(p)
    
    site = p.find('Site')
    add_uuid_to_site(site)

    # Check to see if PlatformSensor has sites
    # This could be an "Actual Site" override with a seperate location
    platform_sensor_sites = p.findall('PlatformSensor/Site')
    ps_sites = []
    for ps_site in platform_sensor_sites:
        print(get_site_fields(ps_site))
        add_uuid_to_site(ps_site)
        ps_sites.append(get_site_fields(ps_site))


    transport_medium = p.find('TransportMedium')
    if transport_medium is not None:
        tm = {}
        tm['mediumtype'] = transport_medium.get('MediumType')
        tm['mediumid'] = transport_medium.get('MediumId')
        platform_obj['transportmedium'] = tm

    config_sensors = p.findall('PlatformConfig/ConfigSensor')
    script_sensors = p.findall('PlatformConfig/DecodesScript/ScriptSensor')
    cfg_sensors = {}
    if config_sensors is not None:
        print('\n*** ConfigSensor ***')
        for cs in config_sensors:
            
            # Get the ScriptSensor for this ConfigSensor
            # to determine the units
            sensor_number = cs.get('SensorNumber')
            print(f'Sensor Number: {sensor_number}')
            
            for ss in script_sensors:
                if ss.get('SensorNumber') == sensor_number:       
                    units = ss.find('UnitConverter').get('ToUnitsAbbr')

            sensor_name = cs.find('SensorName').text.strip()
            print(f'SensorName: {sensor_name}')
            dataTypes = cs.findall('DataType')
            dtypes = {}
            for dt in dataTypes:                
                for name, value in dt.attrib.items():
                    print(f'{dt.tag}: {name} -> {value}')
                    dtypes[name] = value 
                    dtypes['ToUnitsAbbr'] = units            

            cfg_sensors[sensor_name] = dtypes

    
    ## Add the PlatformSensor and PlatformSensorProperty sub elements
    ## which will contain UUIDs to map sensor param/units to MIDAS timeseries
    
    print('\n\n$$$ --------------------- $$$')

    print(f'ConfigSensor Count: {len(config_sensors)}')
    
    platform_sensors = p.findall('PlatformSensor')
    for ps in platform_sensors:
        print(f"PlatformSensor => {ps.get('SensorNumber')}")

    # If no PlatformSensors elements, add empty elements for each config sensor
    if not platform_sensors:
        print('This platform has no PlatformSensor elements')
        for s in range(1, len(config_sensors)+1):
            add_platform_sensor(s, p)
        # Recheck for PlatformSensor nodes
        platform_sensors = p.findall('PlatformSensor')
           
    # Recheck for PlatformSensor nodes
    # platform_sensors = p.findall('PlatformSensor')
    
    # Check number of PlatformSensor elements
    if len(platform_sensors) < len(config_sensors):
        print("PlatformSensor count < ConfigSensor Count")
        # Loop over config sensors to enumerate
        cfg_sensors_numbers = list(range(1, len(config_sensors)+1))
        platform_sensors_numbers = list(range(1, len(platform_sensors)+1))
        for s in cfg_sensors_numbers:
            for ps in platform_sensors:
                print(f"Checking for {s} in {platform_sensors_numbers}")
                if s not in platform_sensors_numbers:                   
                    print(f'adding platform sensor: {s}')
                    add_platform_sensor(s, p)
                    break #without this ducplicated will be added
            

    
    # Recheck for PlatformSensor nodes
    platform_sensors = p.findall('PlatformSensor')

    if len(config_sensors) == len(platform_sensors):
        print("Platform has PlatformSensor count = ConfigSensor Count")
        for ps in platform_sensors:
            add_platform_sensor_uuid_property(ps)

    # Recheck for PlatformSensor nodes
    platform_sensors = p.findall('PlatformSensor')
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    

    # Add the platform sensor to the config sensors dict just to keep these
    # pieces together for the JSON output
    for cs in config_sensors:
        for ps in platform_sensors:
            if cs.get('SensorNumber') == ps.get('SensorNumber'):
                print(f"SENSORS MATCH: {cs.get('SensorNumber')}")
                if ps.find('PlatformSensorProperty') is not None and ps.find('PlatformSensorProperty').get('PropertyName') == 'uuid':
                    print(f"--->{cs.find('SensorName').text}")
                    print(f"==>{ps.find('PlatformSensorProperty').text}")
                    cfg_sensors[cs.find('SensorName').text.strip()]['uuid'] = ps.find('PlatformSensorProperty').text.strip()
        
    


    platform_obj['config_sensors'] = cfg_sensors
    platform_obj['platform_sensors'] = ps_sites
    platform_obj['site'] = get_site_fields(site)   
    platform_obj['id'] = p.get('PlatformId')
    platforms_list.append(platform_obj)

outfile_json = os.path.abspath(os.path.join(script_dir, '..', 'output', 'json', f'{os.path.basename(infile)}'))
outfile_json = outfile_json.replace('.xml', '.json')
print(f'\nSaving json output to: {outfile_json}')
with open(outfile_json, 'w') as json_file:
    json.dump(platforms_list, json_file, indent=4)

print(f'Saving xml output to: {outfile_xml}')
tree.write(outfile_xml,  encoding="utf-8", xml_declaration=True, standalone=True)