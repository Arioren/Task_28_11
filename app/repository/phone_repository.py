from Tools.scripts.make_ctype import method
from toolz.curried import reduce

from app.db.database import driver
from app.db.model import Device
from app.repository.device_repo import create_device_repo


def get_data(data: dict):
    first_device = data['first_device']['device']
    first_location = data['first_device']['location']
    second_device = data['second_device']['device']
    second_location = data['second_device']['location']
    interaction = data['interaction']

    create_device_repo(first_device, first_location)
    create_device_repo(second_device, second_location)

    with driver.session() as session:
        session.run('''
            MATCH (d1:Device), (d2:Device)
            WHERE d1.id = $from_device_id AND d2.id = $to_device_id
            MERGE (d1)-[i:CONNECTED{
                method: $method,
                bluetooth_version: $bluetooth_version,
                signal_strength_dbm: $signal_strength_dbm,
                distance_meters: $distance_meters,
                duration_seconds: $duration_seconds,
                timestamp: $timestamp}]->(d2)
            ''',
            from_device_id=interaction.from_device,
            to_device_id=interaction.to_device,
            method=interaction.method,
            bluetooth_version=interaction.bluetooth_version,
            signal_strength_dbm=interaction.signal_strength_dbm,
            distance_meters=interaction.distance_meters,
            duration_seconds=interaction.duration_seconds,
            timestamp=interaction.timestamp)

#finding all devices connected to each other using the Bluetooth method, and how long is the path.
def get_all_devices_connected():
    query = '''
    MATCH (d1:Device)-[i:CONNECTED]->(d2:Device) RETURN d1, d2
    '''

# finding all devices connected to each other with a signal strength stronger than -60
def get_all_devices_with_signal():
    query = '''
    MATCH (d1:Device)-[i:CONNECTED]->(d2:Device)
    WHERE i.signal_strength_dbm > -60
    RETURN d1, d2
    '''
    with driver.session() as session:
        respond = session.run(query).data()
        respond = reduce(lambda x, y: x + [Device(**y['d1']), Device(**y['d2'])], respond, [])
        result = []
        for device in respond:
            if all(device.id != d.id for d in result):
                result.append(device)
        return result