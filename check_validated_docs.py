import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyProject.settings')
django.setup()

from rawdocs.models import RawDocument

print("=" * 80)
print("VÉRIFICATION DES DOCUMENTS VALIDÉS")
print("=" * 80)

docs = RawDocument.objects.filter(is_validated=True).order_by('id')
print(f"\nTotal documents validés: {docs.count()}\n")

for doc in docs:
    print(f"\nDocument ID: {doc.id}")
    print(f"  Titre: {doc.title or 'N/A'}")
    print(f"  Pages totales: {doc.total_pages}")
    print(f"  Fichier associé: {bool(doc.file)}")

    if doc.file:
        print(f"  Chemin du fichier: {doc.file.name}")
        try:
            file_path = doc.file.path
            print(f"  Chemin absolu: {file_path}")
            file_exists = os.path.exists(file_path)
            print(f"  Fichier existe: {'✅ OUI' if file_exists else '❌ NON'}")

            if file_exists:
                file_size = os.path.getsize(file_path)
                print(f"  Taille: {file_size / 1024:.2f} KB")
        except Exception as e:
            print(f"  ❌ Erreur d'accès au fichier: {e}")
    else:
        print(f"  ❌ Aucun fichier associé")

    print(f"  Validé le: {doc.validated_at}")
    print("-" * 80)

print("\n" + "=" * 80)
print("FIN DE LA VÉRIFICATION")
print("=" * 80)
