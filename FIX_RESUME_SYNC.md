# Correction - Synchronisation automatique du résumé lors d'annotations manuelles

## Problème résolu
Lorsque l'expert ajoutait ou supprimait des annotations manuellement dans la partie "Annoter manuellement", le résumé global du document n'était pas toujours mis à jour à cause du système de throttling (cache de 30 secondes).

## Solution appliquée

### Modifications dans `expert/views.py`

#### 1. Fonction `expert_save_manual_annotation` (ligne ~3952)
**Avant :**
```python
# résumé global (asynchrone / throttlé)
try:
    trigger_summary_regeneration_safe(page.document, request.user, 3)
except Exception as e:
    print(f"⚠️ Erreur déclenchement régénération document (manual): {e}")
```

**Après :**
```python
# Resume global (IMMEDIATE pour action manuelle expert - ignore le throttling)
try:
    REGENERATION_CACHE.pop(page.document.id, None)  # Réinitialise le cache
    trigger_summary_regeneration_safe(page.document, request.user, 0)  # Délai 0 = immédiat
except Exception as e:
    print(f"[WARNING] Erreur declenchement regeneration document (manual): {e}")
```

#### 2. Fonction `expert_delete_annotation` (ligne ~4095)
**Avant :**
```python
try:
    trigger_summary_regeneration_safe(document, request.user, 3)
except Exception as e:
    print(f"⚠️ Erreur déclenchement régénération après suppression: {e}")
```

**Après :**
```python
try:
    REGENERATION_CACHE.pop(document.id, None)  # Réinitialise le cache
    trigger_summary_regeneration_safe(document, request.user, 0)  # Délai 0 = immédiat
except Exception as e:
    print(f"[WARNING] Erreur declenchement regeneration apres suppression: {e}")
```

## Changements clés

1. **Réinitialisation du cache** : `REGENERATION_CACHE.pop(document.id, None)`
   - Supprime l'entrée du cache pour ce document
   - Permet de contourner le throttling de 30 secondes

2. **Délai immédiat** : `delay_seconds=0`
   - Pas d'attente de 3 ou 5 secondes
   - La régénération démarre immédiatement

3. **Messages d'erreur ASCII-safe**
   - Remplacement des emojis par `[WARNING]`
   - Évite les problèmes d'encodage dans les logs

## Comportement attendu maintenant

### ✅ Avant (problématique)
1. Expert ajoute une annotation → Résumé mis à jour ✓
2. Expert ajoute une 2ème annotation dans les 30 secondes → **Résumé ignoré** ✗
3. Message log : `⏰ Régénération résumé ignorée (trop récente) pour doc 284`

### ✅ Après (corrigé)
1. Expert ajoute une annotation → Résumé mis à jour immédiatement ✓
2. Expert ajoute une 2ème annotation → **Résumé mis à jour immédiatement** ✓
3. Expert supprime une annotation → **Résumé mis à jour immédiatement** ✓

## Test manuel

1. **Ouvrir un document dans la partie Expert**
2. **Ajouter plusieurs annotations manuellement** (en moins de 30 secondes)
3. **Vérifier** que le message dans les logs montre :
   ```
   [INFO] Regeneration automatique programmee dans 0s pour doc <ID>
   [OK] Regeneration resume reussie pour doc <ID>
   ```
4. **Consulter le résumé global** → Toutes les annotations doivent être reflétées

## Impact

- ✅ **Synchronisation immédiate** pour les actions manuelles de l'expert
- ✅ **Pas de perte d'annotations** dans le résumé
- ✅ **Meilleure cohérence** entre annotations et résumé
- ⚠️ **Note** : Les actions automatiques (IA) gardent le throttling pour éviter la surcharge

## Autres problèmes corrigés

### Encodage des logs
Tous les messages avec emojis et caractères accentués ont été remplacés par des versions ASCII-safe :
- `🔍` → `[INFO]`
- `✅` → `[OK]`
- `⚠️` → `[WARNING]`
- `❌` → `[ERROR]`
- `📄` → `[INFO]`
- `⏰` → `[THROTTLE]`

**Fichiers modifiés :**
- `expert/views.py`
- `rawdocs/groq_annotation_system.py`
- `rawdocs/regulatory_analyzer.py`

## Vérification

Pour vérifier que tout fonctionne :
```bash
# Dans le terminal Django, vous devriez voir :
[INFO] Regeneration automatique programmee dans 0s pour doc 284
[OK] Regeneration resume reussie pour doc 284
```

Au lieu de :
```bash
ðŸ"„ RÃ©gÃ©nÃ©ration automatique programmÃ©e dans 3s pour doc 284
â° RÃ©gÃ©nÃ©ration rÃ©sumÃ© ignorÃ©e (trop rÃ©cente) pour doc 284
```
