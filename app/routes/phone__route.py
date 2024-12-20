from datetime import datetime

from flask import Blueprint, request, jsonify
import app.repository.phone_repository as repo
from app.db.model import Device, Interaction, Location

phone_bluprint = Blueprint('phone', __name__)

@phone_bluprint.route('/phone_tracker', methods=['POST'])
def get_interaction():
    try:
        respond:dict = request.json
    except Exception as e:
        return jsonify({'error':'not json'}), 400
    try:
        first_device = {**respond['devices'][0]}
        del first_device['location']
        second_device = {**respond['devices'][1]}
        del second_device['location']
        respond['interaction']['timestamp'] = datetime.strptime(respond['interaction']['timestamp'], "%Y-%m-%dT%H:%M:%S")
        data = {
            'first_device': {'device': Device(**first_device),
                             'location': Location(**respond['devices'][0]['location'])},
            'second_device': {'device': Device(**second_device),
                             'location': Location(**respond['devices'][0]['location'])},
            'interaction': Interaction(**respond['interaction'])
        }
        if data['first_device']['device'].id == data['second_device']['device'].id:
            raise
    except Exception as e:
        return jsonify({'error': 'bad data'}), 400
    try:
        repo.get_data(data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@phone_bluprint.route('/phone_tracker', methods=['GET'])
def get_all_devices_connected():
    respond = repo.get_all_devices_connected()
    return jsonify(respond), 200


@phone_bluprint.route('/phone_tracker/signal', methods=['GET'])
def get_all_devices_with_signal():
    respond = repo.get_all_devices_with_signal()
    return jsonify(respond), 200


@phone_bluprint.route('/phone_tracker/body/<device_id>', methods=['GET'])
def count_devices_connected_to_device(device_id):
    respond = repo.count_devices_connected_to_device(device_id)
    return jsonify(respond), 200

@phone_bluprint.route('/phone_tracker/body/<string:device_id>/<string:device_id2>', methods=['GET'])
def is_connected(device_id, device_id2):
    respond = repo.is_direct_connection(device_id, device_id2)
    return jsonify(respond), 200


@phone_bluprint.route('/phone_tracker/interaction/<string:device_id>', methods=['GET'])
def get_all_interactions(device_id):
    respond = repo.get_most_recent_interaction(device_id)
    if respond is None:
        return jsonify({'error': 'no interactions'}), 400
    respond.timestamp = respond.timestamp.isoformat()
    return jsonify(respond), 200