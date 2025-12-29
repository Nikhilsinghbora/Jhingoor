from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import logging
import os

from agents.prompts import SYSTEM_PROMPT

load_dotenv()
client = genai.Client()

AI_MODEL = os.getenv("AI_MODEL")

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
        logging.error(f"Error in process_multimodel function: {e}")
        print("Error in process_multimodel function:", e)
        return "Sorry, I couldn't process your request at the moment."