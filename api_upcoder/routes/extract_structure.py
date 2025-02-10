from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup
import re

# Créer un Blueprint pour cette route
extract_structure_bp = Blueprint('extract_structure', __name__)

# Regex pour ajouter des marqueurs uniques autour du texte
unique_marker_pattern = re.compile(r"\{\{(\d+)\}\}")

def extract_structure_with_markers(gutenberg_html):
    """
    Extrait la structure HTML/Gutenberg et identifie les parties de texte à générer.
    Ajoute des marqueurs uniques autour de chaque partie de texte.
    """
    soup = BeautifulSoup(gutenberg_html, 'html.parser')
    ignore_tags = {'script', 'style', 'code', 'pre'}
    text_mapping = {}

    # Parcourir tous les éléments contenant du texte
    for element in soup.find_all(string=True):
        if isinstance(element, BeautifulSoup.Comment) or element.parent.name in ignore_tags or not element.strip():
            continue

        original_text = element.strip()
        if original_text:
            # Générer un marqueur unique pour ce texte
            marker = f"{{{{ {len(text_mapping)} }}}}"
            text_mapping[marker] = original_text
            # Remplacer le texte par le marqueur dans la structure
            element.replace_with(marker)

    # Retourner la structure modifiée et la correspondance texte/marqueurs
    return str(soup), text_mapping


# Route : Extraire la structure HTML/Gutenberg
@extract_structure_bp.route('/extract-structure', methods=['POST'])
def extract_structure():
    if not request.json or 'gutenberg' not in request.json:
        return jsonify({'error': 'Données manquantes'}), 400

    gutenberg_html = request.json['gutenberg']
    structured_html, text_mapping = extract_structure_with_markers(gutenberg_html)

    return jsonify({
        'structured_html': structured_html,
        'text_mapping': text_mapping
    })


def reinject_text_into_gutenberg(structured_html, modified_texts):
    """
    Réinjecte le texte modifié dans la structure HTML/Gutenberg.
    """
    soup = BeautifulSoup(structured_html, 'html.parser')

    # Créer une liste des marqueurs présents dans la structure
    markers_in_html = unique_marker_pattern.findall(structured_html)

    # Vérifier que le nombre de marqueurs correspond au nombre de textes modifiés
    if len(markers_in_html) != len(modified_texts):
        raise ValueError("Le nombre de textes modifiés ne correspond pas aux marqueurs dans la structure.")

    # Créer un mapping entre les marqueurs et les textes modifiés
    text_mapping = {f"{{{{ {i} }}}}" : modified_texts[i] for i in range(len(modified_texts))}

    # Remplacer les marqueurs par les textes modifiés
    for element in soup.find_all(string=unique_marker_pattern):
        marker = element.strip()
        if marker in text_mapping:
            element.replace_with(BeautifulSoup(text_mapping[marker], 'html.parser'))

    # Retourner le HTML final
    return str(soup)


# Route : Réinjecter le texte dans la structure HTML/Gutenberg
@extract_structure_bp.route('/reinject-text', methods=['POST'])
def reinject_text():
    if not request.json or 'structured_html' not in request.json or 'modified_texts' not in request.json:
        return jsonify({'error': 'Données manquantes'}), 400

    structured_html = request.json['structured_html']
    modified_texts = request.json['modified_texts']

    try:
        final_html = reinject_text_into_gutenberg(structured_html, modified_texts)
        return jsonify({'gutenberg': final_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500