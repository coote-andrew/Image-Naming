# Image Sorter Using Ollama Vision and Text Models
This is a simple Python project that automatically sorts and renames images based on their content.

It uses:
- A vision model to describe each image.
- A text model to suggest a filename and a category folder.
Both models are run locally using Ollama.

## How it Works
It looks at each .jpg, .jpeg, or .png file in your input folder.
It generates a short description of the image (e.g., "A vintage photo of a family gathering").
It then asks for:
A short, hyphenated filename.
A folder from a list you specify (like Funny, Historic, Personal).
It moves and renames the file accordingly.

# Requirements
Python 3.10+
Ollama installed and running

Python packages:
requests
pydantic

Install dependencies with:
```
pip install requests pydantic
```

## Setting up Ollama
You need to install Ollama — it's a local LLM server.


Steps:
Download Ollama from https://ollama.com/ and install it.
Run Ollama. It must stay running in the background.

Download the required models:
```
ollama pull llava
ollama pull gemma3:4b
```

llava is used for image understanding (vision).
gemma3:4b is used for filename/folder suggestion (text).

### Configuration
In the script, you must configure:

```
images_folder = r"your\path\to\images"
destination_root = r"your\path\to\sorted\output"
allowed_folders = ["Funny", "Historic", "Personal", "Reference", "Other"]
```

images_folder — where your unsorted images are.
destination_root — where you want the sorted images saved.
allowed_folders — must match exactly (case-sensitive) what the AI can pick from.

## Running the Script
(in case you're not familiar with Git - just click on the python file and then download in the triple dots to get the image_classifier file
Otherwise use git clone)

Once you've set up your folders and Ollama is running:
```
python image_classifier.py
```

It will:
Process each image.
Generate descriptions.
Suggest filenames and folders.
Move and rename the images into the right folders.
You’ll see live progress printed out.

## Notes
If an API call to Ollama fails, the script will retry up to 3 times.
Filenames are automatically made unique if a file with the same name already exists.
Only images (.jpg, .jpeg, .png) are processed.
If the model suggests an invalid folder (not in your allowed list), the file is skipped.
