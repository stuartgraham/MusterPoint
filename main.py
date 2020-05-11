#
# Title : MusterPoint Assignment
# Author : Stuart Graham
# Git : https://github.com/stuartgraham/MusterPoint
#
# Standard Python library imports, this is 3rd party code
from random import randrange, choice
from time import sleep
# pip install tinydb
# Used to managed small noSQL database, this is 3rd party code
# https://pypi.org/project/tinydb/
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
# pip install tabulate
# Used to managed small noSQL database, this is 3rd party code
# https://pypi.org/project/tabulate/
from tabulate import tabulate

# Base Data - Do not delete or edit
BASE_ZONE = [{'name':'Zone0', 'cctv_sensorid' : 'XXX000', 'door_sensorid' : 'XXX000'}]
BASE_USER = [{'name':'Unknown', 'badge_id' : '0000000', 'face_coords' : '000,000'}]


# Test base Zone data - Can be editted
TEST_ZONES = [{'name':'Zone1', 'cctv_sensorid' : 'ABC123', 'door_sensorid' : 'ABC123'},
         {'name':'Zone2', 'cctv_sensorid' : 'DEF456', 'door_sensorid' : 'DEF456'},
         {'name':'Zone3', 'cctv_sensorid' : 'XYZ789', 'door_sensorid' : 'XYZ789'}]

# Test base Users data - Can be editted
TEST_USERS = [{'name':'Alice', 'badge_id' : 'ABC', 'face_coords' : '123,123'},
         {'name':'Bob', 'badge_id' : 'DEF', 'face_coords' : '456,456'},
         {'name':'Charlie', 'badge_id' : 'XYZ', 'face_coords' : '789,789'}]

# If test data exists use instead of base
try:
    TEST_ZONES
except NameError:
    ZONES = BASE_ZONE
else:
    ZONES = TEST_ZONES

try:
    TEST_USERS
except NameError:
    USERS = BASE_USER
else:
    USERS = TEST_USERS

# Variable for test runs for testing personnel test activity
TEST_RUNS = 20

class ZoneRegister:
    ''' Rolls up LiveZones and becomes a master register for reading by safety superintendents '''
    
    def __init__(self, zones):
        self.registers = zones

    def update_all_zones(self, zone, who_is_it, action):
        ''' Entry point to remove last known activity from other zones'''
        for i in self.registers:
            # Do not delete the affirming zone registration
            if i.name == zone:
                continue
            # Search LiveZone in-memory database for activity to remove
            db = i.register
            query = Query()
            # Removes all record of user from zones
            if action == 'remove_user_records_from_zones':
                if not db.search(query.name == who_is_it) == []:
                    db.remove(query.name == who_is_it)
                    print('ZONE: {} removed from {}'.format(who_is_it, i.name))
            # Removes lastknown state of user from zones
            if action == 'remove_user_lastknown_from_zones':
                if not db.search(query.name == who_is_it) == []:
                    db.update({'lastknown': ''},query.name == who_is_it)
                    print('ZONE: Activity removed from {} for user {}'.format(i.name, who_is_it))
    
    def read_register(self):
        ''' Read current register state '''
        print('-'* 37)
        print('| ZONE REGISTER                      |')
        print('-'* 37)
        table = []
        for i in self.registers:
                db = i.register
                for row in db:
                    table.append([i.name, row['name'], row['door'], row['cctv']])
        print(tabulate(table, headers=['Zone', 'Name', 'Door', 'CCTV'], tablefmt='orgtbl'))
        print('-'* 37)
        # Insert interface to callback register output to UI 

