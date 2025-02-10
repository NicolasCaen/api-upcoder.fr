from flask import Blueprint, jsonify

# Créer un Blueprint pour cette route
get_routes_bp = Blueprint('get_routes', __name__)

# Route : Récupérer toutes les routes disponibles
@get_routes_bp.route('/get-routes', methods=['GET'])
def get_routes():
    from flask import current_app

    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == 'static':  # Ignorer les fichiers statiques
            continue

        routes.append({
            'path': rule.rule,
            'methods': list(rule.methods - {'OPTIONS', 'HEAD'})  # Exclure OPTIONS et HEAD
        })
    return jsonify(routes)