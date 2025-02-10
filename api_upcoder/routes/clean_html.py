from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup

# Créer un Blueprint pour cette route
clean_html_bp = Blueprint('clean_html', __name__)

# Route : Nettoyer le HTML
@clean_html_bp.route('/clean-html', methods=['POST'])
def clean_html():
    try:
        # Vérifier si les données JSON sont présentes
        if not request.is_json or 'html' not in request.json:
            return jsonify({'error': 'Données manquantes ou invalides'}), 400

        # Récupérer le contenu HTML
        raw_html = request.json['html']
        print(f"Raw HTML reçu : {raw_html}")  # Message de debug

        # Nettoyer le HTML avec BeautifulSoup
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Supprimer les balises script et style
        for tag in soup(['script', 'style']):
            tag.decompose()

        # Normaliser le contenu
        cleaned_html = soup.prettify()
        print(f"HTML nettoyé : {cleaned_html}")  # Message de debug

        return jsonify({'cleaned_html': cleaned_html})

    except Exception as e:
        # Retourner une erreur avec un message détaillé
        return jsonify({'error': str(e)}), 500