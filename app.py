from flask import Flask

from Colas.routes import queues_bp
from Pilas.routes import stacks_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app.register_blueprint(stacks_bp)
    app.register_blueprint(queues_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
