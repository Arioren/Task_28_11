from app.db.database import driver
from app.db.model import Device


def create_device_repo(device: Device, location):
    with driver.session() as session:
        session.run('''
            CREATE (d:Device {id: $id,
                brand: $brand,
                model: $model,
                os: $os})
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
            latitude=location.latitude,
            longitude=location.longitude,
            altitude_meters=location.altitude_meters,
            accuracy_meters=location.accuracy_meters)