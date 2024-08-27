from flask import Flask, request, render_template, Response, jsonify
from flask_openapi import Swagger
from flask_cors import cross_origin, CORS
from modules.logging import log_user_ip, setup_logging
from modules.config import setup_config
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes.templates import templates_bp
from routes.users import users_bp
from routes.streams import streams_bp

# Load configuration and set up logging
config = setup_config()
logger = setup_logging()

# Configuration settings
FLASK_DEBUG = config['DEFAULT']['FLASK_DEBUG']
FLASK_RUN_HOST = config['DEFAULT']['FLASK_RUN_HOST']
FLASK_RUN_PORT = config['DEFAULT']['FLASK_RUN_PORT']
SECRET_KEY = config['DEFAULT']['SECRET_KEY']
TITLE = config['DEFAULT']["TITLE"]
DESCRIPTION = config['DEFAULT']["DESCRIPTION"]

app = Flask(__name__)
app.jinja_env.autoescape = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)

jwt = JWTManager(app)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "openapi",
            "route": "/dev/openapi.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/dev/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/dev/docs/",
    "title": TITLE,
    "description": DESCRIPTION,
    "termsOfService": "/terms",
    "openapi": "3.0.3",
    "version": "1.0.11",
    "swagger_ui_bundle_js": "//petstore.swagger.io/swagger-ui-bundle.js",
    "swagger_ui_standalone_preset_js": "//petstore.swagger.io/swagger-ui-standalone-preset.js",
    "swagger_initializer_js": "//petstore.swagger.io/swagger-initializer.js",
    "jquery_js": "//petstore.swagger.io/jquery.min.js",
    "swagger_ui_css": "//petstore.swagger.io/swagger-ui.css",
    "index_css": "//petstore.swagger.io/index.css",
    "components": {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "in": "header",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config)
app.register_blueprint(templates_bp, url_prefix='/')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(streams_bp, url_prefix='/streams')

@app.route('/')
@cross_origin()
def index():
    user_ip_data = log_user_ip(request)
    return render_template('index.html')

@app.route('/api/')
@cross_origin()
def backend_api():
    user_ip_data = log_user_ip(request)
    response_data = {"message": "whut are you doin here?"}
    return jsonify({"responseData": response_data})

@app.route('/dev/')
@cross_origin()
def backend_dev():
    user_ip_data = log_user_ip(request)
    response_data = {"message": "whut are you doin here?"}
    return jsonify({"responseData": response_data})

@app.route('/dev/docs')
@cross_origin()
def backend_doc():
    user_ip_data = log_user_ip(request)
    response_data = {"message": "whut are you doin here?"}
    return jsonify({"responseData": response_data})

@app.route('/dev/docs/')
@cross_origin()
def backend_docs():
    user_ip_data = log_user_ip(request)
    response_data = {"message": "whut are you doin here?"}
    return jsonify({"responseData": response_data})

@app.route('/robots.txt')
@cross_origin()
def robots_txt():
    robots_txt_content = "User-agent: *\nDisallow: /private/"
    return Response(robots_txt_content, mimetype='text/plain')

@app.errorhandler(404)
@cross_origin()
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
