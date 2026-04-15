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
# Vertex AI published model IDs typically include a version suffix (e.g. gemini-2.0-flash-001);
# the Gemini Developer API accepts short names like gemini-2.0-flash.
_DEFAULT_MODEL_VERTEX = "gemini-2.0-flash-001"
_DEFAULT_MODEL_DEVELOPER = "gemini-2.0-flash"
_DEFAULT_MODEL = _DEFAULT_MODEL_VERTEX if USE_VERTEX_AI else _DEFAULT_MODEL_DEVELOPER


def _legacy_model_remap(use_vertex: bool) -> dict[str, str]:
    # v1beta generateContent rejects unversioned "gemini-1.5-*" IDs on the Developer API;
    # on Vertex, prefer a published snapshot id for the same tier.
    flash_target = _DEFAULT_MODEL_VERTEX if use_vertex else _DEFAULT_MODEL_DEVELOPER
    return {
        "gemini-1.5-flash": flash_target,
        "gemini-1.5-flash-8b": flash_target,
        "gemini-1.5-pro": "gemini-1.5-pro-002",
    }


_LEGACY_GEMINI_MODELS: dict[str, str] = _legacy_model_remap(USE_VERTEX_AI)


def _normalize_gemini_model_id(raw: str) -> str:
    m = raw.strip()
    if m.startswith("models/"):
        m = m[len("models/") :].strip()
    if not m:
        return _DEFAULT_MODEL
    resolved = _LEGACY_GEMINI_MODELS.get(m, m)
    if resolved != m:
        logging.info(
            "Remapped legacy Gemini model id %r -> %r (%s).",
            m,
            resolved,
            "Vertex AI" if USE_VERTEX_AI else "Gemini Developer API",
        )
    return resolved


_raw_model = (os.getenv("AI_MODEL") or os.getenv("GOOGLE_AI_MODEL") or _DEFAULT_MODEL).strip()
AI_MODEL = _normalize_gemini_model_id(_raw_model or _DEFAULT_MODEL)
logging.info(
    "Gemini chat model: %s (provider=%s)",
    AI_MODEL,
    "Vertex AI" if USE_VERTEX_AI else "Gemini Developer API",
)

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
            "process_multimodel failed (model=%s, vertex=%s). If this is HTTP 404, set AI_MODEL to a "
            "model your project supports (Vertex: see Generative AI models in GCP console; "
            "Developer API: e.g. gemini-2.0-flash).",
            AI_MODEL,
            USE_VERTEX_AI,
        )
        print("Error in process_multimodel function:", e)
        return "Sorry, I couldn't process your request at the moment."