class MusterRegister():
    ''' Takes a snapshot of LiveZones on instantiation, compiles zone details to in memory database register to allow for manipulation'''
    
    def __init__(self, zones, alarm_zone, alarm_description):
        self.alarm_zone = alarm_zone
        self.alarm_description = alarm_description
        self.register = TinyDB(storage=MemoryStorage)
        # Collapse LiveZone data to single database entity and extend schema for CheckedIn state
        db = self.register
        for i in zones:
            for row in i.register:
                db.insert({'zone': i.name, 'name' : row['name'], 'cctv' : row['door'], 'door' : row['cctv'], 'lastknown' : row['lastknown'], 'checkedin' : 'False'})

    def read_register(self):
        ''' Read current register state with 2 views - unaccounted and accounted for personnel'''
        print('-'* 67)
        print(' MUSTER REGISTER - ALARM IN : {} TYPE : {}'.format(self.alarm_zone, self.alarm_description))
        print('-'* 67)
        table_unaccounted = []
        db = self.register
        for row in db:
            # Only add rows for those not unaccounted for 
            if row['checkedin'] == 'False':
                table_unaccounted.append([row['zone'], row['name'], row['door'], row['cctv'], row['lastknown'], row['checkedin']])
        print(tabulate(table_unaccounted, headers=['Zone', 'Name', 'Door', 'CCTV', 'Last Known', 'Checked-In'], tablefmt='orgtbl'))
        print('-'* 67)
        print(' ACCOUNTED FOR ')
        print('-'* 67)
        table_accounted = []
        db = self.register
        for row in db:
            # Only add rows for those not accounted for 
            if row['checkedin'] == 'True':
                table_accounted.append(row['name'])
        # Remove duplicates as the we have them accounted for at muster
        table_accounted = list(dict.fromkeys(table_accounted))
        temp_table = []
        for i in table_accounted:
            temp_table.append([i, 'True'])
        table_accounted = temp_table
        # Add a placeholder if array empty
        if table_accounted == []:
            table_accounted.append(['None', 'N/A'])
        print(tabulate(table_accounted, headers=['Name', 'Checked-In'], tablefmt='orgtbl'))
        print('-'* 25)

    def user_check_in(self, user):
        ''' Checks in user when accounted for an update muster register '''
        db = self.register
        query = Query()
        db.update({'checkedin': 'True'}, query.name == user)
        self.read_register()

class LiveZone:
    ''' LiveZone is an activated Zone with active sensor objects '''
    
    def __init__(self, name, door_sensor, cctv_sensor):
        self.name = name
        self.door_sensor = door_sensor
        self.cctv_sensor = cctv_sensor
        self.register = TinyDB(storage=MemoryStorage)

    def add_user_to_zone(self, zone, who_is_it, sensor_type):
        ''' Add user to zone when directed by sensor'''
        db = self.register
        query = Query()
        # If no entries in zone found for use then gracefully add one
        if db.search(query.name == who_is_it) == []:
            print('DATA: No record found')
            db.insert({'name': who_is_it, 'cctv' : 'False', 'door' : 'False', 'lastknown': ''})
            print('DATA: Inserted record for', who_is_it)
        # Else update existing record
        else:
            print('DATA: Found record for', who_is_it)
        db.update({sensor_type: 'True', 'lastknown': zone}, query.name == who_is_it)
        print('DATA: Updated record for', who_is_it)
        # Post update, check if the user is double confirmed in zone
        self.confirm_user_state(who_is_it, zone)
        print('#'*80)

    def confirm_user_state(self, who_is_it, zone):
        ''' Check if user is confirmed on both sensors in zone, tell other zones to delete if so '''
        db = self.register
        query = Query()
        record = db.search(query.name == who_is_it)
        print('DATA: Output all', record)
        # Initiate double confirm if both sensors are true
        if record[0]['cctv'] == 'True' and record[0]['door'] == 'True':
            print('ZONE: User is double confirmed, tell other zones to delete')
            live_register.update_all_zones(zone, who_is_it, 'remove_user_records_from_zones')
        # Initiate last known activity on single sensor activity
        else:
            live_register.update_all_zones(zone, who_is_it, 'remove_user_lastknown_from_zones')
            print('ZONE: Keep in zone')
           
class BaseSensor:   
    ''' Base sensor class for capturing common functions '''
    
    def test_sensor(self, sensor_type='cctv'):
        ''' Used to test the sensor object is working '''
        if sensor_type == 'cctv':
            print('SNSR: CCTV Sensor is working')
        if sensor_type == 'door':
            print('SNSR: Door Sensor is working')

    def assert_id(self, id, lookup='face'):
        ''' Function will attempt to assert the user from incoming id and Lookup type '''
        # Iterate across active_users to attempt to validate
        for i in active_users:
            # Select lookup type
            if lookup == 'badge':
                if id == i.badge_id:
                    return i.name
            if lookup == 'face':
                if id == i.face_coords:
                    return i.name
        # If lookup cannot find match
        return 'Unknown'

