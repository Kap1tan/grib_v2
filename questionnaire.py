from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

# Define all questionnaire steps and their options
QUESTIONNAIRE_STEPS = {
    "ЛОБ": {
        "options": ["Скошенный", "Прямой"],
        "next": "НАДБРОВКА"
    },
    "НАДБРОВКА": {
        "options": ["Выраженная", "Невыраженная"],
        "next": "ЗОНЫ_ЛБА"
    },
    "ЗОНЫ_ЛБА": {
        "options": ["Комбы", "Эго"],
        "next": "БРОВИ_НАКЛОН"
    },
    "БРОВИ_НАКЛОН": {
        "options": ["Атакующие", "Домиком"],
        "next": "БРОВИ_ГУСТОТА"
    },
    "БРОВИ_ГУСТОТА": {
        "options": ["Густые", "Редкие"],
        "next": "БРОВИ_ВЫСОТА"
    },
    "БРОВИ_ВЫСОТА": {
        "options": ["Высокие", "Низкие"],
        "next": "БРОВИ_ФОРМА"
    },
    "БРОВИ_ФОРМА": {
        "options": ["Излом", "Серпы", "Прямые"],
        "next": "ГЛАЗА_РАЗМЕР"
    },
    "ГЛАЗА_РАЗМЕР": {
        "options": ["Большие", "Маленькие"],
        "next": "ГЛАЗА_ГЛУБИНА"
    },
    "ГЛАЗА_ГЛУБИНА": {
        "options": ["Глубоко", "Выражено"],
        "next": "ГЛАЗА_ВЫПУКЛОСТЬ"
    },
    "ГЛАЗА_ВЫПУКЛОСТЬ": {
        "options": ["Выпуклые", "Впалые"],
        "next": "ГЛАЗА_ПОСАДКА"
    },
    "ГЛАЗА_ПОСАДКА": {
        "options": ["Близкая", "Широкая"],
        "next": "ГЛАЗА_НАКЛОН"
    },
    "ГЛАЗА_НАКЛОН": {
        "options": ["Вверх", "Вниз"],
        "next": "ГЛАЗА_ВЕКО"
    },
    "ГЛАЗА_ВЕКО": {
        "options": ["Нависшее", "Спазмированное"],
        "next": "НОС_ВЫСОТА"
    },
    "НОС_ВЫСОТА": {
        "options": ["Высокий", "Низкий"],
        "next": "НОС_ДЛИНА"
    },
    "НОС_ДЛИНА": {
        "options": ["Длинный", "Короткий"],
        "next": "НОС_ШИРИНА"
    },
    "НОС_ШИРИНА": {
        "options": ["Узкий", "Широкий"],
        "next": "НОС_НАКЛОН"
    },
    "НОС_НАКЛОН": {
        "options": ["Вздернутый", "Вниз"],
        "next": "НОС_ПРЯМОТА"
    },
    "НОС_ПРЯМОТА": {
        "options": ["Прямая", "Впалая"],
        "next": "НОС_ШИРИНА_ПЕРЕНОСИЦЫ"
    },
    "НОС_ШИРИНА_ПЕРЕНОСИЦЫ": {
        "options": ["Широкая", "Узкая"],
        "next": "ГУБЫ_ПОЛНОТА"
    },
    "ГУБЫ_ПОЛНОТА": {
        "options": ["Пухлые", "Тонкие"],
        "next": "ГУБЫ_ДОМИНАНТА"
    },
    "ГУБЫ_ДОМИНАНТА": {
        "options": ["Верхняя Полная", "Нижняя Полная", "Верхняя Тонкая", "Нижняя Тонкая"],
        "next": "ГУБЫ_РАЗМЕР"
    },
    "ГУБЫ_РАЗМЕР": {
        "options": ["Большой", "Маленький"],
        "next": "ГУБЫ_ЛИНИЯ"
    },
    "ГУБЫ_ЛИНИЯ": {
        "options": ["Изогнутая", "Прямая"],
        "next": "ГУБЫ_НАКЛОН"
    },
    "ГУБЫ_НАКЛОН": {
        "options": ["Вверх", "Вниз"],
        "next": "ГУБЫ_ФОРМА"
    },
    "ГУБЫ_ФОРМА": {
        "options": ["Слитая", "Раздельная"],
        "next": "ЧЕЛЮСТЬ_ТЯЖЕСТЬ"
    },
    "ЧЕЛЮСТЬ_ТЯЖЕСТЬ": {
        "options": ["Тяжелая", "Легкая"],
        "next": "ЧЕЛЮСТЬ_ШИРИНА"
    },
    "ЧЕЛЮСТЬ_ШИРИНА": {
        "options": ["Широкая", "Узкая"],
        "next": "ЧЕЛЮСТЬ_КОМБИНАЦИИ"
    },
    "ЧЕЛЮСТЬ_КОМБИНАЦИИ": {
        "options": ["Узкая + Тяжелая", "Узкая + Легкая", "Широкая + Тяжелая", "Широкая + Легкая"],
        "next": "ЧЕЛЮСТЬ_УГОЛ"
    },
    "ЧЕЛЮСТЬ_УГОЛ": {
        "options": ["Прямой", "Плавный"],
        "next": "ЧЕЛЮСТЬ_ВЫДВИНУТОСТЬ"
    },
    "ЧЕЛЮСТЬ_ВЫДВИНУТОСТЬ": {
        "options": ["Выдвинутая", "Втянутая"],
        "next": "ЧЕЛЮСТЬ_ВЕРХНЯЯ"
    },
    "ЧЕЛЮСТЬ_ВЕРХНЯЯ": {
        "options": ["Высокая", "Низкая"],
        "next": "ПОДБОРОДОК_ТЯЖЕСТЬ"
    },
    "ПОДБОРОДОК_ТЯЖЕСТЬ": {
        "options": ["Тяжелый", "Легкий"],
        "next": "ПОДБОРОДОК_ВЫСТУП"
    },
    "ПОДБОРОДОК_ВЫСТУП": {
        "options": ["Выступающий", "Втянутый"],
        "next": "ПОДБОРОДОК_КОМБИНАЦИИ"
    },
    "ПОДБОРОДОК_КОМБИНАЦИИ": {
        "options": ["Тяжелый + Выступающий", "Тяжелый + Втянутый", "Легкий + Выступающий", "Легкий + Втянутый"],
        "next": "ПОДБОРОДОК_ШИРИНА"
    },
    "ПОДБОРОДОК_ШИРИНА": {
        "options": ["Узкий", "Широкий"],
        "next": "ДОП_ЗАТЫЛОК"
    },
    "ДОП_ЗАТЫЛОК": {
        "options": ["Скошенный", "Выраженный"],
        "next": "ДОП_СКУЛЫ"
    },
    "ДОП_СКУЛЫ": {
        "options": ["В стороны", "В перед"],
        "next": "ДОП_УШИ"
    },
    "ДОП_УШИ": {
        "options": ["Большие", "Маленькие"],
        "next": "ДОП_ШЕЯ"
    },
    "ДОП_ШЕЯ": {
        "options": ["Длинная", "Короткая"],
        "next": "FINISH"
    }
}

def create_keyboard(options, skip=True):
    keyboard = []
    for option in options:
        keyboard.append([InlineKeyboardButton(text=option, callback_data=option)])
    if skip:
        keyboard.append([InlineKeyboardButton(text="Пропустить", callback_data="skip")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def get_next_question(current_step: str, state: FSMContext) -> tuple[str, InlineKeyboardMarkup]:
    if current_step == "FINISH":
        return "FINISH", None
    
    step_data = QUESTIONNAIRE_STEPS[current_step]
    options = step_data["options"]
    next_step = step_data["next"]
    
    # Get the category name (part before the underscore)
    category = current_step.split("_")[0]
    
    # Create the message text
    message_text = f"{category} ✔️\n\n"
    if "_" in current_step:
        subcategory = current_step.split("_")[1].lower()
        message_text += f"Выберите {subcategory}:"
    
    return message_text, create_keyboard(options)

def get_step_title(step: str) -> str:
    if "_" in step:
        return step.split("_")[1].lower()
    return step.lower() 