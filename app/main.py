from flask import Flask

from app.routes.phone__route import phone_bluprint

app = Flask(__name__)


if __name__ == '__main__':
    app.register_blueprint(phone_bluprint, url_prefix='/api')
    app.run()