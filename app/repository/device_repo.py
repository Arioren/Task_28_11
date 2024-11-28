from app.db.database import driver
from app.db.model import Device


def create_device_repo(device: Device, location):
    with driver.session() as session:
        res = session.run('''
        MATCH (d:Device {id: $id})
        RETURN d
        ''',
        id=device.id)
        if res.single() is not None:
            return
        session.run('''
            CREATE (d:Device {id: $id,
                brand: $brand,
                model: $model,
                os: $os,
                name: $name})
            CREATE (l:Location {
                latitude: $latitude,
                longitude: $longitude,
                altitude_meters: $altitude_meters,
                accuracy_meters: $accuracy_meters})
            CREATE (l)-[:LOCATION]->(d)
            ''',
            id=device.id,
            brand=device.brand,
            model=device.model,
            os=device.os,
            name=device.name,
            latitude=location.latitude,
            longitude=location.longitude,
            altitude_meters=location.altitude_meters,
            accuracy_meters=location.accuracy_meters)