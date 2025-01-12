from telegram.ext import *
from telegram import *
from telegram import Update
from telegram import ReplyKeyboardMarkup
from asyncio import Queue
import os
from pydub import AudioSegment
from openai import OpenAI 
import whisper

with open("token.txt") as file:
    token = file.read()

model = whisper.load_model("medium")
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard = True,one_time_keyboard = False, keyboard = [["Yes","No"]])

def get_transcribe(audio:str, language:str = "en"):
    return model.transcribe(audio = str(audio), language = language, verbose = True,fp16 = False)

        
async def start(update,context):
    await update.message.reply_text("Send me a voice message or video note and I will transcribe it for you. Forwarded messages are okay! Made by @nigelyeap, please contact me if you need help.")
    
async def handle_message(update,context):
    if update.message.text and started == True:
        if update.message.text.lower() == "yes":
            await update.message.reply_text("Thank you for your feedback! Do send another voice recording when you want!", reply_markup = ReplyKeyboardRemove())
            return
        elif update.message.text.lower() == "no":
            await update.message.reply_text("Thank you for your feedback! Do send another voice recording when you want!", reply_markup = ReplyKeyboardRemove())
            return
    if update.message.text:
        await update.message.reply_text("Please send a voice message or video note, not text. If you need help, type /start.")
    
    elif update.message.voice:
        message_text = await transcribe_vm(update,context)
        await update.message.reply_text(message_text)
        await user_review(update,context)
        return

    elif update.message.video_note:
        message_text = await transcribe_bubble(update,context)
        await update.message.reply_text(message_text)
        await user_review(update,context)
        return
 
async def user_review(update,context):
    await update.message.reply_text("Are there any mistakes?", reply_markup = reply_keyboard)
    return   
async def transcribe_vm(update: Update,context: ContextTypes.DEFAULT_TYPE) -> None:
    global started
    started = True
    voice = await context.bot.get_file(update.message.voice.file_id)
    voice_file = await voice.download_to_drive()
    await update.message.reply_text("Audio received, transcribing...")  
    audio = get_transcribe(audio = voice_file)    
    os.remove(voice_file)

    return audio.get("text","")
    
async def transcribe_bubble(update: Update,context: ContextTypes.DEFAULT_TYPE) -> None:
    global started
    started = True
    voice = await context.bot.get_file(update.message.video_note.file_id)
    voice_file = await voice.download_to_drive()
    await update.message.reply_text("Bubble received, transcribing...")  
    audio = get_transcribe(audio = voice_file)
    os.remove(voice_file)

    return audio.get("text","")
    


app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.VIDEO_NOTE,handle_message))
app.run_polling()
print("Bot started")
app.idle()