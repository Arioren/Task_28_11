from flask import Flask

app = Flask(__name__)


if __name__ == '__main__':
    app.register_blueprint(api, url_prefix='/api')
    app.run()