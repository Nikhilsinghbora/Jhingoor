from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import logging
import os

from agents.prompts import SYSTEM_PROMPT

load_dotenv()
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").strip().lower() in {"1", "true", "yes", "on"}
VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID", "").strip()
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1").strip() or "us-central1"

if USE_VERTEX_AI:
    if not VERTEX_PROJECT_ID:
        raise ValueError("USE_VERTEX_AI=true requires VERTEX_PROJECT_ID in environment.")
    client = genai.Client(
        vertexai=True,
        project=VERTEX_PROJECT_ID,
        location=VERTEX_LOCATION,
    )
    logging.info(
        "LLM client initialized in Vertex AI mode (project=%s, location=%s).",
        VERTEX_PROJECT_ID,
        VERTEX_LOCATION,
    )
else:
    client = genai.Client()
    logging.info("LLM client initialized in Gemini Developer API mode.")

# Prefer AI_MODEL; fall back to GOOGLE_AI_MODEL so .env matches the rest of the bot docs.
_DEFAULT_MODEL = "gemini-2.0-flash"
AI_MODEL = (
    (os.getenv("AI_MODEL") or os.getenv("GOOGLE_AI_MODEL") or _DEFAULT_MODEL).strip()
)
if not AI_MODEL:
    AI_MODEL = _DEFAULT_MODEL
logging.info("Gemini chat model: %s", AI_MODEL)

async def process_multimodel(prompt:str,file_path:str=None,mime_type:str = None)-> str:
    try: 
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        )
        contents = [prompt]
        if file_path and mime_type:
            logging.info("Processing media input")
            logging.info(f"Received file for processing: {file_path} with MIME type: {mime_type}")
            # if mime_type.startswith("image/"):
            logging.info("Loading image input")
            print("file_path:", file_path)
            media_file = client.files.upload(file=file_path)
            contents.append(media_file)

            # elif mime_type.startswith("audio/"):
            #     logging.info("Loading audio input")
            #     audio = types.AudioChunk.from_file(file_path)
            #     contents.append(audio)

        response = client.models.generate_content(
            model=AI_MODEL,
            contents=contents,
            config=config
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.exception(
            "process_multimodel failed (model=%s). If this is HTTP 404, set AI_MODEL to a "
            "valid ID for your key (e.g. gemini-2.0-flash or gemini-2.5-flash).",
            AI_MODEL,
        )
        print("Error in process_multimodel function:", e)
        return "Sorry, I couldn't process your request at the moment."