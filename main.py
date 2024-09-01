import logging
from aiogram import Bot, Dispatcher, executor, types
import yt_dlp
import os
import time

logging.basicConfig(level=logging.INFO)

bot = Bot(token="7448556215:AAEwtFmRU0sb1SjXuOXkA03dAtJOmgT3H6s") 
dp = Dispatcher(bot)

class FilenameCollectorPP(yt_dlp.postprocessor.common.PostProcessor):
    def __init__(self):
        super(FilenameCollectorPP, self).__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information["filepath"])
        return [], information

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Приветствую! Введите название ролика, и я найду его для вас.")

@dp.message_handler()
async def search(message: types.Message):
    query = message.text
    wait_message = await message.reply('Ожидайте...')  # Сохраняем сообщение

    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': 'True',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        filename_collector = FilenameCollectorPP()
        ydl.add_post_processor(filename_collector)
        try:
            video = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            filepath = filename_collector.filenames[0]
            
            if filepath.endswith(".mp3"):
                await wait_message.delete()  # Удаляем сообщение "Ожидайте..."
                await message.reply_document(open(filepath, 'rb'))
                
                time.sleep(5)
                os.remove(filepath)
        except Exception as e:
            await wait_message.delete()  # Удаляем сообщение "Ожидайте..." в случае ошибки
            await message.reply(f"Произошла ошибка: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
