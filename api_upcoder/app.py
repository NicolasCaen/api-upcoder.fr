from flask import Flask
from flask_cors import CORS  # Gestion des politiques CORS

# Initialiser l'application Flask
app = Flask(__name__)

# Activer CORS pour toutes les origines
CORS(app, resources={r"/*": {"origins": "*"}})

# Importer et enregistrer les Blueprints
from routes.html_to_markdown import html_to_markdown_bp
from routes.markdown_to_gutenberg import markdown_to_gutenberg_bp
from routes.get_routes import get_routes_bp
from routes.clean_html import clean_html_bp
from routes.markdown_to_html import markdown_to_html_bp
from routes.generate_lorem_ipsum import generate_lorem_ipsum_bp
from routes.ai_content_generator import ai_content_generator_bp
from routes.extract_structure import extract_structure_bp  # Nouveau Blueprint


app.register_blueprint(extract_structure_bp)  # Enregistrer la nouvelle route
app.register_blueprint(html_to_markdown_bp)
app.register_blueprint(markdown_to_gutenberg_bp)
app.register_blueprint(get_routes_bp)
app.register_blueprint(clean_html_bp)
app.register_blueprint(markdown_to_html_bp)
app.register_blueprint(generate_lorem_ipsum_bp)
app.register_blueprint(ai_content_generator_bp)

if __name__ == '__main__':
    app.run()