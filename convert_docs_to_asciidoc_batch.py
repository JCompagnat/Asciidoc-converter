import os
import base64
import yaml
from openai import OpenAI
from docx import Document

# ===========================================================
# 🔧 CONFIGURATION VIA config.yaml
# ===========================================================
CONFIG_PATH = "config.yaml"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(
        f"⚠️ Fichier de configuration '{CONFIG_PATH}' introuvable.\n"
        "Crée un fichier config.yaml à la racine du projet avec ce contenu :\n\n"
        "openai:\n"
        "  api_key: sk-xxxx\n"
        "paths:\n"
        "  input_folder: docs_input\n"
        "  output_folder: docs_asciidoc\n"
        "  images_folder: images_exported\n"
        "model: gpt-5\n"
    )

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["openai"]["api_key"]
model_name = config.get("model", "gpt-5")
input_folder = config["paths"]["input_folder"]
output_folder = config["paths"]["output_folder"]
images_folder = os.path.join(output_folder, config["paths"]["images_folder"])

os.makedirs(output_folder, exist_ok=True)
os.makedirs(images_folder, exist_ok=True)

client = OpenAI(api_key=api_key)

# ===========================================================
# 1️⃣ EXTRACTION SEQUENTIELLE (texte + images dans l’ordre)
# ===========================================================
def extract_docx_sequence(docx_path, base_name):
    """
    Extrait le texte et les images d’un document Word dans l’ordre d’apparition.
    """
    doc = Document(docx_path)
    sequence = []
    image_counter = 0

    for block in doc.element.body:
        # --- Paragraphe ---
        if block.tag.endswith("p"):
            paragraph = next((p for p in doc.paragraphs if p._p == block), None)
            if paragraph:
                # Texte du paragraphe
                try:
                    text = paragraph.text.strip()
                    if text:
                        sequence.append({"type": "text", "content": text})
                except Exception as e:
                    print(f"⚠️ Erreur lecture paragraphe : {e}")

                # Images contenues dans le paragraphe
                for run in getattr(paragraph, "runs", []):
                    try:
                        if run.element.xpath(".//a:blip"):
                            image_counter += 1
                            img_name = f"{base_name}_img{image_counter:02d}.png"
                            img_path = os.path.join(images_folder, img_name)
                            extract_image_from_run(run, img_path)
                            sequence.append({"type": "image", "content": img_name})
                    except Exception as e:
                        print(f"⚠️ Erreur extraction image : {e}")

        # --- Tableau ---
        elif block.tag.endswith("tbl"):
            sequence.append({"type": "text", "content": "[Tableau détecté ici]"})
    return sequence


# ===========================================================
# 2️⃣ EXTRACTION D’UNE IMAGE À PARTIR D’UN RUN
# ===========================================================
def extract_image_from_run(run, img_path):
    """
    Extrait une image intégrée dans un paragraphe et la sauvegarde sur disque.
    """
    try:
        blip = run.element.xpath(".//a:blip")
        if not blip:
            return
        rId = blip[0].get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        image_part = run.part.related_parts[rId]
        with open(img_path, "wb") as f:
            f.write(image_part.blob)
    except Exception as e:
        print(f"⚠️ Erreur lors de l’extraction d’image : {e}")


# ===========================================================
# 3️⃣ ENVOI À GPT POUR CONVERSION EN ASCIIDOC
# ===========================================================
def convert_sequence_to_asciidoc(sequence, filename):
    """
    Envoie la séquence texte + images à GPT-5 Vision pour reconstitution AsciiDoc.
    """
    print(f"🧠 Conversion séquentielle du document : {filename}")

    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un expert en documentation technique. "
                "Reconstitue la procédure en AsciiDoc à partir du texte et des images fournis "
                "dans l’ordre d’apparition. Conserve la logique originale et insère chaque image "
                "à l’endroit approprié dans le flux. Structure le tout avec des titres et sous-sections clairs."
            ),
        },
        {
            "role": "user",
            "content": [],
        },
    ]

    for item in sequence:
        if item["type"] == "text":
            messages[1]["content"].append({"type": "text", "text": item["content"]})
        elif item["type"] == "image":
            img_path = os.path.join(images_folder, item["content"])
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })

    response = client.chat.completions.create(model=model_name, messages=messages)
    return response.choices[0].message.content


# ===========================================================
# 4️⃣ TRAITEMENT GLOBAL DES FICHIERS .DOCX
# ===========================================================
def process_all_docx():
    for filename in os.listdir(input_folder):
        if not filename.endswith(".docx"):
            continue

        base_name = os.path.splitext(filename)[0]
        file_path = os.path.join(input_folder, filename)

        print(f"📄 Lecture du document : {filename}")
        sequence = extract_docx_sequence(file_path, base_name)
        adoc_text = convert_sequence_to_asciidoc(sequence, filename)

        output_path = os.path.join(output_folder, f"{base_name}.adoc")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(adoc_text)

        print(f"✅ AsciiDoc créé : {output_path}")
        print(f"📸 {sum(1 for i in sequence if i['type']=='image')} image(s) intégrée(s)\n")


# ===========================================================
if __name__ == "__main__":
    process_all_docx()
