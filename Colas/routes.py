from flask import Blueprint, render_template

queues_bp = Blueprint("queues", __name__, url_prefix="/queues")


@queues_bp.get("/")
def queues_page():
    """Render the queues module placeholder."""
    return render_template("queues/index.html")
