from datetime import datetime

from Tools.scripts.make_ctype import method
from toolz.curried import reduce

from app.db.database import driver
from app.db.model import Device, Interaction
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
    with driver.session() as session:
        query = """
                MATCH (start:Device)
                MATCH (end:Device)
                WHERE start <> end
                MATCH path = shortestPath((start)-[:CONNECTED*]->(end))
                WHERE ALL(r IN relationships(path) WHERE r.method = 'Bluetooth')
                WITH path, length(path) as pathLength
                ORDER BY pathLength DESC
                LIMIT 1
                RETURN pathLength, nodes(path) AS devices
                """
        result = session.run(query).single()

        if result:
            return {
                "path_length": result["pathLength"],
                "devices": [node["id"] for node in result["devices"]],
            }
        else:
            return None

# finding all devices connected to each other with a signal strength stronger than -60
def get_all_devices_with_signal():
    with driver.session() as session:
        query = """
                        MATCH (start:Device)
                        MATCH (end:Device)
                        WHERE start <> end
                        MATCH path = shortestPath((start)-[:CONNECTED*]->(end))
                        WHERE ALL(r IN relationships(path) WHERE r.signal_strength_dbm > -60)
                        WITH path, length(path) as pathLength
                        ORDER BY pathLength DESC
                        LIMIT 1
                        RETURN nodes(path) AS devices
                        """
        result = session.run(query).single()

        if result:
            return [node["id"] for node in result["devices"]]
        else:
            return None


# count how many devices are connected to a specific device based on a provided ID
def count_devices_connected_to_device(device_id):
    with driver.session() as session:
        respond1 = session.run('''
                    MATCH (d1:Device)-[i:CONNECTED]->(d2:Device)
                    WHERE d1.id = $device_id
                    RETURN count(d2)
                    ''', device_id=device_id).single()
        respond2 = session.run('''
                    MATCH (d1:Device)-[i:CONNECTED]->(d2:Device)
                    WHERE d2.id = $device_id
                    RETURN count(d1)
                    ''', device_id=device_id).single()
        respond = respond1['count(d2)'] + respond2['count(d1)']
        return respond

# determine whether there is a direct connection between two devices.
def is_direct_connection(from_device_id, to_device_id):
    with driver.session() as session:
        respond1 = session.run('''
            MATCH (d1:Device)-[i:CONNECTED]->(d2:Device)
            WHERE d1.id = $from_device_id AND d2.id = $to_device_id
            RETURN i
            ''',
            from_device_id=from_device_id,
            to_device_id=to_device_id).single()
        respond2 = session.run('''
            MATCH (d1:Device)-[i:CONNECTED]->(d2:Device)
            WHERE d1.id = $to_device_id AND d2.id = $from_device_id
            RETURN i
            ''',
            from_device_id=from_device_id,
            to_device_id=to_device_id).single()
        return respond1 is not None or respond2 is not None



# fetch the most recent interaction for a specific device, sorted by timestamp.
def get_most_recent_interaction(device_id):
    with driver.session() as session:
        respond = session.run('''
            MATCH (d:Device {id: $device_id})-[i:CONNECTED]->(other:Device)
            RETURN i, other.id AS to_device
            ORDER BY i.timestamp DESC
            LIMIT 1
            ''',
            device_id=device_id
        )
        record = respond.single()
        respond2 = session.run('''
            MATCH (d:Device {id: $device_id})<-[i:CONNECTED]-(other:Device)
            RETURN i, other.id AS to_device
            ORDER BY i.timestamp DESC
            LIMIT 1
            ''',
            device_id=device_id
        )
        record2 = respond2.single()
        if record is None and record2 is None:
            return
        if record is None:
            final = record2
        elif record2 is None:
            final = record
        else:
            final = record if record['i']['timestamp'] > record2['i']['timestamp'] else record2
        interaction_data = final["i"]  # Get the relationship properties
        return Interaction(
            from_device=device_id,
            to_device=final["to_device"],
            method=interaction_data.get("method", ""),
            bluetooth_version=interaction_data.get("bluetooth_version", ""),
            signal_strength_dbm=interaction_data.get("signal_strength_dbm", 0),
            distance_meters=interaction_data.get("distance_meters", 0.0),
            duration_seconds=interaction_data.get("duration_seconds", 0),
            timestamp=interaction_data.get("timestamp")
        )