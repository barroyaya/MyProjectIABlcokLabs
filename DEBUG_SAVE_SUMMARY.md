# Guide de débogage - Bouton "Sauvegarder le résumé" (Partie Expert)

## Problèmes corrigés
1. Les problèmes d'encodage dans la gestion des erreurs ont été corrigés dans `expert/views.py`
2. Ajout d'un mode **rapide** (sans annotation IA) pour une sauvegarde instantanée
3. Meilleur feedback visuel avec temps écoulé et compteur d'annotations créées

## Comment tester si le bouton fonctionne maintenant

### 1. Ouvrir la console du navigateur
- **Chrome/Edge**: Appuyez sur `F12` puis cliquez sur l'onglet "Console"
- **Firefox**: Appuyez sur `F12` puis cliquez sur l'onglet "Console"

### 2. Accéder à la page d'annotation
1. Naviguez vers la partie Expert
2. Ouvrez un document
3. Cliquez sur "Voir JSON & Résumé" ou "JSON Document Complet"

### 3. Tester le bouton "Sauvegarder le résumé"
1. Modifiez le texte dans la zone de texte "Résumé Global du Document (Expert)"
2. **Choisissez le mode** :
   - ✅ **Case cochée** (par défaut) : Annotation IA automatique (10-30 secondes, plus précis)
   - ⬜ **Case décochée** : Sauvegarde rapide (1-2 secondes, sans annotation IA)
3. Cliquez sur le bouton "Sauvegarder le résumé"
4. Observez :
   - Le bouton se désactive avec un spinner
   - Le message indique le temps estimé
   - À la fin, le temps réel écoulé s'affiche

## Messages attendus

### ✅ Si ça fonctionne
Dans la console JavaScript, vous devriez voir:
- Aucune erreur rouge
- Le message de statut devrait afficher: "Résumé sauvegardé • Modifications: ..."

Dans la console du serveur (terminal où Django tourne), vous pourriez voir:
- `[WARNING] Erreur annotation IA automatique: ...` (c'est normal si l'IA n'est pas configurée)

### ❌ Si ça ne fonctionne pas
Dans la console JavaScript, vous verrez:
- Des erreurs rouges comme:
  - `TypeError: Cannot read property 'value' of null` → L'élément HTML n'existe pas
  - `SyntaxError: Unexpected token` → Problème de parsing JSON
  - `NetworkError` ou `404` → Problème de route URL
  - `500 Internal Server Error` → Erreur côté serveur Python

## ⚡ Améliorer la vitesse

### Option 1 : Désactiver l'annotation IA automatique
**La plus simple !** Décochez la case "Annotation IA automatique" avant de sauvegarder.
- ✅ **Rapide** : 1-2 secondes au lieu de 10-30 secondes
- ✅ **Suffit** pour synchroniser les entités extraites du texte
- ⚠️ **Limite** : Ne crée pas automatiquement les annotations dans le document

### Option 2 : Utiliser l'annotation IA en arrière-plan
Gardez la case cochée pour :
- ✅ Création automatique des annotations dans le document
- ✅ Détection intelligente des entités par IA
- ⏱️ Temps : 10-30 secondes selon la taille du résumé

**Astuce** : Pendant que l'IA travaille, vous pouvez ouvrir un autre onglet !

## Solutions aux problèmes courants

### Problème 1: "Cannot read property 'value' of null"
**Cause**: L'élément HTML `summary-editor` n'existe pas dans la page
**Solution**: Vérifiez que vous êtes sur la bonne page (celle avec le résumé éditable)

### Problème 2: Erreur 404 ou 403
**Cause**: La route URL n'est pas correctement configurée ou problème CSRF
**Solution**:
```javascript
// Dans la console du navigateur, vérifiez:
console.log(getCookie('csrftoken')); // Doit afficher un token, pas null
```

### Problème 3: Erreur 500 (Internal Server Error)
**Cause**: Erreur Python côté serveur
**Solution**: Regardez le terminal où Django tourne, vous verrez maintenant:
```
[ERROR] save_summary_changes error: <message d'erreur>
<traceback complet>
```

Copiez ce traceback et recherchez la ligne exacte qui cause l'erreur.

### Problème 4: Le JSON n'est pas mis à jour
**Cause**: L'éditeur JSON n'est pas initialisé
**Solution**:
```javascript
// Dans la console du navigateur:
console.log(window.editor); // Doit afficher un objet CodeMirror, pas undefined
```

## Dépendances requises

Pour que la fonction complète fonctionne, vérifiez que:
1. ✅ `extract_entities_from_text()` est définie (ligne ~2207 de views.py)
2. ✅ `extract_by_allowed_keys()` est définie (ligne ~2277 de views.py)
3. ✅ `_clean_values_for_type()` est définie (ligne ~2328 de views.py)
4. ✅ `_canonical_key()` est définie (ligne ~2483 de views.py)
5. ✅ `log_expert_action()` est définie
6. ✅ `await_ai_extract_and_annotate()` est définie (ligne ~3035 de views.py)

## Tester manuellement avec curl

Si le bouton ne fonctionne toujours pas, testez l'API directement:

```bash
# Remplacez <DOC_ID> par l'ID de votre document
# Remplacez <CSRF_TOKEN> par le token CSRF de votre session

curl -X POST http://localhost:8000/expert/annotation/document/<DOC_ID>/save-summary/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <CSRF_TOKEN>" \
  -d '{"summary_content": "Test de résumé modifié"}'
```

## Contact pour support
Si le problème persiste après avoir suivi ce guide:
1. Copiez le contenu de la console JavaScript (F12)
2. Copiez le traceback du terminal Django
3. Notez l'URL exacte de la page où vous testez
4. Partagez ces informations pour obtenir de l'aide

## Changements effectués

### Fichier: `templates/expert/view_document_annotation_json.html`
- **Ligne ~612**: Ajout d'un ID au bouton pour le contrôler via JavaScript
- **Ligne ~615**: Ajout d'une case à cocher "Annotation IA automatique"
  - Cochée par défaut = mode complet (lent mais précis)
  - Décochée = mode rapide (sauvegarde uniquement)
- **Ligne ~1196**: Fonction `saveSummaryChanges()` améliorée :
  - Désactive le bouton pendant le traitement (évite les double-clics)
  - Affiche un spinner et un message selon le mode choisi
  - Affiche le temps écoulé à la fin
  - Compte et affiche le nombre d'annotations IA créées

### Fichier: `expert/views.py`
- **Ligne ~1659**: Amélioré la gestion d'erreur pour l'annotation IA automatique
  - Ajout de `traceback.format_exc()` pour voir l'erreur complète
  - Remplacement des emojis par `[WARNING]` pour éviter les problèmes d'encodage

- **Ligne ~1837**: Amélioré la gestion d'erreur globale de `save_summary_changes`
  - Ajout de `traceback.format_exc()` pour voir l'erreur complète
  - Remplacement des emojis par `[ERROR]` pour éviter les problèmes d'encodage

Ces changements permettent maintenant de voir exactement où et pourquoi une erreur se produit.
