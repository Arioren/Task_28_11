from flask import Blueprint, request
import app.repository.phone_repository as repo

phone_bluprint = Blueprint('phone', __name__)

@phone_bluprint.route('/phone_tracker', methods=['POST'])
def get_interaction():
    respond = request.json
    print(respond)
    repo.get_data(respond)