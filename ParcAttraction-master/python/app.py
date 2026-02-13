from flask import Flask, jsonify, request

import request.request as req
import controller.auth.auth as user
import controller.attraction as attraction

app = Flask(__name__)

# ⚠️ PAS DE Flask-CORS du tout !
# Nginx gère TOUT le CORS

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

# Attraction Routes
@app.post('/attraction')
def addAttraction():
    print("Ajout d'une attraction", flush=True)
    # Fonction vérif token
    checkToken = user.check_token(request)
    if (checkToken != True):
        return checkToken

    json = request.get_json()
    retour = attraction.add_attraction(json)
    if (retour):
        return jsonify({"message": "Element ajouté.", "result": retour}), 200
    return jsonify({"message": "Erreur lors de l'ajout.", "result": retour}), 500

@app.get('/attraction')
def getAllAttraction():
    result = attraction.get_all_attraction()
    return result, 200

@app.get('/attraction/<int:index>')
def getAttraction(index):
    result = attraction.get_attraction(index)
    return result, 200

@app.get('/attraction/visible')
def getVisibleAttractions():
    """Récupère uniquement les attractions visibles (sans critiques)"""
    result = attraction.get_visible_attractions()
    return jsonify(result), 200

@app.get('/attraction/visible/critiques')
def getVisibleAttractionsWithCritiques():
    """Récupère les attractions visibles avec leurs critiques"""
    result = attraction.get_visible_attractions_with_critiques()
    return jsonify(result), 200

@app.delete('/attraction/<int:index>')
def deleteAttraction(index):
    # Fonction vérif token
    checkToken = user.check_token(request)
    if (checkToken != True):
        return checkToken

    if (attraction.delete_attraction(index)):
        return "Element supprimé.", 200
    return jsonify({"message": "Erreur lors de la suppression."}), 500

# Critique Routes
@app.post('/critique')
def addCritique():
    """Ajoute une critique pour une attraction"""
    json = request.get_json()
    res = attraction.add_critique(json)
    if res:
        return jsonify({"message": "Critique ajoutée", "critique_id": res}), 200
    return jsonify({"message": "Erreur lors de l'ajout de la critique"}), 400

@app.get('/critique/attraction/<int:attraction_id>')
def getCritiquesByAttraction(attraction_id):
    """Récupère toutes les critiques d'une attraction"""
    result = attraction.get_critiques_by_attraction(attraction_id)
    return jsonify(result), 200

# Auth Routes
@app.post('/login')
def login():
    json = request.get_json()

    if (not 'name' in json or not 'password' in json):
        result = jsonify({'messages': ["Nom ou/et mot de passe incorrect"]})
        return result, 400
    
    cur, conn = req.get_db_connection()
    requete = f"SELECT * FROM users WHERE name = '{json['name']}' AND password = '{json['password']}';"
    cur.execute(requete)
    records = cur.fetchall()
    conn.close()

    if len(records) == 0:
        return jsonify({"message": "Identifiants incorrects"}), 401

    result = jsonify({"token": user.encode_auth_token(list(records[0])[0]), "name": json['name']})
    return result, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)