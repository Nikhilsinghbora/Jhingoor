from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import logging
import os

load_dotenv()
client = genai.Client()

AI_MODEL = os.getenv("AI_MODEL")
SYSTEM_PROMPT = "You're a helpful fitness assistant named Jhingoor. Provide concise and friendly responses related to fitness, nutrition, and wellness."

async def process_multimodel(file_path:str,mime_type:str,prompt:str)-> str:
    try: 
        if mime_type.startswith("image/"):
            logging.info("Processing image input")
            image = types.ImageInput.from_file(file_path)
            response = client.models.generate_content(
                model=AI_MODEL,
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    system_instruction=SYSTEM_PROMPT,
                )
            )
        elif mime_type.startswith("audio/"):
            logging.info("Processing audio input")
            audio = types.AudioInput.from_file(file_path)
            response = client.models.generate_content(
                model=AI_MODEL,
                contents=[prompt, audio],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    system_instruction=SYSTEM_PROMPT,
                )
            )
        else:
            logging.info("Processing text input")
            response = client.models.generate_content(
                model=AI_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    system_instruction=SYSTEM_PROMPT,
                )
            )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Error in process_multimodel function: {e}")
        print("Error in process_multimodel function:", e)
        return "Sorry, I couldn't process your request at the moment."