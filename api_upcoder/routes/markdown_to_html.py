from flask import Blueprint, request, jsonify
import markdown

# Créer un Blueprint pour cette route
markdown_to_html_bp = Blueprint('markdown_to_html', __name__)

# Route : Convertir Markdown en HTML
@markdown_to_html_bp.route('/markdown-to-html', methods=['POST'])
def markdown_to_html():
    # Vérifier si les données JSON sont présentes et contiennent une clé 'markdown'
    if not request.is_json or 'markdown' not in request.json:
        return jsonify({'error': 'Données manquantes ou invalides'}), 400

    # Récupérer le contenu Markdown
    raw_markdown = request.json['markdown']

    # Convertir Markdown en HTML
    html_content = markdown.markdown(raw_markdown)

    return jsonify({'html': html_content})