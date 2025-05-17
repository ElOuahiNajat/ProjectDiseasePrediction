import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Version avec sortie simplifiée pour éviter les problèmes d'affichage
def simple_prediction(symptom_list):
    """
    Fonction simple pour prédire la maladie à partir d'une liste de symptômes
    
    Args:
        symptom_list: Liste des symptômes en format texte (séparés par des virgules)
        
    Returns:
        Nom de la maladie prédite et score de confiance
    """
    # Charger les données
    try:
        disease_data = pd.read_csv("C:/Users/Dell/Desktop/Datasets/maladies_symptomes_binary.csv")
        print("✅ Données chargées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données: {e}")
        return "Erreur de chargement des données"
    
    # Préparation des données
    disease_column = "prognosis"  # Changer si nécessaire
    all_symptoms = [col for col in disease_data.columns if col != disease_column]
    
    # Préparation des symptômes de l'utilisateur
    if isinstance(symptom_list, str):
        # Si on reçoit une chaîne, on la divise
        user_symptoms = [s.strip().lower().replace(" ", "_") for s in symptom_list.split(",")]
    else:
        # Si on reçoit déjà une liste
        user_symptoms = [s.strip().lower().replace(" ", "_") for s in symptom_list]
    
    # Vérification des symptômes
    valid_symptoms = [s for s in user_symptoms if s in all_symptoms]
    if not valid_symptoms:
        print("❌ Aucun symptôme valide détecté dans:", user_symptoms)
        print("Symptômes disponibles:", all_symptoms[:10], "...")
        return "Impossible de faire une prédiction - symptômes non reconnus"
    
    # Création du vecteur de symptômes
    input_vector = np.zeros(len(all_symptoms))
    for symptom in valid_symptoms:
        if symptom in all_symptoms:
            input_vector[all_symptoms.index(symptom)] = 1
    
    # Préparation des données d'entraînement
    X = disease_data[all_symptoms]
    y = disease_data[disease_column]
    
    # Séparation en train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entraînement du modèle (avec paramètres simples)
    print("⏳ Entraînement du modèle SVM...")
    svm = SVC(probability=True, kernel='rbf', C=1.0, gamma='scale')
    svm.fit(X_train_scaled, y_train)
    
    # Évaluation rapide
    y_pred = svm.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"📊 Précision du modèle: {accuracy:.2%}")
    
    # Prédiction pour les symptômes de l'utilisateur
    input_df = pd.DataFrame([input_vector], columns=all_symptoms)
    input_scaled = scaler.transform(input_df)
    
    # Faire la prédiction
    try:
        prediction = svm.predict(input_scaled)[0]
        probabilities = svm.predict_proba(input_scaled)[0]
        classes = svm.classes_
        
        # Trouver l'index de la maladie prédite
        disease_idx = np.where(classes == prediction)[0][0]
        confidence = probabilities[disease_idx] * 100
        
        # Symptômes caractéristiques de la maladie
        disease_data_subset = disease_data[disease_data[disease_column] == prediction]
        disease_symptoms = []
        for symptom in all_symptoms:
            if disease_data_subset[symptom].iloc[0] == 1:
                disease_symptoms.append(symptom)
        
        # Format de sortie simplifié et clair
        print("\n" + "="*50)
        print(f"MALADIE PRÉDITE: {prediction}")
        print(f"CONFIANCE: {confidence:.2f}%")
        print("="*50)
        
        print("\nSYMPTÔMES ENTRÉS:")
        for s in valid_symptoms:
            print(f" - {s.replace('_', ' ')}")
        
        print("\nAUTRES SYMPTÔMES POSSIBLES DE CETTE MALADIE:")
        other_symptoms = [s for s in disease_symptoms if s not in valid_symptoms][:5]
        for s in other_symptoms:
            print(f" - {s.replace('_', ' ')}")
        
        return prediction, confidence
        
    except Exception as e:
        print(f"❌ Erreur lors de la prédiction: {e}")
        return "Erreur de prédiction"

# Exemple d'utilisation
if __name__ == "__main__":
    # Tester avec un exemple de symptômes
    symptoms = input("Entrez vos symptômes séparés par des virgules: ")
    result = simple_prediction(symptoms)
    
    if isinstance(result, tuple):
        disease, confidence = result
        print(f"\nRÉSULTAT FINAL: {disease} avec {confidence:.2f}% de confiance")
    else:
        print(f"\nRÉSULTAT FINAL: {result}")