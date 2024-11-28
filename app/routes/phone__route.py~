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
        data = {
            'first_device': {'device': Device(**first_device),
                             'location': Location(**respond['devices'][0]['location'])},
            'second_device': {'device': Device(**second_device),
                             'location': Location(**respond['devices'][0]['location'])},
            'interaction': Interaction(**respond['interaction'])
        }
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