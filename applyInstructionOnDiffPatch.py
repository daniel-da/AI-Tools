import re
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "nom_du_modele"  # Exemple: "codestral", "llama3", etc.
PROMPT_TEMPLATE = """Voici un patch git diff pour un fichier. {instruction}
Patch :
{segment}
Réponds uniquement avec le patch modifié, sans explication."""

# Personnalisez l'instruction selon le besoin
INSTRUCTION = "Corrige les erreurs éventuelles et optimise le code modifié."

def segment_patch(patch_text):
    """Découpe le patch en segments par fichier modifié."""
    segments = re.split(r'(?=^diff --git)', patch_text, flags=re.MULTILINE)
    return [seg for seg in segments if seg.strip()]

def send_to_ollama(segment, instruction):
    """Envoie un segment à Ollama et retourne la réponse."""
    prompt = PROMPT_TEMPLATE.format(instruction=instruction, segment=segment)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        print(f"Erreur lors de l'appel à Ollama : {e}")
        return segment  # En cas d'erreur, on garde le segment original

def main():
    input_patch = "mon_patch.diff"
    output_patch = "mon_patch_modifie.diff"

    # 1. Lire le patch
    with open(input_patch, "r", encoding="utf-8") as f:
        patch_text = f.read()

    # 2. Segmenter
    segments = segment_patch(patch_text)
    print(f"{len(segments)} segments détectés.")

    # 3. Traiter chaque segment avec Ollama
    processed_segments = []
    for i, segment in enumerate(segments, 1):
        print(f"Traitement du segment {i}/{len(segments)}...")
        result = send_to_ollama(segment, INSTRUCTION)
        processed_segments.append(result)
        time.sleep(1)  # Petite pause pour éviter de surcharger Ollama

    # 4. Reconstituer le patch final
    final_patch = "\n".join(processed_segments)

    # 5. Sauvegarder le résultat
    with open(output_patch, "w", encoding="utf-8") as f:
        f.write(final_patch)

    print(f"Patch modifié sauvegardé dans : {output_patch}")

if __name__ == "__main__":
    main()
