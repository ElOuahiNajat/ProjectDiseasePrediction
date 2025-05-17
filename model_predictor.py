import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import ast  # Pour convertir les chaînes en listes


class DiseasePredictor:
    def __init__(self, disease_data_path, medications_path=None, description_path=None, 
                 diets_path=None, precautions_path=None, workout_path=None, model_path=None):
        """
        Initialise le prédicteur de maladies avec toutes les informations supplémentaires
        
        Args:
            disease_data_path: Chemin vers le fichier CSV des maladies/symptômes
            medications_path: Chemin vers le fichier CSV des médicaments
            description_path: Chemin vers le fichier CSV des descriptions
            diets_path: Chemin vers le fichier CSV des régimes alimentaires
            precautions_path: Chemin vers le fichier CSV des précautions
            workout_path: Chemin vers le fichier CSV des exercices/routines
            model_path: Chemin vers un modèle préentraîné (optionnel)
        """
        self.disease_data = pd.read_csv(disease_data_path)
        self.disease_column = "prognosis"  # Colonne contenant les noms des maladies
        self.all_symptoms = [col for col in self.disease_data.columns if col != self.disease_column]
        
        # Chargement des fichiers supplémentaires s'ils sont fournis
        self.medications_data = self._load_data(medications_path)
        self.description_data = self._load_data(description_path)
        self.diets_data = self._load_data(diets_path)
        self.precautions_data = self._load_data(precautions_path)
        self.workout_data = self._load_data(workout_path)
        
        # Chargement du modèle s'il existe, sinon entraînement d'un nouveau
        self.model = None
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.train_model()
    
    def _load_data(self, file_path):
        """Charge un fichier CSV s'il existe"""
        if file_path and os.path.exists(file_path):
            return pd.read_csv(file_path)
        return None
    
    def get_symptoms(self):
        """Renvoie la liste des symptômes disponibles, formatés pour l'affichage"""
        return [symptom.replace('_', ' ').capitalize() for symptom in self.all_symptoms]
    
    def train_model(self, test_size=0.2, random_state=42):
        """Entraîne le modèle de prédiction de maladies"""
        print("Entraînement du modèle en cours...")
        
        # Séparation des features et de la cible
        X = self.disease_data[self.all_symptoms]
        y = self.disease_data[self.disease_column]
        
        # Création et entraînement du modèle
        self.model = RandomForestClassifier(n_estimators=100, random_state=random_state)
        self.model.fit(X, y)  # Entraînement sur toutes les données
        
        print("✅ Modèle entraîné avec succès")
        return self.model
    
    def predict(self, user_symptoms):
        """
        Prédit la maladie basée sur les symptômes fournis par l'utilisateur et récupère
        toutes les informations supplémentaires
        
        Args:
            user_symptoms: Liste des symptômes présents
            
        Returns:
            Dictionnaire avec toutes les informations sur la prédiction et les détails associés
        """
        if self.model is None:
            print("⚠️ Le modèle n'a pas encore été entraîné. Entraînement en cours...")
            self.train_model()
        
        # Normalisation des symptômes entrés
        normalized_symptoms = []
        for symptom in user_symptoms:
            # Convertir au format du modèle (lower case, underscores)
            normalized = symptom.lower().replace(' ', '_')
            if normalized in self.all_symptoms:
                normalized_symptoms.append(normalized)
        
        # Création d'un vecteur de symptômes (0 ou 1 pour chaque symptôme possible)
        input_vector = np.zeros(len(self.all_symptoms))
        for symptom in normalized_symptoms:
            if symptom in self.all_symptoms:
                idx = self.all_symptoms.index(symptom)
                input_vector[idx] = 1
        
        # Prédiction avec le modèle
        input_df = pd.DataFrame([input_vector], columns=self.all_symptoms)
        prediction = self.model.predict(input_df)[0]
        
        # Score de confiance (probabilité de la classe prédite)
        probabilities = self.model.predict_proba(input_df)[0]
        classes = self.model.classes_
        confidence_score = probabilities[np.where(classes == prediction)[0][0]]
        
        # Symptômes caractéristiques de la maladie prédite
        disease_symptoms = self.get_disease_symptoms(prediction)
        
        # Calcul de la précision comme pourcentage de symptômes entrés qui correspondent à la maladie
        matching_symptoms = [s for s in normalized_symptoms if s in disease_symptoms]
        precision = (len(matching_symptoms) / len(normalized_symptoms)) * 100 if normalized_symptoms else 0
        
        # Récupération de toutes les informations supplémentaires
        result = {
            "disease": prediction,
            "score": confidence_score,
            "precision": precision,
            "symptoms": [s.replace('_', ' ').capitalize() for s in normalized_symptoms],
            "disease_symptoms": [s.replace('_', ' ').capitalize() for s in disease_symptoms],
            "medications": self.get_medications(prediction),
            "description": self.get_description(prediction),
            "diets": self.get_diets(prediction),
            "precautions": self.get_precautions(prediction),
            "workout": self.get_workout(prediction)
        }
        
        return result
    
    def get_disease_symptoms(self, disease_name):
        """Retourne les symptômes associés à une maladie spécifique"""
        disease_data = self.disease_data[self.disease_data[self.disease_column] == disease_name]
        if disease_data.empty:
            return []
        
        # Récupérer les symptômes qui ont une valeur de 1 pour cette maladie
        symptoms = []
        for symptom in self.all_symptoms:
            if disease_data[symptom].iloc[0] == 1:
                symptoms.append(symptom)
        
        return symptoms
    
    def get_medications(self, disease_name):
        """Retourne les médicaments recommandés pour une maladie"""
        if self.medications_data is None:
            return []
        
        # Vérifier si la maladie est dans le fichier des médicaments
        if 'Disease' not in self.medications_data.columns or disease_name not in self.medications_data['Disease'].values:
            return []
        
        # Récupérer les médicaments pour cette maladie
        meds = self.medications_data[self.medications_data['Disease'] == disease_name]['Medication'].iloc[0]
        
        # Convertir la chaîne en liste si nécessaire
        if isinstance(meds, str) and meds.startswith('['):
            try:
                return ast.literal_eval(meds)
            except:
                return [meds]
        return [meds] if isinstance(meds, str) else meds
    
    def get_description(self, disease_name):
        """Retourne la description de la maladie"""
        if self.description_data is None:
            return ""
        
        if 'Disease' not in self.description_data.columns or disease_name not in self.description_data['Disease'].values:
            return ""
        
        return self.description_data[self.description_data['Disease'] == disease_name]['Description'].iloc[0]
    
    def get_diets(self, disease_name):
        """Retourne les recommandations alimentaires pour la maladie"""
        if self.diets_data is None:
            return []
        
        if 'Disease' not in self.diets_data.columns or disease_name not in self.diets_data['Disease'].values:
            return []
        
        diets = self.diets_data[self.diets_data['Disease'] == disease_name]['Diet'].iloc[0]
        
        # Convertir la chaîne en liste si nécessaire
        if isinstance(diets, str) and diets.startswith('['):
            try:
                return ast.literal_eval(diets)
            except:
                return [diets]
        return [diets] if isinstance(diets, str) else diets
    
    def get_precautions(self, disease_name):
        """Retourne les précautions pour la maladie"""
        if self.precautions_data is None:
            return []
        
        if 'Disease' not in self.precautions_data.columns or disease_name not in self.precautions_data['Disease'].values:
            return []
        
        # Récupérer toutes les précautions pour cette maladie
        precautions_row = self.precautions_data[self.precautions_data['Disease'] == disease_name]
        
        # Collecter toutes les précautions non-nulles
        precautions = []
        for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
            if col in precautions_row.columns and not pd.isna(precautions_row[col].iloc[0]):
                precautions.append(precautions_row[col].iloc[0])
        
        return precautions
    
    def get_workout(self, disease_name):
        """Retourne les recommandations d'exercice pour la maladie"""
        if self.workout_data is None:
            return []
        
        if 'disease' not in self.workout_data.columns or disease_name not in self.workout_data['disease'].values:
            return []
        
        # Récupérer toutes les activités physiques pour cette maladie
        workout_rows = self.workout_data[self.workout_data['disease'] == disease_name]
        return workout_rows['workout'].tolist()
    
    def save_model(self, model_path="disease_model.joblib"):
        """Sauvegarde le modèle sur disque"""
        if self.model is None:
            print("❌ Le modèle n'a pas encore été entraîné.")
            return
        joblib.dump(self.model, model_path)
        print(f"✅ Modèle sauvegardé à {model_path}")
    
    def load_model(self, model_path="disease_model.joblib"):
        """Charge un modèle préentraîné depuis le disque"""
        try:
            self.model = joblib.load(model_path)
            print("✅ Modèle chargé avec succès")
        except Exception as e:
            print(f"❌ Impossible de charger le modèle depuis {model_path}: {e}")
            return False
        return True