import os
import shutil
from datetime import datetime
from pathlib import Path

# === Dossiers ===
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs_asciidoc"
BACKUP_DIR = BASE_DIR / "backup_before_normalization"

# Crée le dossier de sauvegarde s’il n’existe pas
BACKUP_DIR.mkdir(exist_ok=True)

def backup_original(file_path: Path):
    """Crée une copie de sauvegarde du fichier avant modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = BACKUP_DIR / backup_name
    shutil.copy2(file_path, backup_path)
    print(f"💾 Copie de sauvegarde créée : {backup_path.name}")
    return backup_path

def normalize_asciidoc(file_path: Path):
    """Nettoie et standardise un fichier AsciiDoc (simplifié ici)"""
    print(f"🔧 Normalisation de {file_path.name}...")

    # Sauvegarde avant modification
    backup_original(file_path)

    # Lis le contenu
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Exemple de normalisation : corriger les doubles espaces et sauts inutiles
    content = content.replace(" ", " ")  # remplace les espaces insécables
    content = content.replace("\t", "    ")  # remplace tabulations
    content = "\n".join([line.rstrip() for line in content.splitlines()])  # trim right

    # Sauvegarde la version normalisée
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Normalisation terminée : {file_path.name}")

def process_all_docs():
    """Traite tous les fichiers .adoc du dossier"""
    adoc_files = list(DOCS_DIR.glob("*.adoc"))

    if not adoc_files:
        print("⚠️ Aucun fichier .adoc trouvé.")
        return

    for adoc_file in adoc_files:
        normalize_asciidoc(adoc_file)

    print("✨ Tous les fichiers ont été normalisés avec succès.")

if __name__ == "__main__":
    process_all_docs()
