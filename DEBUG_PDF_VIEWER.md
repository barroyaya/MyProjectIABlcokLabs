# 🔍 Guide de Débogage - Visualiseur PDF "Analyser les Relations dans les Documents Validés"

## 📋 Résumé du Problème

Le panneau PDF ne s'affiche pas dans l'interface "Analyser les Relations dans les Documents Validés". Seules les relations sont visibles.

## ✅ Modifications Apportées

### 1. **Logging Complet Ajouté**

Tous les fichiers JavaScript ont été enrichis avec des logs détaillés préfixés par `[nomFonction]` pour tracer le flux d'exécution :

- `[selectDocument]` - Sélection du document
- `[analyzeSelectedPages]` - Lancement de l'analyse
- `[displayAnalysisResults]` - Affichage des résultats
- `[loadPdfPageImage]` - Chargement des images PDF

### 2. **Indicateur Visuel des Fichiers PDF Disponibles**

**Backend** (`expert/views_enrichment.py`, ligne ~777) :
- Ajout du champ `pdf_file_exists` dans la réponse JSON de `get_validated_documents()`
- Vérifie physiquement si le fichier PDF existe sur le disque

**Frontend** (`view_document_annotation_json_enriched.html`) :
- Documents avec PDF manquant : bordure rouge, icône ⚠️, badge "PDF indisponible"
- Documents avec PDF disponible : bordure normale, icône 📄, badge "PDF disponible"

### 3. **Gestion d'Erreurs Améliorée**

La fonction `loadPdfPageImage()` :
- ✅ Vérifie que `selectedDocument` existe
- ✅ Vérifie que `selectedDocument.id` est défini
- ✅ Vérifie que le conteneur DOM existe
- ⚠️ En cas d'erreur de chargement d'image : cache automatiquement le panneau PDF et passe en affichage "relations uniquement"

## 🔍 Comment Déboguer

### Étape 1 : Ouvrir la Console du Navigateur

1. Appuyez sur **F12** (ou Ctrl+Shift+I)
2. Allez dans l'onglet **Console**

### Étape 2 : Tester avec un Document Valide

**Documents CONFIRMÉS avec PDF disponible :**
- ✅ ID **109** - Sunlenca (2 pages)
- ✅ ID **111** - Guidelines variations (79 pages) - **RECOMMANDÉ POUR LES TESTS**
- ✅ ID **112** - Drug Product Specifications (2 pages)
- ✅ ID **113** - Validation Verification (25 pages)
- ✅ ID **114** - Pharmaceutical Quality System (21 pages)
- ✅ ID **284** - ICH guideline Q11 (29 pages)

**Documents avec PDF MANQUANT (à éviter) :**
- ❌ ID 143, 144, 148, 171, 196, 198, 200, 201, et tous après ID 206 jusqu'à 279

### Étape 3 : Analyser les Logs Console

Voici ce que vous devriez voir dans la console après avoir sélectionné un document et cliqué sur "Analyser les relations" :

```
[selectDocument] Called with docId: 111
[selectDocument] validatedDocuments array: [...]
✅ [selectDocument] Document found: {...}
[selectDocument] Document ID: 111, Title: Guidelines...

[analyzeSelectedPages] Called
[analyzeSelectedPages] selectedDocument: {...}
[analyzeSelectedPages] Pages to analyze: [1, 2, ...]
[analyzeSelectedPages] API URL: /expert/document/111/analyze-pages-relations/
[analyzeSelectedPages] Response status: 200
[analyzeSelectedPages] Response data: {...}
✅ [analyzeSelectedPages] Analysis successful, calling displayAnalysisResults

[displayAnalysisResults] HTML rendered for X pages
[displayAnalysisResults] About to load PDF images for each page
[displayAnalysisResults] selectedDocument at this point: {...}
[displayAnalysisResults] Calling loadPdfPageImage for page 1
[displayAnalysisResults] Calling loadPdfPageImage for page 2
...

[loadPdfPageImage] Called for page 1
[loadPdfPageImage] selectedDocument: {...}
✅ [loadPdfPageImage] Loading PDF image from: /expert/page-image/111/1/
[loadPdfPageImage] Document ID: 111, Page: 1
✅ [loadPdfPageImage] PDF image loaded successfully for page 1
```

