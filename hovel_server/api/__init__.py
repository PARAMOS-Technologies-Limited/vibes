from .status import status_bp
from .branch import branch_bp

def register_blueprints(app):
    app.register_blueprint(status_bp)
    app.register_blueprint(branch_bp) 