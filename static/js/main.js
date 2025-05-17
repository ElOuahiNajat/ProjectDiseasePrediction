// main.js - Script principal pour HealthAI
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des variables
    const symptomSearch = document.getElementById('symptomSearch');
    const symptomItems = document.querySelectorAll('.symptom-item');
    const selectedSymptomsContainer = document.getElementById('selectedSymptomsContainer');
    const analyzeButton = document.getElementById('analyzeButton');
    const diagnosisForm = document.getElementById('diagnosisForm');
    const loaderContainer = document.getElementById('loaderContainer');
    const resultSection = document.getElementById('resultSection');
    
    // Gestion de la recherche de symptômes
    if (symptomSearch) {
        symptomSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            symptomItems.forEach(function(item) {
                const label = item.querySelector('label');
                const symptomText = label.textContent.toLowerCase();
                
                if (symptomText.includes(searchTerm)) {
                    item.style.display = '';  // Afficher l'élément
                } else {
                    item.style.display = 'none';  // Masquer l'élément
                }
            });
        });

        // Créer le conteneur d'image qui sera utilisé pour toutes les images au survol
        const imageContainer = document.createElement('div');
        imageContainer.id = 'hover-image-container';
        
        const hoverImage = document.createElement('img');
        hoverImage.id = 'hover-image';
        
        imageContainer.appendChild(hoverImage);
        document.body.appendChild(imageContainer);
        
        // Configuration des images au survol des symptômes
        const symptomItemsWithImages = document.querySelectorAll('.symptom-item');
        
        symptomItemsWithImages.forEach(item => {
            // Récupérer l'URL de l'image de l'élément symptôme
            const originalImg = item.querySelector('.symptom-hover-image');
            let imgSrc = '';
            
            if (originalImg) {
                imgSrc = originalImg.getAttribute('src');
            }
            
            // Si l'image existe, configurer les événements de survol
            if (imgSrc) {
                item.addEventListener('mouseenter', function(e) {
                    // Configurer l'image
                    hoverImage.setAttribute('src', imgSrc);
                    imageContainer.style.display = 'block';
                    
                    // Positionner l'image près du curseur mais en s'assurant qu'elle est entièrement visible
                    updateImagePosition(e);
                });
                
                item.addEventListener('mousemove', updateImagePosition);
                
                item.addEventListener('mouseleave', function() {
                    imageContainer.style.display = 'none';
                });
            }
        });
        
        // Fonction pour mettre à jour la position de l'image en fonction du curseur
        function updateImagePosition(e) {
            const x = e.clientX;
            const y = e.clientY;
            
            // Obtenir les dimensions de la fenêtre
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;
            
            // Obtenir les dimensions de l'image
            const imgWidth = 200; // Même largeur que définie dans le CSS
            const imgHeight = 150; // Hauteur maximale définie dans le CSS
            
            // Calculer la position pour s'assurer que l'image reste dans la fenêtre
            let posX = x + 20; // 20px à droite du curseur par défaut
            let posY = y - imgHeight / 2; // Centré verticalement par rapport au curseur
            
            // Vérifier si l'image dépasse à droite
            if (posX + imgWidth > windowWidth) {
                posX = x - imgWidth - 20; // Placer à gauche du curseur
            }
            
            // Vérifier si l'image dépasse en haut ou en bas
            if (posY < 0) {
                posY = 0;
            } else if (posY + imgHeight > windowHeight) {
                posY = windowHeight - imgHeight;
            }
            
            // Appliquer la position
            imageContainer.style.left = posX + 'px';
            imageContainer.style.top = posY + 'px';
        }
    }
    
    // ... [Reste du code de sélection des symptômes] ...
    
    // Code existant pour les symptômes
    symptomItems.forEach(function(item) {
        const checkbox = item.querySelector('input[type="checkbox"]');
        
        item.addEventListener('click', function(e) {
            if (e.target === checkbox) {
                return;
            }
            
            const symptomName = this.querySelector('label').textContent.trim();
            
            checkbox.checked = !checkbox.checked;
            this.classList.toggle('selected', checkbox.checked);
            
            if (checkbox.checked) {
                addSelectedSymptom(symptomName);
            } else {
                removeSelectedSymptom(symptomName);
            }
        });
        
        checkbox.addEventListener('change', function(e) {
            e.stopPropagation();
        });
    });
    
    // Fonction pour ajouter un symptôme sélectionné
    function addSelectedSymptom(symptomName) {
        const existingSymptom = selectedSymptomsContainer.querySelector(`[data-symptom="${symptomName}"]`);
        if (existingSymptom) {
            return;
        }
        
        const placeholder = selectedSymptomsContainer.querySelector('.text-muted');
        
        if (placeholder) {
            selectedSymptomsContainer.innerHTML = '';
        }
        
        const symptomElement = document.createElement('div');
        symptomElement.className = 'selected-symptom';
        symptomElement.setAttribute('data-symptom', symptomName);
        symptomElement.innerHTML = `${symptomName} <i class="bi bi-x-circle"></i>`;
        
        symptomElement.querySelector('i').addEventListener('click', function(e) {
            e.stopPropagation();
            removeSelectedSymptom(symptomName);
            
            const checkbox = document.querySelector(`input[value="${symptomName.toLowerCase().replace(/\s+/g, '_')}"]`);
            if (checkbox) {
                checkbox.checked = false;
                checkbox.closest('.symptom-item').classList.remove('selected');
            }
        });
        
        selectedSymptomsContainer.appendChild(symptomElement);
        updateSubmitButtonState();
    }
    
    // Fonction pour retirer un symptôme sélectionné
    function removeSelectedSymptom(symptomName) {
        const symptomElement = selectedSymptomsContainer.querySelector(`[data-symptom="${symptomName}"]`);
        
        if (symptomElement) {
            selectedSymptomsContainer.removeChild(symptomElement);
        }
        
        if (selectedSymptomsContainer.children.length === 0) {
            selectedSymptomsContainer.innerHTML = '<p class="text-muted">Sélectionnez vos symptômes ci-dessous</p>';
        }
        
        updateSubmitButtonState();
    }
    
    // Mise à jour de l'état du bouton d'analyse
    function updateSubmitButtonState() {
        const selectedSymptoms = selectedSymptomsContainer.querySelectorAll('.selected-symptom');
        
        if (selectedSymptoms.length >= 3) {
            analyzeButton.removeAttribute('disabled');
            analyzeButton.classList.remove('btn-secondary');
            analyzeButton.classList.add('btn-primary');
        } else {
            analyzeButton.setAttribute('disabled', 'disabled');
            analyzeButton.classList.remove('btn-primary');
            analyzeButton.classList.add('btn-secondary');
        }
    }
    
    // ... [Reste du code de formulaire et loader] ...
    
    // DÉBUT DU CODE CORRIGÉ POUR LE CHATBOT
    const chatbotBtn = document.getElementById('chatbotBtn');
    const chatbotBox = document.getElementById('chatbotBox');
    const closeChatbot = document.getElementById('closeChatbot');
    const chatbotInput = document.getElementById('chatbotInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatbotBody = document.getElementById('chatbotBody');

    // Fonction pour afficher/masquer le chatbot
    function toggleChatbot(show) {
        chatbotBox.style.display = show ? 'flex' : 'none';
    }

    // Fonction pour ajouter un message au chatbot
    function addChatMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        messageDiv.textContent = text;
        chatbotBody.appendChild(messageDiv);
        chatbotBody.scrollTop = chatbotBody.scrollHeight;
    }

    // Fonction pour appeler l'API de chat
    async function fetchChatResponse(message) {
        try {
            // Afficher un indicateur de chargement
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message bot';
            loadingDiv.innerHTML = '<em>Réflexion en cours...</em>';
            chatbotBody.appendChild(loadingDiv);
            chatbotBody.scrollTop = chatbotBody.scrollHeight;
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });
            
            // Supprimer l'indicateur de chargement
            chatbotBody.removeChild(loadingDiv);
            
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Erreur lors de la récupération de la réponse:', error);
            return "Désolé, je rencontre des difficultés techniques. Veuillez réessayer plus tard.";
        }
    }

    // Fonction pour envoyer un message au chatbot
    async function sendChatMessage() {
        const message = chatbotInput.value.trim();
        if (message === '') return;
        
        // Ajouter le message de l'utilisateur à l'interface
        addChatMessage(message, true);
        chatbotInput.value = '';
        
        // Obtenir une réponse de l'API
        const botResponse = await fetchChatResponse(message);
        addChatMessage(botResponse);
    }

    // Gestionnaires d'événements pour le chatbot
    if (chatbotBtn) {
        chatbotBtn.addEventListener('click', function() {
            toggleChatbot(chatbotBox.style.display !== 'flex');
        });
    }
    
    if (closeChatbot) {
        closeChatbot.addEventListener('click', function() {
            toggleChatbot(false);
        });
    }
    
    if (sendMessage) {
        sendMessage.addEventListener('click', sendChatMessage);
    }
    
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
    
    // Message de bienvenue au chargement
    if (chatbotBody) {
        setTimeout(() => {
            addChatMessage("Bonjour ! Je suis l'assistant HealthAI. Comment puis-je vous aider aujourd'hui ?");
        }, 500);
    }
    // FIN DU CODE CORRIGÉ POUR LE CHATBOT

    // Initialisation des éléments sélectionnés au chargement de la page
    const selectedItems = document.querySelectorAll('.symptom-item input[type="checkbox"]:checked');
    selectedItems.forEach(checkbox => {
        const item = checkbox.closest('.symptom-item');
        item.classList.add('selected');
        const symptomName = item.querySelector('label').textContent.trim();
        addSelectedSymptom(symptomName);
    });
});