import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import FSInputFile
import cv2
from cv2 import dnn_superres
import tempfile

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Ваш токен Telegram-бота
BOT_TOKEN = "7902225195:AAHdEaG1Y7b8a_GuN0aIQbS27ufrI41-r_U"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Инициализация модели суперразрешения
sr = dnn_superres.DnnSuperResImpl_create()
path = "FSRCNN-small_x4.pb"  # Путь к модели FSRCNN
sr.readModel(path)
sr.setModel("fsrcnn", 4)  # Устанавливаем модель FSRCNN с масштабом 4

# Функция для улучшения изображения с использованием FSRCNN
def upscale_image_with_fsrcnn(image: cv2.Mat) -> cv2.Mat:
    # Улучшаем изображение с использованием модели
    result = sr.upsample(image)
    return result

# Функция для сохранения изображения с уменьшением размера файла
def save_compressed_image(image: cv2.Mat, output_path: str, compression_level: int = 50):

    # Сохраняем изображение в формате JPG с заданным уровнем сжатия
    cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, compression_level])

# Обработчик команды /start
@router.message(F.command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для улучшения изображений. Просто отправь мне фотографию, и я увеличу её разрешение с помощью модели FSRCNN!"
    )

# Обработчик команды /help
@router.message(F.command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Для использования бота просто отправь мне изображение. Я улучшю его разрешение с помощью модели FSRCNN и отправлю результат обратно."
    )

# Обработчик сообщений с фотографией
@router.message(F.photo)
async def handle_photo(message: types.Message):
    # Загружаем фотографию
    photo = message.photo[-1]  # Берём фотографию в максимальном качестве
    file_info = await bot.get_file(photo.file_id)

    # Загружаем файл
    file = await bot.download_file(file_info.file_path)

    # Сохраняем временно изображение
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(file.getvalue())
        temp_file_path = temp_file.name

    # Читаем изображение с помощью OpenCV
    image = cv2.imread(temp_file_path)

    # Улучшаем изображение
    enhanced_image = upscale_image_with_fsrcnn(image)

    # Сохраняем улучшенное изображение в сжатом формате
    enhanced_temp_file_path = "./upscaled_image_compressed.jpg"
    save_compressed_image(enhanced_image, enhanced_temp_file_path, compression_level=85)  # Уменьшаем размер

    # Отправляем улучшенное изображение пользователю
    await message.answer_photo(FSInputFile(enhanced_temp_file_path), caption="Вот ваше улучшенное изображение!")

# Запуск бота
async def main():
    dp.include_router(router)  # Подключаем маршрутизатор
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
