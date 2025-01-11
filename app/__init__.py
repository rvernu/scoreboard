from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    with app.app_context():
        # Import and register blueprints
        from .routes import main
        from .route.data import data_route
        app.register_blueprint(main)
        app.register_blueprint(data_route)

    return app
