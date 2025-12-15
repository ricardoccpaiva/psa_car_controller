"""
Modern Flask REST API Server for PSA Car Controller
Serves SvelteKit frontend and provides REST API endpoints
"""
import logging
import sys
from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS
from werkzeug import run_simple

from psa_car_controller.common.mylogger import file_handler

if sys.version_info >= (3, 8):
    import importlib
else:
    import importlib_metadata as importlib

# pylint: disable=invalid-name
app = None
logger = logging.getLogger(__name__)


def create_app(debug: bool = False):
    """Create and configure the Flask application"""
    global app

    # Create Flask app
    app = Flask(__name__,
                static_folder='../../frontend/build',
                static_url_path='')

    app.config["DEBUG"] = debug
    app.logger.addHandler(file_handler)

    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/get_*": {"origins": "*"},
        r"/charge*": {"origins": "*"},
        r"/wakeup/*": {"origins": "*"},
        r"/preconditioning/*": {"origins": "*"},
        r"/position/*": {"origins": "*"},
        r"/positions": {"origins": "*"},
        r"/abrp": {"origins": "*"},
        r"/horn/*": {"origins": "*"},
        r"/lights/*": {"origins": "*"},
        r"/lock_door/*": {"origins": "*"},
        r"/settings*": {"origins": "*"},
        r"/vehicles/*": {"origins": "*"},
        r"/battery/*": {"origins": "*"},
        r"/style.json": {"origins": "*"}
    })

    # Import API routes
    # This will register all the @app.route decorators
    importlib.import_module('psa_car_controller.web.view.api')

    # Serve SvelteKit app
    @app.route('/')
    def serve_app():
        """Serve the main SvelteKit app"""
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files or fallback to index.html for SPA routing"""
        file_path = Path(app.static_folder) / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(app.static_folder, path)
        else:
            # Fallback to index.html for client-side routing
            return send_from_directory(app.static_folder, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors by serving the SPA"""
        return send_from_directory(app.static_folder, 'index.html')

    return app


def start_app(title=None, base_path="/", debug: bool = False,
              host="127.0.0.1", port=5000, reloader=False, **kwargs):
    """Start the Flask application"""
    app = create_app(debug=debug)

    logger.info(f"Starting PSA Car Controller on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Frontend: SvelteKit")
    logger.info(f"API: REST endpoints available")

    run_simple(
        hostname=host,
        port=port,
        application=app,
        use_reloader=reloader,
        use_debugger=debug
    )


# Backwards compatibility
def config_flask(title=None, base_path="/", debug: bool = False,
                host="127.0.0.1", port=5000, reloader=False, **kwargs):
    """
    Legacy config function for backwards compatibility
    Returns config dict for run_simple
    """
    app = create_app(debug=debug)

    return {
        "hostname": host,
        "port": port,
        "application": app,
        "use_reloader": reloader,
        "use_debugger": debug
    }


def run(config):
    """Run the application with given config"""
    return run_simple(**config)
