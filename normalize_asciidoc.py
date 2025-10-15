#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalize_asciidoc.py
-------------------------------------
Normalise un fichier AsciiDoc :
- crée une sauvegarde horodatée avant modification
- corrige les chemins d'images pour correspondre aux fichiers existants
- nettoie les titres, métadonnées et encodages éventuels

Usage :
    python normalize_asciidoc.py "docs_asciidoc/Création de compte PACS.adoc"
"""

import os
import re
import sys
import shutil
from datetime import datetime
from difflib import get_close_matches


def create_backup(file_path: str):
    """Crée une copie de sauvegarde du fichier AsciiDoc avant modification"""
    backup_dir = os.path.join(os.path.dirname(__file__), "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(file_path)}.bak_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)

    shutil.copy(file_path, backup_path)
    print(f"💾 Copie de sauvegarde créée : {backup_path}")


def normalize_image_paths(adoc_path: str):
    """Corrige les références d’images dans le .adoc pour qu’elles pointent vers les bons fichiers."""
    base_dir = os.path.dirname(adoc_path)
    images_dir = os.path.join(base_dir, "images_exported")
    if not os.path.exists(images_dir):
        print(f"⚠️ Dossier d’images introuvable : {images_dir}")
        return

    # Liste des fichiers disponibles dans images_exported
    image_files = {os.path.basename(f): f for f in os.listdir(images_dir)}

    # Lire le contenu du fichier AsciiDoc
    with open(adoc_path, "r", encoding="utf-8") as f:
        content = f.read()

    def replace_image_ref(match):
        ref = match.group(1).strip()
        desc = match.group(2).strip() if match.group(2) else ""
        base_name = os.path.basename(ref)

        if base_name in image_files:
            return f"image::{base_name}[{desc}]"
        else:
            # Essaye de trouver un nom similaire (tolérance orthographique)
            similar = get_close_matches(base_name, image_files.keys(), n=1, cutoff=0.6)
            if similar:
                print(f"🔄 Correction : {base_name} → {similar[0]}")
                return f"image::{similar[0]}[{desc}]"
            else:
                print(f"⚠️ Image non trouvée : {base_name}")
                return match.group(0)

    # Cherche toutes les références image::...
    new_content = re.sub(r"image::([^\[]+)\[([^\]]*)\]", replace_image_ref, content)

    # Sauvegarde le contenu normalisé
    with open(adoc_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ Normalisation des chemins d’images terminée.")


def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python normalize_asciidoc.py <fichier.adoc>")
        sys.exit(1)

    adoc_path = sys.argv[1]
    if not os.path.exists(adoc_path):
        print(f"❌ Fichier introuvable : {adoc_path}")
        sys.exit(1)

    # Étape 1 : sauvegarde
    create_backup(adoc_path)

    # Étape 2 : normalisation images
    normalize_image_paths(adoc_path)

    print("✨ Normalisation terminée avec succès.")


if __name__ == "__main__":
    main()
