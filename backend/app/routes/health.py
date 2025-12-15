from flask_smorest import Blueprint
from flask.views import MethodView

# Fix tag/name typos for better OpenAPI output
blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")

@blp.route("/", methods=["GET"])
class HealthCheck(MethodView):
    def get(self):
        """Return a simple health response."""
        return {"message": "Healthy"}
