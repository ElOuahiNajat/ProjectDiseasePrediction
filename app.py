from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from dotenv import load_dotenv
from model_predictor import DiseasePredictor

# Pour l'intégration de Gemini
from google import genai
from google.genai import types

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# ---- Configuration et initialisation ----

# Initialisation du prédicteur avec tous les fichiers CSV
predictor = DiseasePredictor(
    "data/maladies_symptomes_binary.csv",
    medications_path="data/medications.csv",
    description_path="data/description.csv",
    diets_path="data/diets.csv",
    precautions_path="data/precautions_df.csv",
    workout_path="data/workout_df.csv",
    model_path=None  # Mettre le chemin vers votre modèle préentraîné si disponible
)

# Chargement des données des symptômes avec poids et images
symptoms_info = pd.read_csv("data/symptom-severity.csv")

symptoms_dict = {}
symptoms = []

for _, row in symptoms_info.iterrows():
    raw_name = row['Symptom']
    formatted_name = raw_name.replace('_', ' ').capitalize()
    
    symptoms_dict[formatted_name] = {
        'weight': row['weight'],
        'url': row['url'] if 'url' in row and not pd.isna(row['url']) else None
    }
    symptoms.append(raw_name)

# ---- Routes principales ----

@app.route("/", methods=["GET", "POST"])
def index():
    """Page d'accueil permettant l'analyse des symptômes"""
    result = None

    if request.method == "POST":
        selected_symptoms = request.form.getlist("symptoms")
        
        if selected_symptoms:
            result = predictor.predict(selected_symptoms)
            result["score"] = f"{result['score']*100:.2f}%"
            result["precision"] = f"{result['precision']:.2f}%"
    
    return render_template("index.html", symptoms=symptoms, result=result, symptoms_dict=symptoms_dict)

@app.route('/chat', methods=['POST'])
def chat():
    """API pour le chat avec l'assistant santé (Gemini)"""
    try:
        # Récupération du message utilisateur
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message requis"}), 400
            
        user_message = data.get("message", "")
        
        # Génération de la réponse avec Gemini
        response = generate_response(user_message)
        
        return jsonify({"response": response})
    except Exception as e:
        app.logger.error(f"Erreur lors du traitement de la requête chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ---- Fonctions auxiliaires ----

def generate_response(user_input):
    """Génère une réponse via l'API Gemini"""
    try:
        # Vérification de la clé API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Erreur: Clé API Gemini non configurée."
        
        # Initialisation du client Gemini
        client = genai.Client(api_key=api_key)
        
        # Configuration de la requête
        model = "gemini-1.5-flash"
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
            ],
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""Tu es un assistant santé bienveillant."""),
            ],
        )
        
        # Génération de la réponse
        output = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                output += chunk.text
        
        return output
    except Exception as e:
        app.logger.error(f"Erreur lors de la génération de réponse: {str(e)}")
        return f"Désolé, je n'ai pas pu traiter votre demande: {str(e)}"

# ---- Point d'entrée de l'application ----

if __name__ == "__main__":
    app.run(debug=True)