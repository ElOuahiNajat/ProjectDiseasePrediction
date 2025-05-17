from flask import Flask, request, jsonify, render_template, url_for
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Liste de symptômes (exemple simplifié)
symptoms = [
    "fièvre", "maux_de_tête", "toux", "fatigue", "courbatures",
    "mal_de_gorge", "congestion_nasale", "essoufflement", "douleur_thoracique"
]

# Dictionnaire pour les infos des symptômes
symptoms_dict = {}  # À remplir avec vos données

@app.route('/')
def index():
    return render_template('index.html', symptoms=symptoms, symptoms_dict=symptoms_dict)

@app.route('/', methods=['POST'])
def analyze():
    # Traitement du formulaire pour l'analyse des symptômes
    # Votre code existant ici...
    return render_template('index.html', symptoms=symptoms, symptoms_dict=symptoms_dict, result=result)

@app.route('/chat', methods=['POST'])
def chat():
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

def generate_response(user_input):
    try:
        # Vérification de la clé API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Erreur: Clé API Gemini non configurée."
        
        # Initialisation du client Gemini
        client = genai.Client(api_key=api_key)
        
        # Configuration de la requête
        model = "gemini-1.5-flash"  # Vérifiez le nom du modèle
        
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
                types.Part.from_text(text="""Tu es un assistant santé bienveillant, non médecin. 
                Tu dois aider les utilisateurs à comprendre l'application HealthAI et à naviguer dans ses fonctionnalités.
                Tu peux donner des conseils généraux sur la santé mais précise toujours que tu n'es pas un médecin et 
                que l'utilisateur devrait consulter un professionnel de la santé pour des conseils médicaux personnalisés."""),
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

if __name__ == "__main__":
    app.run(debug=True)