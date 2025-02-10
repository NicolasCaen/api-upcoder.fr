from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup, Comment
import openai
from google.cloud import aiplatform
import requests
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import time

ai_content_generator_bp = Blueprint('ai_content_generator', __name__)

class AIProvider(ABC):
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles pour ce provider"""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int, model: str) -> str:
        """Génère du texte avec le modèle spécifié"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Vérifie si le provider est configuré"""
        pass

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.models = {
            'gpt-4': {'max_tokens': 4096, 'type': 'chat'},
            'gpt-4-turbo': {'max_tokens': 4096, 'type': 'chat'},
            'gpt-3.5-turbo': {'max_tokens': 4096, 'type': 'chat'},
            'gpt-3.5-turbo-instruct': {'max_tokens': 4096, 'type': 'completion'},
            'text-davinci-003': {'max_tokens': 2048, 'type': 'completion'}
        }
        openai.api_key = self.api_key

    def get_available_models(self) -> List[str]:
        return list(self.models.keys())

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, max_tokens: int, model: str) -> str:
        if model not in self.models:
            raise ValueError(f"Modèle {model} non supporté par OpenAI")

        try:
            if self.models[model]['type'] == 'chat':
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=min(max_tokens, self.models[model]['max_tokens'])
                )
                return response.choices[0].message.content.strip()
            else:
                response = openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=min(max_tokens, self.models[model]['max_tokens'])
                )
                return response.choices[0].text.strip()
        except Exception as e:
            print(f"OpenAI Error: {str(e)}")
            raise

class MistralAIProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv('MISTRAL_API_KEY')
        self.models = {
            'mistral-tiny': {'max_tokens': 4096},
            'mistral-small': {'max_tokens': 8192},
            'mistral-medium': {'max_tokens': 32768}
        }

    def get_available_models(self) -> List[str]:
        return list(self.models.keys())

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, max_tokens: int, model: str) -> str:
        if model not in self.models:
            raise ValueError(f"Modèle {model} non supporté par Mistral")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": min(max_tokens, self.models[model]['max_tokens'])
            }
            response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()  # Lève une exception en cas d'erreur HTTP
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Mistral AI Error: {str(e)}")
            raise

class DeepseekAIProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.models = {
            'deepseek-chat': {'max_tokens': 4096},
            'deepseek-coder': {'max_tokens': 8192}
        }

    def get_available_models(self) -> List[str]:
        return list(self.models.keys())

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, max_tokens: int, model: str) -> str:
        if model not in self.models:
            raise ValueError(f"Modèle {model} non supporté par Deepseek")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "prompt": prompt,
                "max_tokens": min(max_tokens, self.models[model]['max_tokens'])
            }
            response = requests.post(
                "https://api.deepseek.com/v1/completions",
                headers=headers,
                json=data
            )
            return response.json()["choices"][0]["text"]
        except Exception as e:
            print(f"Deepseek Error: {str(e)}")
            raise

class AIContentGenerator:
    PROVIDERS = {
        'openai': OpenAIProvider,
        'mistral': MistralAIProvider,
        'deepseek': DeepseekAIProvider
    }

    def __init__(self, topic: str, provider_name: str, model: str, tone: str = "professionnel"):
        self.topic = topic
        self.tone = tone
        self.cache = {}
        self.provider = self._get_provider(provider_name)
        self.model = self._validate_model(model)

    def _get_provider(self, provider_name: str) -> AIProvider:
        provider_class = self.PROVIDERS.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Provider {provider_name} non supporté")
        
        provider = provider_class()
        if not provider.is_available():
            raise ValueError(f"Provider {provider_name} non configuré")
        return provider

    def _validate_model(self, model: str) -> str:
        available_models = self.provider.get_available_models()
        if model not in available_models:
            raise ValueError(f"Modèle {model} non disponible pour ce provider. Modèles disponibles: {available_models}")
        return model

    def generate_content(self, original_length: int) -> str:
        cache_key = f"{self.topic}_{original_length}_{self.tone}_{self.model}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        size_prompt = "court" if original_length < 100 else "moyen" if original_length < 300 else "long"
        prompt = f"""Générez un texte {size_prompt} sur {self.topic} dans un ton {self.tone}. 
                    Le texte doit faire environ {original_length} caractères."""
        
        try:
            generated_text = self.provider.generate_text(prompt, original_length // 2, self.model)
            self.cache[cache_key] = generated_text
            return generated_text
        except Exception as e:
            print(f"Erreur de génération: {str(e)}")
            return f"Erreur de génération: {str(e)}"

@ai_content_generator_bp.route('/get-available-providers', methods=['GET'])
def get_available_providers():
    """Endpoint pour obtenir les providers et leurs modèles disponibles"""
    providers_info = {}
    for provider_name, provider_class in AIContentGenerator.PROVIDERS.items():
        provider = provider_class()
        if provider.is_available():
            providers_info[provider_name] = provider.get_available_models()
    return jsonify(providers_info)

@ai_content_generator_bp.route('/generate-ai-content', methods=['POST'])
def generate_ai_content_route():
    try:
        if not request.is_json:
            return jsonify({'error': 'Données JSON requises'}), 400
            
        required_fields = {'content', 'topic', 'provider', 'model'}
        if not all(field in request.json for field in required_fields):
            return jsonify({'error': 'Les champs content, topic, provider et model sont requis'}), 400
            
        html_content = request.json['content']
        topic = request.json['topic']
        provider = request.json['provider']
        model = request.json['model']
        tone = request.json.get('tone', 'professionnel')
        
        generator = AIContentGenerator(topic, provider, model, tone)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        ignore_tags = {'script', 'style', 'code', 'pre'}
        
        for element in soup.find_all(string=True):
            if (isinstance(element, Comment) or 
                element.parent.name in ignore_tags or 
                not element.strip()):
                continue
                
            original_text = element.strip()
            if original_text:
                time.sleep(0.5)
                new_text = generator.generate_content(len(original_text))
                element.replace_with(new_text)
        
        return jsonify({
            'generated_content': str(soup),
            'topic': topic,
            'provider': provider,
            'model': model,
            'tone': tone
        })
        
    except Exception as e:
        print(f"Error in generate_ai_content: {str(e)}")
        return jsonify({'error': str(e)}), 500