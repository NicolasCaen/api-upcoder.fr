from flask import Blueprint, request, jsonify
import markdown

# Créer un Blueprint pour cette route
markdown_to_gutenberg_bp = Blueprint('markdown_to_gutenberg', __name__)

# Route : Convertir Markdown en Gutenberg
@markdown_to_gutenberg_bp.route('/markdown-to-gutenberg', methods=['POST'])
def markdown_to_gutenberg():
    if not request.json or 'markdown' not in request.json:
        return jsonify({'error': 'Données manquantes'}), 400

    markdown_content = request.json['markdown']
    html_content = markdown.markdown(markdown_content)

    gutenberg_block = f"""
    <!-- wp:custom-block -->
    <div class="wp-block-custom-block">
        {html_content}
    </div>
    <!-- /wp:custom-block -->
    """

    return jsonify({'gutenberg': gutenberg_block})