class CCTVSensor(BaseSensor):
    ''' CCTVSensor, child of BaseSensor will emit face co-ordinates of personnel passing in front of it'''
    
    def __init__(self, identity='', zone='', *args):
        self.name = 'CCTV' + '-' + str(zone) + '-' + str(identity)
        self.id = str(identity)
        self.zone = str(zone)
        self.sensor_type = 'cctv'

    def input_jpg(self, facecoord):
        ''' Takes emitted face coordinates and will attempt to ascertain who user is from active User objects, 
        then add it to appropriate zone'''
        who_is_it = self.assert_id(facecoord, 'face')
        print('SNSR: {} sensor : {}'.format(self.zone, self.name))
        print('SNSR: Face ID ({}) observed, identified as {}'.format(facecoord, who_is_it))
        # If ID is unknown print line break and move on
        if who_is_it == 'Unknown':
            print('#'*80)
        else:
        # Look across the active LiveZones objects to pass mesages to correct LiveZone object
            for i in live_zones:
                if i.name == self.zone:
                    i.add_user_to_zone(self.zone, who_is_it, self.sensor_type)

class DoorSensor(BaseSensor):
    ''' DoorSensor, child of BaseSensor will emit badge ID of personnel swiping badge on door sensor'''

    def __init__(self, identity='', zone='', *args):
        self.name = 'DOOR' + '-' + str(zone) + '-' + str(identity)
        self.id = str(identity)
        self.zone = str(zone)
        self.sensor_type = 'door'

    def input_badge_id(self, badge_id):
        ''' Takes emitted badge ID and will attempt to ascertain who user is from active User objects, 
        then add it to appropriate zone'''
        who_is_it = self.assert_id(badge_id, 'badge')
        print('SNSR: {} sensor : {}'.format(self.zone, self.name))
        print('SNSR: Badge ID ({}) swiped, identified as {}'.format(badge_id, who_is_it))
        # If ID is unknown print line break and move on
        if who_is_it == 'Unknown':
            # Insert interface to physical door sensor to deny access
            print('#'*80)
        else:
        # Look across the active LiveZones objects to pass mesages to correct LiveZone object
            for i in live_zones:
                if i.name == self.zone:
                    i.add_user_to_zone(self.zone, who_is_it, self.sensor_type)
            # Insert interface to physical door sensor to allow access        

class Zone:
    ''' Zone Class represents facility zone complete with sensors'''
    def __init__(self, name='', cctv_sensorid='', door_sensorid=''):
        self.name = name
        self.cctv_sensorid = cctv_sensorid
        self.door_sensorid = door_sensorid

class User:
    ''' User Class represents facility personnel'''
    def __init__(self, name='', badge_id='', facecoord=''):
        self.name = name
        self.badge_id = badge_id
        self.face_coords = facecoord

# Initialisation functions
def initialise_zones(zones):
    '''Instantiate some user objects'''
    active_zones = []
    for i in zones:
        active_zone = Zone(i['name'], i['cctv_sensorid'], i['door_sensorid'])
        active_zones.append(active_zone)
    return active_zones

def initialise_users(users):
    '''Instantiate some user objects'''
    active_users = []
    for i in users:
        active_user = User(i['name'], i['badge_id'], i['face_coords'])
        active_users.append(active_user)
    return active_users

def initialise_sensors(zones):
    '''Instantiate sensors'''
    new_live_zones = []
    for i in zones:
        door_obj = DoorSensor(i.door_sensorid, i.name)
        cctv_obj = CCTVSensor(i.cctv_sensorid, i.name)
        new_live_zones.append(LiveZone(i.name, door_obj, cctv_obj))
    return new_live_zones

# Interfaces functions for UI
def alarm_triggered(zone, alarm):
    ''' Interface from alarm system to trigger alarm''' 
    live_muster_register = MusterRegister(live_zones, zone, alarm)
    live_muster_register.read_register()
    # Insert interface to alarm system that muster register was created
    return live_muster_register

