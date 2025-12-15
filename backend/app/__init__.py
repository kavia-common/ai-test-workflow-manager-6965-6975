from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
import logging

from .routes.health import blp as health_blp
from .routes.suites import blp as suites_blp

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configure logger
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# CORS for local dev preview; restrict to frontend origin on port 3000
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://localhost:3000"]}})

# OpenAPI/Swagger configuration
app.config["API_TITLE"] = "AI Test Workflow Manager API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Optional: Tag descriptions for better grouping
openapi_tags = [
    {"name": "Health", "description": "Health check route"},
    {"name": "Suites", "description": "CRUD operations for test suites and AI suggestions"},
]
app.config["OPENAPI_TAGS"] = openapi_tags

api = Api(app)

# Basic error handlers for consistent JSON responses
@app.errorhandler(400)
def bad_request(err):
    msg = getattr(err, "description", "Bad Request")
    payload = msg if isinstance(msg, dict) else {"message": str(msg)}
    return jsonify(payload), 400

@app.errorhandler(404)
def not_found(err):
    msg = getattr(err, "description", "Not Found")
    payload = msg if isinstance(msg, dict) else {"message": str(msg)}
    return jsonify(payload), 404

@app.errorhandler(500)
def internal_error(err):
    app.logger.exception("Internal server error: %s", err)
    return jsonify({"message": "Internal server error"}), 500

# Register blueprints
api.register_blueprint(health_blp)
api.register_blueprint(suites_blp)
