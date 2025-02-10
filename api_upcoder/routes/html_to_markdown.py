from flask import Blueprint, request, jsonify
import html2text

# Créer un Blueprint pour cette route
html_to_markdown_bp = Blueprint('html_to_markdown', __name__)

# Route : Convertir HTML en Markdown
@html_to_markdown_bp.route('/html-to-markdown', methods=['POST'])
def html_to_markdown():
    if not request.json or 'html' not in request.json:
        return jsonify({'error': 'Données manquantes'}), 400

    html_content = request.json['html']
    h = html2text.HTML2Text()
    markdown_content = h.handle(html_content)

    return jsonify({'markdown': markdown_content})