### Étape 4 : Identifier les Problèmes Courants

#### ❌ Problème 1 : selectedDocument est undefined

**Symptôme dans la console :**
```
❌ [loadPdfPageImage] selectedDocument is null or undefined
```

**Cause :** Le document n'a pas été correctement sélectionné avant l'analyse.

**Solution :** Assurez-vous de cliquer sur un document dans la liste avant de lancer l'analyse.

---

#### ❌ Problème 2 : Le fichier PDF n'existe pas

**Symptôme dans la console :**
```
⚠️ [loadPdfPageImage] Failed to load PDF image for page X
[loadPdfPageImage] URL attempted: /expert/page-image/XXX/Y/
[loadPdfPageImage] Hiding PDF panel for page X
[loadPdfPageImage] Switching to single column layout (relations only)
```

**Cause :** Le fichier PDF physique a été supprimé du disque ou n'a jamais été téléchargé.

**Solution :** Choisissez un document avec le badge "✅ PDF disponible" (vert).

---

#### ❌ Problème 3 : Le conteneur DOM n'existe pas

**Symptôme dans la console :**
```
❌ [loadPdfPageImage] Container pdf-container-X not found in DOM
```

**Cause :** Le HTML n'a pas été généré correctement.

**Solution :** Vérifiez que `displayAnalysisResults()` a bien été appelé et que le HTML a été injecté.

---

## 🧪 Test Pas à Pas Recommandé

1. **Rafraîchir la page** (F5 ou Ctrl+R)

2. **Ouvrir la console** (F12 → onglet Console)

3. **Cliquer sur "Analyser Documents Validés"** dans le menu principal

4. **Choisir le document ID 111** (Guidelines - 79 pages)
   - Devrait avoir un badge vert "✅ PDF disponible"

5. **Sélectionner le mode "Page unique"**

6. **Cocher la page 1**

7. **Cliquer sur "Analyser les relations"**

8. **Observer la console** - vous devriez voir tous les logs ci-dessus

9. **Vérifier l'affichage** :
   - Panneau gauche : Image de la page 1 du PDF avec contrôles de zoom
   - Panneau droit : Liste des relations trouvées

---

## 📊 Vérification des Documents Disponibles

Un script de vérification a été créé : `check_validated_docs.py`

**Pour l'exécuter :**

```bash
python check_validated_docs.py
```

**Résultat :** Liste tous les documents validés et indique si leur fichier PDF existe physiquement.

---

## 🆘 Si le Problème Persiste

**Collectez les informations suivantes et partagez-les :**

1. **Copie complète de la console** après avoir suivi le test pas à pas

2. **ID du document** testé

3. **Capture d'écran** de l'interface montrant le problème

4. **Logs du serveur Django** (dans le terminal où le serveur tourne)

5. **Résultat de :**
   ```bash
   python check_validated_docs.py | Select-String "Document ID: 111" -Context 0,10
   ```

---

## 📁 Fichiers Modifiés

1. **`expert/views_enrichment.py`** (lignes ~777-800)
   - Ajout de la vérification de l'existence du fichier PDF

2. **`templates/expert/view_document_annotation_json_enriched.html`**
   - Logging complet dans toutes les fonctions JavaScript
   - Indicateurs visuels pour les PDFs disponibles/manquants
   - Gestion d'erreur améliorée

3. **`check_validated_docs.py`** (nouveau fichier)
   - Script de diagnostic pour vérifier les documents

---

## ✅ Prochaines Étapes

1. Rafraîchir la page du navigateur (Ctrl+R)
2. Tester avec le document ID **111** (confirmé disponible)
3. Ouvrir la console (F12) et observer les logs
4. Rapporter tous les messages de la console

**Le système de logging détaillé permettra d'identifier précisément où le problème se produit.**

---

**Date de modification :** 2025-10-02
**Fichiers concernés :** 3
**Logs ajoutés :** ~25 points de traçage
