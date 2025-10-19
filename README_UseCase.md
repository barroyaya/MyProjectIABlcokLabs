# 📋 Diagramme de Cas d'Utilisation - Mode d'Emploi

## 📁 Fichiers Créés

### 1. `use_case_diagram.md`
Document détaillé avec tous les cas d'utilisation du système, acteurs, et relations.

### 2. `use_case_diagram.puml`
Code PlantUML pour générer le diagramme visuel.

### 3. `README_UseCase.md` (ce fichier)
Instructions pour utiliser et générer les diagrammes.

## 🎯 Résumé du Système

### **Acteurs Principaux**
- **👨‍💼 Expert Pharmaceutique** : Utilisateur principal, valide et enrichit
- **👤 Métadonneur** : Utilisateur standard, gère les documents
- **🤖 Système IA** : Automatise l'extraction et l'enrichissement
- **🔧 Administrateur** : Gère le système

### **Modules Clés**
1. **📄 Gestion Documents** - Upload, visualisation, navigation PDF
2. **🔍 Extraction & Annotation** - Reconnaissance automatique d'entités
3. **🧠 Enrichissement Intelligent** - Génération relations et Q&A
4. **🎨 Créateur Visuel Relations** - Interface graphique interactive
5. **❓ Système Q&A** - Tests et corrections des réponses IA
6. **📊 Apprentissage** - Amélioration continue par feedback expert

## 🖼️ Générer le Diagramme Visuel

### Option 1 : PlantUML Online
1. Allez sur [http://www.plantuml.com/plantuml/uml](http://www.plantuml.com/plantuml/uml)
2. Copiez le contenu de `use_case_diagram.puml`
3. Collez dans l'éditeur en ligne
4. Cliquez "Submit" pour générer l'image

### Option 2 : VS Code Extension
1. Installez l'extension "PlantUML" dans VS Code
2. Ouvrez `use_case_diagram.puml`
3. Utilisez `Alt + D` pour prévisualiser
4. Exportez en PNG/SVG

### Option 3 : CLI Local
```bash
# Si PlantUML est installé localement
java -jar plantuml.jar use_case_diagram.puml
```

## 🔍 Cas d'Utilisation Prioritaires

### **🔴 CRITIQUES (MVP)**
- Télécharger document PDF
- Extraire annotations automatiques
- Créer relations visuelles
- Enrichir avec IA

### **🟡 IMPORTANTS**
- Tester système Q&A
- Corriger réponses IA
- Auto-organiser canvas
- Comparer IA vs Expert

### **🟢 AVANCÉS**
- Analyser paragraphes libres
- Apprentissage machine avancé
- Export/Import données
- Administration fine

## 🔄 Flux Principal

```
1. 📤 Upload PDF (Métadonneur)
2. 🔍 Extraction auto (IA)
3. 🎨 Enrichissement visuel (Expert)
4. ❓ Test Q&A (Expert)
5. 📊 Apprentissage (Expert + IA)
6. 💾 Sauvegarde finale (Expert)
```

## 🏗️ Architecture Fonctionnelle

Le système suit une architecture **Expert-in-the-loop** :
- **IA génère** → **Expert valide** → **Système apprend**

### Patterns Utilisés
- **Chain of Responsibility** : Pipeline d'enrichissement
- **Strategy** : Différents types de relations
- **Observer** : Apprentissage des corrections expertes
- **Command** : Actions sur le canvas visuel

## 📈 Métriques de Performance

### Cas d'Utilisation Mesurables
- **Temps d'enrichissement** : < 30s par document
- **Précision IA** : > 85% validation expert
- **Relations créées** : ~15-25 par document
- **Q&A générées** : ~8-12 par document
- **Taux d'apprentissage** : Amélioration continue

---

*Ce diagramme de cas d'utilisation couvre l'ensemble du système d'enrichissement de documents pharmaceutiques avec IA et validation experte.*