import asyncio
import random
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from questionnaire import QUESTIONNAIRE_STEPS, get_next_question
from analysis_formatter import AnalysisFormatter
from aiogram.exceptions import TelegramBadRequest

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot token
BOT_TOKEN = ""

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Allowed user IDs
ALLOWED_USERS = {5012986012, 804644988}

# States
class Form(StatesGroup):
    waiting_for_choice = State()

# Data structure for storing user choices
user_data = {}

# Start command handler
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("Извините, у вас нет доступа к этому боту.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать", callback_data="start")],
        [InlineKeyboardButton(text="Выбрать рандомно", callback_data="random")]
    ])
    
    await message.answer(
        "Привет! Я ваш личный помощник для составления нейротипологического портрета. "
        "Давайте начнем процесс анализа.",
        reply_markup=keyboard
    )

# Random selection handler
@dp.callback_query(lambda c: c.data == "random")
async def process_random(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ALLOWED_USERS:
        await callback_query.answer("Нет доступа")
        return

    # Generate random selections with possibility of skipping
    random_selections = {}
    skipped_parameters = []
    
    for step, data in QUESTIONNAIRE_STEPS.items():
        selected_option = random.choice(data["options"])
        # Пропускаем, если параметр надбровка выбран как "Невыраженная"
        if step == "НАДБРОВКА" and selected_option == "Невыраженная":
            skipped_parameters.append(step)
            continue
        
        # 20% chance to skip each parameter (applies after specific checks)
        if random.random() < 0.2:
            skipped_parameters.append(step)
            continue
        random_selections[step] = selected_option

    # Print results to console
    print("\nRandom Selections for User:", callback_query.from_user.id)
    print("\nSelected parameters:")
    for key, value in random_selections.items():
        print(f"{key}: {value}")
    
    if skipped_parameters:
        print("\nSkipped parameters:")
        for param in skipped_parameters:
            print(f"{param}: Пропущено")

    # Создаем и сохраняем файл с результатами
    formatter = AnalysisFormatter()
    
    raw_data_maps = {}
    # Читаем данные из файлов и сохраняем их в raw_data_maps
    with open("Лоб.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Лоб.txt"] = formatter.parse_raw_text_file(f.read())
    
    with open("Брови.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Брови.txt"] = formatter.parse_raw_text_file(f.read())
    
    with open("Глаза.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Глаза.txt"] = formatter.parse_raw_text_file(f.read())
    
    with open("Нос.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Нос.txt"] = formatter.parse_raw_text_file(f.read())
    
    with open("Губы.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Губы.txt"] = formatter.parse_raw_text_file(f.read())
    
    with open("Челюсть.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Челюсть.txt"] = formatter.parse_raw_text_file(f.read())
    
    with open("Подбородок.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Подбородок.txt"] = formatter.parse_raw_text_file(f.read())
    
    with open("Доп Черты.txt", "r", encoding="utf-8") as f:
        raw_data_maps["Доп Черты.txt"] = formatter.parse_raw_text_file(f.read())
    
    # Форматируем и сохраняем результаты
    formatted_data = formatter.format_analysis(raw_data_maps, random_selections)
    filename = f"analysis_{callback_query.from_user.id}.pdf"
    formatter.save_to_pdf(formatted_data, filename)

    # Отправляем файл пользователю
    document = FSInputFile(filename)
    await callback_query.message.answer_document(
        document=document,
        caption="Рандомные выборы были сгенерированы и сохранены в PDF файл.\n"
               "Некоторые параметры были пропущены случайным образом."
    )
    # Запускаем удаление файла с задержкой
    asyncio.create_task(delete_file_after_delay(filename, 30))

    await callback_query.message.edit_text(
        "Вы можете начать заново с помощью команды /start",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Начать заново", callback_data="start")]
        ])
    )

# Start analysis handler
@dp.callback_query(lambda c: c.data == "start")
async def start_analysis(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in ALLOWED_USERS:
        await callback_query.answer("Нет доступа")
        return

    # Initialize user data
    user_data[callback_query.from_user.id] = {}
    await state.set_state(Form.waiting_for_choice)
    await state.update_data(current_step="ЛОБ")

    # Get first question
    message_text, keyboard = await get_next_question("ЛОБ", state)
    await callback_query.message.edit_text(message_text, reply_markup=keyboard)

# Handle user choices
@dp.callback_query(Form.waiting_for_choice)
async def process_choice(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in ALLOWED_USERS:
        await callback_query.answer("Нет доступа")
        return

    user_id = callback_query.from_user.id
    data = await state.get_data()
    current_step = data.get("current_step")

    # Обрабатываем специальный случай для "НАДБРОВКА" с опцией "Невыраженная"
    if current_step == "НАДБРОВКА" and callback_query.data == "Невыраженная":
        # Не сохраняем этот параметр в user_data, так как описание не требуется
        pass
    elif callback_query.data != "skip":
        # Store the user's choice
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id][current_step] = callback_query.data

    # Get next step
    next_step = QUESTIONNAIRE_STEPS[current_step]["next"]
    
    if next_step == "FINISH":
        # Создаем и сохраняем файл с результатами
        formatter = AnalysisFormatter()
        
        raw_data_maps = {}
        # Читаем данные из файлов и сохраняем их в raw_data_maps
        with open("Лоб.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Лоб.txt"] = formatter.parse_raw_text_file(f.read())
        
        with open("Брови.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Брови.txt"] = formatter.parse_raw_text_file(f.read())
        
        with open("Глаза.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Глаза.txt"] = formatter.parse_raw_text_file(f.read())
        
        with open("Нос.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Нос.txt"] = formatter.parse_raw_text_file(f.read())
        
        with open("Губы.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Губы.txt"] = formatter.parse_raw_text_file(f.read())
        
        with open("Челюсть.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Челюсть.txt"] = formatter.parse_raw_text_file(f.read())
        
        with open("Подбородок.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Подбородок.txt"] = formatter.parse_raw_text_file(f.read())
        
        with open("Доп Черты.txt", "r", encoding="utf-8") as f:
            raw_data_maps["Доп Черты.txt"] = formatter.parse_raw_text_file(f.read())
        
        # Форматируем и сохраняем результаты
        formatted_data = formatter.format_analysis(raw_data_maps, user_data[user_id])
        filename = f"analysis_{user_id}.pdf"
        formatter.save_to_pdf(formatted_data, filename)

        # Отправляем файл пользователю
        document = FSInputFile(filename)
        await callback_query.message.answer_document(
            document=document,
            caption="Анализ завершен! Все результаты сохранены в PDF файл."
        )
        # Запускаем удаление файла с задержкой
        asyncio.create_task(delete_file_after_delay(filename, 30))
        
        await callback_query.message.edit_text(
            "Вы можете начать заново с помощью команды /start",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Начать заново", callback_data="start")]
            ])
        )
        await state.clear()
        return

    # Update state with next step
    await state.update_data(current_step=next_step)
    
    # Get next question
    message_text, keyboard = await get_next_question(next_step, state)
    try:
        await callback_query.message.edit_text(message_text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.info(f"Сообщение не изменено для пользователя {user_id}. Пропускаю редактирование.")
            await callback_query.answer() # Отвечаем на callback_query, чтобы убрать состояние "загрузки" с кнопки
        else:
            raise # Пробрасываем другие ошибки TelegramBadRequest

# Main function to run the bot
async def main():
    await dp.start_polling(bot)

async def delete_file_after_delay(filename: str, delay: int):
    await asyncio.sleep(delay)
    if os.path.exists(filename):
        os.remove(filename)
        logging.info(f"Удален файл: {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 
