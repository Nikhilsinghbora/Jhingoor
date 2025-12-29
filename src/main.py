import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart
from aiogram.types import Message
from google import genai
from bot.brain import process_multimodel
from database.sync import save_jhingoor_data


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
client = genai.Client()
# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# async def on_startup():
#     print("Checking database schema... 🦗")
#     await init_db()
#     print("Jhingoor is ready!")

    
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    welcome_text = (
        "Chirp Chirp! 🦗 I am Jhingoor, your Fitness Wingman.\n\n"
        "Send me a photo of your meal, a voice note of your workout, "
        "or just tell me how you're feeling. I'm always watching (in a good way)!"
    )
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! \n\n{welcome_text}")

@dp.message()
async def handlere_all_messages(message: Message, bot: Bot) -> None:
    try:
        user_id = message.from_user.id
        folder_path = f"userdata/{user_id}"
        os.makedirs(folder_path, exist_ok=True)

        # HANDLE TEXT MESSAGES
        if message.text:
            await message.answer("Processing your text... 🦗")
            response = await process_multimodel(prompt=message.text)
            await message.answer(response)

        # HANDLE PHOTO OR VOICE
        elif message.photo or message.voice:
            user_caption = message.caption if message.caption else ""
            
            if message.photo:
                await message.answer("Analyzing your image... 🦗📸")
                media_obj = message.photo[-1]  # Get best quality
                file_path = f"{folder_path}/image.png"
                mime_type = "image/png"
                base_prompt = f"Analyze this image for fitness and nutrition. User note: {user_caption}"
            else:
                await message.answer("Listening to your audio... 🦗🎤")
                media_obj = message.voice
                file_path = f"{folder_path}/voice.ogg"
                mime_type = "audio/ogg"
                base_prompt = f"Provide a fitness analysis based on this audio. User note: {user_caption}"


            await bot.download(media_obj, destination=file_path)

            
            response = await process_multimodel(
                file_path=file_path,
                mime_type=mime_type,
                prompt=base_prompt
            )
            db_result = await save_jhingoor_data(user_id, user_caption or message.text or "Media input", response)
            if db_result:
                kcal, protein = db_result
                response += f"\n\n🦗 Logged {kcal} kcal and {protein}g protein to your daily stats!"
            await message.answer(response)

        # HANDLE UNSUPPORTED TYPES
        else:
            await message.answer("Jhingoor only understands text, images, and voice notes for now! 🦗")

    except Exception as e:
        logging.error(f"Error in handlere_all_messages: {e}")
        await message.answer("Chirp! Something went wrong. Please try again.")

async def main() -> None:
    logging.info("Starting bot")

    bot = Bot(token=TELEGRAM_TOKEN)
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())