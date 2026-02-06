import request.request as req

def add_attraction(data):
    print(data, flush=True)
    if (not "nom" in data or data["nom"] == ""):
        return False
    
    if (not "description" in data or data["description"] == ""):
        return False

    if (not "difficulte" in data or data["difficulte"] is None):
        return False

    if (not "visible" in data):
        data["visible"] = True

    if ("attraction_id" in data and data["attraction_id"]):
        requete = f"UPDATE attraction SET nom='{data['nom']}', description='{data['description']}', difficulte={data['difficulte']}, visible={data['visible']} WHERE attraction_id = {data['attraction_id']}"
        req.insert_in_db(requete)
        id = data['attraction_id']
    else:
        requete = "INSERT INTO attraction (nom, description, difficulte, visible) VALUES (?, ?, ?, ?);"
        id = req.insert_in_db(requete, (data["nom"], data["description"], data["difficulte"], data["visible"]))

    return id

def get_all_attraction():
    json = req.select_from_db("SELECT * FROM attraction")
    return json

def get_attraction(id):
    if (not id):
        return False

    json = req.select_from_db("SELECT * FROM attraction WHERE attraction_id = ?", (id,))

    if len(json) > 0:
        return json[0]
    else:
        return []

def delete_attraction(id):
    if (not id):
        return False

    req.delete_from_db("DELETE FROM attraction WHERE attraction_id = ?", (id,))
    return True

def get_visible_attractions():
    return req.select_from_db("SELECT * FROM attraction WHERE visible = 1")

def get_visible_attractions_with_critiques():
    """Récupère les attractions visibles avec leurs critiques associées"""
    attractions = req.select_from_db("SELECT * FROM attraction WHERE visible = 1")
    
    # Pour chaque attraction, récupérer ses critiques
    for attraction in attractions:
        critiques = req.select_from_db(
            "SELECT * FROM critique WHERE attraction_id = ?", 
            (attraction['attraction_id'],)
        )
        attraction['critiques'] = critiques
    
    return attractions

def add_critique(data):
    """Ajoute une critique pour une attraction"""
    if not data.get('attraction_id'):
        return False
    
    if not data.get('note') or data.get('note') < 1 or data.get('note') > 5:
        return False
    
    requete = "INSERT INTO critique (attraction_id, nom, prenom, note, commentaire, est_anonyme) VALUES (?, ?, ?, ?, ?, ?)"
    params = (
        data.get('attraction_id'), 
        data.get('nom', 'Anonyme'), 
        data.get('prenom', ''), 
        data.get('note'), 
        data.get('commentaire', ''), 
        1 if data.get('est_anonyme') else 0
    )
    return req.insert_in_db(requete, params)

def get_critiques_by_attraction(attraction_id):
    """Récupère toutes les critiques d'une attraction"""
    if not attraction_id:
        return []
    
    return req.select_from_db(
        "SELECT * FROM critique WHERE attraction_id = ? ORDER BY critique_id DESC", 
        (attraction_id,)
    )