def add_new_user(name, badge_id, face_coords):
    ''' Interface to add new user'''
    new_user = User(name, badge_id, face_coords)
    active_users.append(new_user)
    # Insert interface to UI that user was created

def add_new_zone(name, cctv_sensorid, door_sensorid):
    ''' Interface to add new user'''
    new_zone = Zone(name, cctv_sensorid, door_sensorid)
    active_zones.append(new_zone)
    new_zones = [new_zone]
    new_live_zones = initialise_sensors(new_zones)
    for i in new_live_zones:
        live_register.registers.append(i)
    # Insert interface to UI that zone was created

# Test functions for simulating personnel activity
def test_personnel_activity(tests):
    ''' Simulates random personnel activity on the active sensors '''
    runs = 1 
    while runs < tests:
        # Picks random user and zone
        rand_zone = randrange(len(live_zones))
        test_zone = live_zones[rand_zone]
        rand_user = randrange(len(active_users))
        test_user = active_users[rand_user]
        # Picks random sensor choice
        test_sensor_type = choice(['cctv', 'badge'])
        # Selects incorrect_data entry 20% basis
        test_type = choice(['real_data', 'real_data', 'real_data', 'real_data', 'incorrect_data'])
        # Execute test
        if test_sensor_type == 'cctv':
            working_sensor = test_zone.cctv_sensor
            if test_type == 'incorrect_data':
                working_sensor.input_jpg('99999999999999')
            else: 
                working_sensor.input_jpg(test_user.face_coords)
        if test_sensor_type == 'badge':
            working_sensor = test_zone.door_sensor
            if test_type == 'incorrect_data':
                working_sensor.input_badge_id('99999999999999')
            else:
                working_sensor.input_badge_id(test_user.badge_id)
        sleep(1)
        runs += 1

def main():
    ''' Main entry point of the app '''
    # Initialise Zones and Users
    global active_zones
    active_zones = initialise_zones(ZONES)
    global active_users
    active_users = initialise_users(USERS)
    global live_zones
    live_zones = initialise_sensors(active_zones)
    global live_register
    live_register = ZoneRegister(live_zones)

    # Test Data - Simulated system activity
    # Simulate personnel stimulating the sensors
    print('###########################################')
    print('# START TEST PERSONNEL ACTIVITY           #')
    print('###########################################')
    test_personnel_activity(TEST_RUNS)
    # Simulate adding new user and zone
    print('###########################################')
    print('# Add Test User Dan & Zone4            #')
    add_new_user('Dan','ASDG','233,234')
    add_new_zone('Zone4', 'SDF323', 'DFS342')
    # Simulate system wait
    sleep(5)
    # Simulate personel stimulating the sensors
    print('###########################################')
    print('# START TEST PERSONNEL ACTIVITY           #')
    print('###########################################')
    test_personnel_activity(TEST_RUNS)
    # Simulate system wait
    sleep(5)
    # Simulate Superintendent viewing zone register
    print('###########################################')
    print('# VIEW CURRENT REGISTER                   #')
    print('###########################################')
    live_register.read_register()
    # Simulate system wait
    sleep(5)
    # Simulate alarm being fired from Zone3
    print('###########################################')
    print('# ALARM TRIGGER                           #')
    print('###########################################')
    alarm_test_register = alarm_triggered('Zone3','FireAlarm')
    # Simulate system wait
    sleep(5)
    # Simulate check in of Alice and Charle by safety superintendent
    print('###########################################')
    print('# MUSTER CHECKIN - ALICE                  #')
    print('###########################################')
    alarm_test_register.user_check_in('Alice')
    # Simulate system wait
    sleep(5)
    print('###########################################')
    print('# MUSTER CHECKIN - CHARLIE                #')
    print('###########################################')
    alarm_test_register.user_check_in('Charlie')
    # Simulate system wait
    sleep(5)
    print('###########################################')
    print('# TESTING COMPLETE                        #')
    print('###########################################')
    print(' ')
    print('###########################################')
    print('# SYSTEM OK - LISTENING                   #')
    print('###########################################')
    # Simulate listener
    sleep(9999999999999)
 
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()