import requests
import base64
import json
import os
import shutil
import time

# Settings
images_folder = r"" # Your input folder location here
destination_root = r"" # Your folder location here
allowed_folders = [#Specifc Folder names here,
]

vision_model = "llava"
text_model = "gemma3:4b"  # Smaller text model

# Ensure output folders exist
os.makedirs(destination_root, exist_ok=True)
for folder in allowed_folders:
    os.makedirs(os.path.join(destination_root, folder), exist_ok=True)

# Helper: API call with retry
def api_call_with_retry(url, payload, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, json=payload, stream=True, timeout=30)
            output_text = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        output_text += data["response"]
            return output_text
        except Exception as e:
            print(f"API call failed, retrying ({retries + 1}/{max_retries})... Error: {e}")
            retries += 1
            time.sleep(1)  # small delay
    raise Exception("API call failed after retries")

# Helper: Generate description with vision model
def generate_description(image_path):
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode("utf-8")
    
    payload = {
        "model": vision_model,
        "prompt": """Describe this image in 1-2 sentences. Note whether the image could be a logo, or whether it's an old fashioned photo.
        Suggest a short catchy title.
        Categorise it into: [Funny, Historic, Personal, Reference, Other,]""",
        "images": [img_data]
    }

    return api_call_with_retry("http://localhost:11434/api/generate", payload)

from pydantic import BaseModel

# Define your schema properly
class FileSuggestion(BaseModel):
    filename: str
    folder: str

def suggest_filename_and_folder(description_text):
    # Message to send
    messages = [
        {
            "role": "user",
            "content": f"""
You are helping manage an image archive.

Given this image description:

\"\"\"{description_text}\"\"\"

Please suggest:
- A **short**, **lowercase**, **hyphenated** filename (no special characters, no spaces).
- Choose **one folder** from ONLY this list: {allowed_folders}.

Respond according to the schema provided.
"""
        }
    ]

    # Structured format
    schema = FileSuggestion.model_json_schema()

    # Now call Ollama properly
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": text_model,
            "messages": messages,
            "format": schema,
            "stream": False  # Important: no streaming for structured outputs
        },
        timeout=30
    )

    # Parse the JSON response safely
    resp_json = response.json()

    # The actual structured content is in resp_json["message"]["content"]
    structured_content = json.loads(resp_json["message"]["content"])

    # Validate against Pydantic (optional, but safest)
    file_suggestion = FileSuggestion(**structured_content)

    return file_suggestion.filename, file_suggestion.folder
# Helper: Ensure unique filename
def ensure_unique_filename(folder_path, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(folder_path, new_filename)):
        new_filename = f"{base}-{counter}{ext}"
        counter += 1
    return new_filename

# Main process
for filename in os.listdir(images_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(images_folder, filename)
        print(f"Processing {filename}...")

       

        
        try:
            # Stage 1
            description_text = generate_description(image_path)

            # Stage 2
            suggested_filename, folder = suggest_filename_and_folder(description_text)

            if folder not in allowed_folders:
                print(f"Invalid folder suggested: {folder}, skipping {filename}")
                continue

            # Ensure filename is unique
            target_folder = os.path.join(destination_root, folder)

            orig_base, orig_ext = os.path.splitext(filename)
            
            # Make sure the new filename keeps the extension
            new_filename_with_ext = f"{suggested_filename}{orig_ext}"
            
            # Ensure filename is unique in folder
            unique_filename = ensure_unique_filename(target_folder, new_filename_with_ext)
            
            # Move and rename
            destination_path = os.path.join(target_folder, unique_filename)
            shutil.move(image_path, destination_path)


            print(f"Moved to {destination_path}")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")

print("All images processed.")
