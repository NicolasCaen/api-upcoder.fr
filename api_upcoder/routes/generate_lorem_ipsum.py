from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup, Comment
import random

generate_lorem_ipsum_bp = Blueprint('generate_lorem_ipsum', __name__)

def get_lorem_words():
    """Retourne une liste de mots Lorem Ipsum."""
    lorem = (
        "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor "
        "incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis "
        "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat "
        "duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore "
        "eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt "
        "in culpa qui officia deserunt mollit anim id est laborum"
    )
    return lorem.split()

def generate_lorem_ipsum_by_length(target_length):
    """
    Génère du Lorem Ipsum avec une longueur approximative spécifiée.
    
    Args:
        target_length (int): Longueur cible en caractères
    
    Returns:
        str: Texte Lorem Ipsum de longueur similaire
    """
    words = get_lorem_words()
    result = []
    current_length = 0
    
    # Ajuster pour la ponctuation et les espaces
    target_length = max(target_length - 20, 10)  # Minimum 10 caractères
    
    while current_length < target_length:
        word = random.choice(words)
        result.append(word)
        current_length += len(word) + 1  # +1 pour l'espace
    
    # Ajouter la ponctuation et les majuscules
    text = ' '.join(result)
    sentences = text.capitalize().split('  ')
    formatted_sentences = [s.strip() + '.' for s in sentences]
    
    return ' '.join(formatted_sentences)

def replace_text_with_lorem_ipsum(html_content):
    """
    Remplace tout le texte visible dans le HTML par du Lorem Ipsum,
    en conservant la structure et une longueur similaire.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    for element in soup.find_all(string=True):
        if isinstance(element, Comment):
            continue
        
        text = element.strip()
        if text and not element.parent.name in ['script', 'style']:
            # Générer du Lorem Ipsum de longueur similaire
            original_length = len(text)
            new_text = generate_lorem_ipsum_by_length(original_length)
            element.replace_with(new_text)

    return str(soup)

@generate_lorem_ipsum_bp.route('/generate-lorem-ipsum', methods=['POST'])
def generate_lorem_ipsum_route():
    try:
        if not request.is_json or ('html' not in request.json and 'gutenberg' not in request.json):
            return jsonify({'error': 'Données manquantes ou invalides'}), 400

        content_key = 'html' if 'html' in request.json else 'gutenberg'
        html_content = request.json[content_key]

        modified_content = replace_text_with_lorem_ipsum(html_content)
        return jsonify({content_key: modified_content})
    
    except Exception as e:
        print(f"Error in generate_lorem_ipsum: {str(e)}")
        return jsonify({'error': str(e)}), 500