import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html,F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from google import genai

from src.bot.brain import process_multimodel


load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
client = genai.Client()
# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`

    welcome_text = (
        "Chirp Chirp! 🦗 I am Jhingoor, your Fitness Wingman.\n\n"
        "Send me a photo of your meal, a voice note of your workout, "
        "or just tell me how you're feeling. I'm always watching (in a good way)!"
    )
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! \n\n{welcome_text}")


@dp.message(F.text)
async def text_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        await message.answer(process_multimodel(str(message.text)))
    except Exception as e:
        logging.error(f"Error in echo_handler: {e}")
        await message.answer("An error occurred while processing your request. Please try again later.")
    except TypeError:
        logging.error("TypeError in echo_handler")
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")

@dp.message(F.photo)
async def image_handler(message: Message,bot:Bot):
    """
    Handler will process image messages
    """
    try:
        await message.answer("Analyzing your image, please wait...🦗📸")
        if message.photo:
            photo = message.photo[-1]
            photo_file = await photo.download()
            image = genai.types.ImageInput.from_file(photo_file.name)
            response = process_multimodel(photo_file.name, photo.content_type or "image/jpeg", "Provide a fitness and nutrition analysis of this image.")
            await message.answer(response.candidates[0].content.parts[0].text)
        else:
            await message.answer("Please send a valid image.")
    except Exception as e:
        logging.error(f"Error in image_handler: {e}")
        await message.answer("An error occurred while processing your image. Please try again later.")

@dp.message(F.voice)
async def voice_handler(message: Message,bot:Bot):
    """
    Handler will process voice messages
    """
    try:
        await message.answer("Listening your voice, please wait...🦗🎤")
        if message.voice:
            voice = message.voice
            voice_file = await voice.download()

            audio = genai.types.AudioInput.from_file(voice_file.name)
            response = process_multimodel(voice_file.name, voice.content_type or "audio/ogg", "Provide a fitness and wellness analysis based on this voice message.")
            await message.answer(response.candidates[0].content.parts[0].text)
        else:
            await message.answer("Please send a valid voice message.")
    except Exception as e:
        logging.error(f"Error in voice_handler: {e}")
        await message.answer("An error occurred while processing your voice message. Please try again later.")


async def main() -> None:
    logging.info("Starting bot")
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())