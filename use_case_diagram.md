# Diagramme de Cas d'Utilisation - Système d'Enrichissement de Documents Pharmaceutiques

## Acteurs du Système

### 👨‍💼 **Expert Pharmaceutique**
- Utilisateur principal spécialisé
- Valide et corrige les annotations IA
- Crée des relations complexes

### 🤖 **Système IA**
- Génère les annotations automatiques
- Enrichit les documents
- Répond aux questions

### 👤 **Métadonneur**
- Utilisateur standard
- Télécharge et gère les documents

### 🔧 **Administrateur**
- Gère le système
- Configure les paramètres

## Cas d'Utilisation par Module

### 📄 **Gestion des Documents**
```
Expert/Métadonneur
├── Télécharger un document PDF
├── Visualiser le document dans l'interface
├── Naviguer dans les pages PDF
├── Sélectionner du texte dans le PDF
└── Gérer les métadonnées du document
```

### 🔍 **Extraction et Annotation**
```
Système IA
├── Extraire les annotations de base
│   ├── Identifier les entités pharmaceutiques
│   ├── Détecter les dosages
│   ├── Reconnaître les indications
│   └── Extraire les contre-indications
├── Générer le JSON structuré
└── Calculer les scores de confiance
```

### 🧠 **Enrichissement Intelligent**
```
Expert + Système IA
├── Enrichir automatiquement le document
│   ├── Générer des relations entre entités
│   ├── Créer des questions-réponses
│   ├── Produire un résumé sémantique
│   └── Identifier les contextes
├── Comparer IA vs Expert
└── Régénérer avec apprentissage
```

### 🎨 **Créateur Visuel de Relations**
```
Expert
├── Ouvrir l'interface visuelle
├── Gérer les entités sur le canvas
│   ├── Ajouter des entités depuis la palette
│   ├── Créer de nouvelles entités
│   ├── Positionner et déplacer les entités
│   └── Sélectionner depuis les annotations
├── Créer des relations
│   ├── Connecter deux entités
│   ├── Choisir le type de relation
│   ├── Décrire la relation (manuel/IA)
│   └── Valider la relation
├── Organiser le graphique
│   ├── Auto-arranger les entités
│   ├── Optimiser la disposition
│   └── Gérer les connexions visuelles
└── Sauvegarder toutes les relations
```

### ❓ **Système Questions-Réponses**
```
Expert
├── Tester le système Q&A
│   ├── Poser une question
│   ├── Choisir la source (basique/enrichi)
│   └── Évaluer la réponse
├── Corriger les réponses
│   ├── Identifier les erreurs
│   ├── Proposer la bonne réponse
│   └── Enregistrer la correction
├── Ajouter des Q&A manuelles
│   ├── Saisir question et réponse
│   ├── Ajouter des tags
│   └── Lier aux entités
└── Analyser des paragraphes
    ├── Extraire des relations depuis du texte
    ├── Prévisualiser les relations trouvées
    ├── Modifier/supprimer des relations
    └── Sauvegarder les relations validées
```

### 📊 **Apprentissage et Amélioration**
```
Expert + Système IA
├── Comparer avec une IA fraîche
├── Analyser les améliorations expertes
├── Enregistrer les patterns d'apprentissage
├── Consulter l'historique des corrections
├── Visualiser les statistiques d'apprentissage
└── Régénérer avec les améliorations
```

### 💾 **Gestion des Données**
```
Expert
├── Éditer le JSON enrichi
├── Sauvegarder les modifications manuelles
├── Exporter les données
├── Consulter les versions
└── Gérer les annotations
    ├── Rechercher des annotations
    ├── Filtrer par type
    ├── Prévisualiser le contenu
    └── Ajouter au canvas visuel
```

### 🔧 **Administration**
```
Administrateur
├── Gérer les utilisateurs et permissions
├── Configurer les paramètres IA
├── Monitorer les performances
├── Gérer les fichiers PDF
└── Maintenir la base de données
```

## Relations Between Use Cases

### **<<include>>**
- "Créer des relations" include "Choisir le type de relation"
- "Enrichir automatiquement" include "Générer des relations"
- "Tester Q&A" include "Évaluer la réponse"

### **<<extend>>**
- "Corriger les réponses" extends "Tester Q&A"
- "Décrire la relation avec IA" extends "Créer des relations"
- "Auto-arranger" extends "Gérer les entités"

### **<<generalization>>**
- Expert et Métadonneur héritent d'Utilisateur
- Tous les cas d'annotation héritent de "Traiter un document"

## Flux Principal du Système

```
1. Métadonneur télécharge un PDF
2. Système IA extrait les annotations de base
3. Expert ouvre le document pour enrichissement
4. Système IA génère l'enrichissement automatique
5. Expert utilise le créateur visuel pour affiner
6. Expert teste et corrige le système Q&A
7. Expert compare et améliore via l'apprentissage
8. Expert sauvegarde la version finale enrichie
```

## Priorités des Cas d'Utilisation

### **🔴 Critiques (Core)**
- Télécharger document PDF
- Extraire annotations de base
- Créer relations visuelles
- Enrichir automatiquement

### **🟡 Importants (Enhanced)**
- Tester système Q&A
- Corriger réponses IA
- Auto-organiser le canvas
- Comparer IA vs Expert

### **🟢 Optionnels (Advanced)**
- Analyser paragraphes
- Gérer apprentissage avancé
- Exporter données
- Administration avancée