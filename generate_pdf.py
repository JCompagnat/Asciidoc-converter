import subprocess
import os
from pathlib import Path

# Répertoire racine du projet (même que le script)
ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR / "docs_asciidoc"
THEMES_DIR = ROOT_DIR / "themes"
FONTS_DIR = THEMES_DIR / "fonts"

def generate_pdf(adoc_file: Path):
    pdf_file = adoc_file.with_suffix(".pdf")

    print(f"🖨️ Génération du PDF : {adoc_file.name}")

    cmd = [
        "asciidoctor-pdf",
        "-a", "pdf-theme=pacs-theme.yml",
        "-a", f"pdf-themesdir={THEMES_DIR}",
        "-a", f"pdf-fontsdir={FONTS_DIR}",
        str(adoc_file),
        "-o", str(pdf_file),
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ PDF généré : {pdf_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")

if __name__ == "__main__":
    for adoc in DOCS_DIR.glob("*.adoc"):
        generate_pdf(adoc)
