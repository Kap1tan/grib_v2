from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Frame, NextPageTemplate, \
    PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
import os


class AnalysisFormatter:
    _option_to_heading_map = {
        "ЛОБ": {
            "Скошенный": "СКОШЕННЫЙ ЛОБ",
            "Прямой": "ПРЯМОЙ ЛОБ",
            "Надбровка": "НАДБРОВКА",
            "Центральная Зона": "ЦЕНТРАЛЬНАЯ ЗОНА ЛБА",
            "Боковые Зоны": "БОКОВЫЕ ЗОНЫ ЛБА",
        },
        "НАДБРОВКА": {
            "Выраженная": "НАДБРОВКА",
        },
        "ЗОНЫ_ЛБА": {
            "Комбы": "БОКОВЫЕ ЗОНЫ ЛБА",
            "Эго": "ЦЕНТРАЛЬНАЯ ЗОНА ЛБА",
        },
        "БРОВИ_НАКЛОН": {
            "Атакующие": "Атакующие Брови",
            "Домиком": "Брови Домиком",
        },
        "БРОВИ_ГУСТОТА": {
            "Густые": "Густые брови",
            "Редкие": "Редкие брови",
        },
        "БРОВИ_ВЫСОТА": {
            "Высокие": "Высоко посаженные Брови",
            "Низкие": "Низко посаженные Брови",
        },
        "БРОВИ_ФОРМА": {
            "ИЗЛОМ": "Ломаные брови",
            "Серпы": "Серповидные брови",
            "Прямые": "Прямые брови",
        },
        "ГЛАЗА_РАЗМЕР": {
            "Большие": "БОЛЬШИЕ ГЛАЗА",
            "Маленькие": "МАЛЕНЬКИЕ ГЛАЗА",
        },
        "ГЛАЗА_ГЛУБИНА": {
            "Глубоко посаженные": "ГЛУБОКО ПОСАЖЕННЫЕ ГЛАЗА",
            "Выражено": "ВЫРАЖЕННЫЕ ГЛАЗА",
        },
        "ГЛАЗА_ВЫПУКЛОСТЬ": {
            "Выпуклые": "ВЫПУКЛЫЕ ГЛАЗА",
            "Впалые": "ВПАЛЫЕ ГЛАЗА",
        },
        "ГЛАЗА_ПОСАДКА": {
            "Близкая": "БЛИЗКАЯ ПОСАДКА ГЛАЗ",
            "Широкая": "ШИРОКАЯ ПОСАДКА ГЛАЗ",
        },
        "ГЛАЗА_НАКЛОН": {
            "Вверх": "НАКЛОН ГЛАЗ ВВЕРХ",
            "Вниз": "НАКЛОН ГЛАЗ ВНИЗ",
        },
        "ГЛАЗА_ВЕКО": {
            "Нависшее": "НАВИСШЕЕ ВЕКО",
            "Спазмированное": "СПАЗМИРОВАННОЕ ВЕКО",
        },
        "НОС_ВЫСОТА": {
            "Высокий": "ВЫСОКИЙ НОС",
            "Низкий": "НИЗКИЙ НОС",
        },
        "НОС_ДЛИНА": {
            "Длинный": "ДЛИННЫЙ НОС",
            "Короткий": "КОРОТКИЙ НОС",
        },
        "НОС_ШИРИНА": {
            "Узкий": "УЗКИЙ НОС",
            "Широкий": "ШИРОКИЙ НОС",
        },
        "НОС_НАКЛОН": {
            "Вздёрнутый": "ВЗДЕРНУТЫЙ КОНЧИК НОСА",
            "Вниз": "КОНЧИК НОСА ВНИЗ",
        },
        "НОС_ПРЯМОТА": {
            "Прямая": "ПРЯМАЯ ПЕРЕНОСИЦА",
            "Впалая": "ВПАЛАЯ ПЕРЕНОСИЦА",
        },
        "НОС_ШИРИНА_ПЕРЕНОСИЦЫ": {
            "Широкая": "ШИРОКАЯ ПЕРЕНОСИЦА",
            "Узкая": "УЗКАЯ ПЕРЕНОСИЦА",
        },
        "ГУБЫ_ПОЛНОТА": {
            "Пухлые": "ПУХЛЫЕ ГУБЫ",
            "Тонкие": "ТОНКИЕ ГУБЫ",
        },
        "ГУБЫ_ДОМИНАНТА": {
            "Верхняя Полная": "ВЕРХНЯЯ ПОЛНАЯ ДОМИНАНТА",
            "Нижняя Полная": "НИЖНЯЯ ПОЛНАЯ ДОМИНАНТА",
            "Верхняя Тонкая": "ВЕРХНЯЯ ТОНКАЯ ДОМИНАНТА",
            "Нижняя Тонкая": "НИЖНЯЯ ТОНКАЯ ДОМИНАНТА",
        },
        "ГУБЫ_РАЗМЕР": {
            "Большой": "БОЛЬШОЙ РОТ",
            "Маленький": "МАЛЕНЬКИЙ РОТ",
        },
        "ГУБЫ_ЛИНИЯ": {
            "Изогнутая": "ИЗОГНУТАЯ ЛИНИЯ ГУБ",
            "Прямая": "ПРЯМАЯ ЛИНИЯ ГУБ",
        },
        "ГУБЫ_НАКЛОН": {
            "Вверх": "НАКЛОН УГОЛКОВ ГУБ",
            "Вниз": "НАКЛОН УГОЛКОВ ВНИЗ",
        },
        "ГУБЫ_ФОРМА": {
            "Слитая": "СЛИТАЯ ВЕРХНЯЯ ГУБА",
            "Раздельная": "РАЗДЕЛЬНАЯ ВЕРХНЯЯ ГУБА",
        },
        "ЧЕЛЮСТЬ_ТЯЖЕСТЬ": {
            "Тяжелая": "ТЯЖЕЛАЯ ЧЕЛЮСТЬ",
            "Легкая": "ЛЁГКАЯ ЧЕЛЮСТЬ",
        },
        "ЧЕЛЮСТЬ_ШИРИНА": {
            "Широкая": "ШИРОКАЯ ЧЕЛЮСТЬ",
            "Узкая": "УЗКАЯ ЧЕЛЮСТЬ",
        },
        "ЧЕЛЮСТЬ_КОМБИНАЦИИ": {
            "Узкая + Тяжелая": "УЗКАЯ + ТЯЖЕЛАЯ",
            "Узкая + Легкая": "УЗКАЯ + ЛЕГКАЯ",
            "Широкая + Тяжелая": "ШИРОКАЯ + ТЯЖЕЛАЯ",
            "Широкая + Легкая": "ШИРОКАЯ + ЛЕГКАЯ",
        },
        "ЧЕЛЮСТЬ_УГОЛ": {
            "Выраженный": "ВЫРАЖЕННЫЙ УГОЛ",
            "Плавный": "ПЛАВНЫЙ УГОЛ",
        },
        "ЧЕЛЮСТЬ_ВЫДВИНУТОСТЬ": {
            "Выдвинутая": "ВЫДВИНУТАЯ ЧЕЛЮСТЬ",
            "Втянутая": "ВТЯНУТАЯ ЧЕЛЮСТЬ",
        },
        "ЧЕЛЮСТЬ_ВЕРХНЯЯ": {
            "Высокая": "ВЫСОКАЯ ВЕРХНЯЯ ЧЕЛЮСТЬ",
            "Низкая": "НИЗКАЯ ВЕРХНЯЯ ЧЕЛЮСТЬ",
        },
        "ПОДБОРОДОК_ТЯЖЕСТЬ": {
            "Тяжелый": "ТЯЖЕЛЫЙ ПОДБОРОДОК",
            "Легкий": "ЛЁГКИЙ ПОДБОРОДОК",
        },
        "ПОДБОРОДОК_ВЫСТУП": {
            "Выступающий": "ВЫСТУПАЮЩИЙ ПОДБОРОДОК",
            "Втянутый": "ВТЯНУТЫЙ ПОДБОРОДОК",
        },
        "ПОДБОРОДОК_КОМБИНАЦИИ": {
            "Тяжелый + Выступающий": "ТЯЖЕЛЫЙ + ВЫСТУПАЮЩИЙ",
            "Тяжелый + Втянутый": "ТЯЖЕЛЫЙ + ВТЯНУТЫЙ",
            "Легкий + Выступающий": "ЛЁГКИЙ + ВЫСТУПАЮЩИЙ",
            "Легкий + Втянутый": "ЛЁГКИЙ + ВТЯНУТЫЙ",
        },
        "ПОДБОРОДОК_ШИРИНА": {
            "Узкий": "УЗКИЙ ПОДБОРОДОК",
            "Широкий": "ШИРОКИЙ ПОДБОРОДОК",
        },
        "ДОП_ЗАТЫЛОК": {
            "Скошенный": "СКОШЕННЫЙ ЗАТЫЛОК",
            "Выраженный": "ВЫРАЖЕННЫЙ ЗАТЫЛОК",
        },
        "ДОП_СКУЛЫ": {
            "В стороны": "ВЫРАЖЕННЫЕ СКУЛЫ В СТОРОНЫ",
            "Вперед": "ВЫРАЖЕННЫЕ СКУЛЫ ВПЕРЁД",
        },
        "ДОП_УШИ": {
            "Большие": "БОЛЬШИЕ УШИ",
            "Маленькие": "МАЛЕНЬКИЕ УШИ",
        },
        "ДОП_ШЕЯ": {
            "Длинная": "ДЛИННАЯ ШЕЯ",
            "Короткая": "КОРОТКАЯ ШЕЯ",
        },
    }

    _file_category_map = {
        "ЛОБ": "Лоб.txt",
        "НАДБРОВКА": "Лоб.txt",
        "ЗОНЫ_ЛБА": "Лоб.txt",
        "БРОВИ_НАКЛОН": "Брови.txt",
        "БРОВИ_ГУСТОТА": "Брови.txt",
        "БРОВИ_ВЫСОТА": "Брови.txt",
        "БРОВИ_ФОРМА": "Брови.txt",
        "ГЛАЗА_РАЗМЕР": "Глаза.txt",
        "ГЛАЗА_ГЛУБИНА": "Глаза.txt",
        "ГЛАЗА_ВЫПУКЛОСТЬ": "Глаза.txt",
        "ГЛАЗА_ПОСАДКА": "Глаза.txt",
        "ГЛАЗА_НАКЛОН": "Глаза.txt",
        "ГЛАЗА_ВЕКО": "Глаза.txt",
        "НОС_ВЫСОТА": "Нос.txt",
        "НОС_ДЛИНА": "Нос.txt",
        "НОС_ШИРИНА": "Нос.txt",
        "НОС_НАКЛОН": "Нос.txt",
        "НОС_ПРЯМОТА": "Нос.txt",
        "НОС_ШИРИНА_ПЕРЕНОСИЦЫ": "Нос.txt",
        "ГУБЫ_ПОЛНОТА": "Губы.txt",
        "ГУБЫ_ДОМИНАНТА": "Губы.txt",
        "ГУБЫ_РАЗМЕР": "Губы.txt",
        "ГУБЫ_ЛИНИЯ": "Губы.txt",
        "ГУБЫ_НАКЛОН": "Губы.txt",
        "ГУБЫ_ФОРМА": "Губы.txt",
        "ЧЕЛЮСТЬ_ТЯЖЕСТЬ": "Челюсть.txt",
        "ЧЕЛЮСТЬ_ШИРИНА": "Челюсть.txt",
        "ЧЕЛЮСТЬ_КОМБИНАЦИИ": "Челюсть.txt",
        "ЧЕЛЮСТЬ_УГОЛ": "Челюсть.txt",
        "ЧЕЛЮСТЬ_ВЫДВИНУТОСТЬ": "Челюсть.txt",
        "ЧЕЛЮСТЬ_ВЕРХНЯЯ": "Челюсть.txt",
        "ПОДБОРОДОК_ТЯЖЕСТЬ": "Подбородок.txt",
        "ПОДБОРОДОК_ВЫСТУП": "Подбородок.txt",
        "ПОДБОРОДОК_КОМБИНАЦИИ": "Подбородок.txt",
        "ПОДБОРОДОК_ШИРИНА": "Подбородок.txt",
        "ДОП_ЗАТЫЛОК": "Доп Черты.txt",
        "ДОП_СКУЛЫ": "Доп Черты.txt",
        "ДОП_УШИ": "Доп Черты.txt",
        "ДОП_ШЕЯ": "Доп Черты.txt",
    }

    @staticmethod
    def clean_metadata(text: str) -> str:
        """Очищает текст от метаданных формата 'информация, [DD.MM.YYYY HH:MM]'"""
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if not line.startswith('информация, ['):
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    @staticmethod
    def parse_raw_text_file(file_content: str) -> dict[str, str]:
        """Парсит данные из текстового файла в словарь {Заголовок: Описание}"""
        data = {}
        file_content = AnalysisFormatter.clean_metadata(file_content)
        lines = file_content.strip().split('\n')

        current_heading = None
        current_description_lines = []

        # Create a mapping from normalized heading to original heading for correct key storage
        normalized_heading_to_original_map = {}
        for category_map in AnalysisFormatter._option_to_heading_map.values():
            for original_heading in category_map.values():
                # Normalize the original heading for robust comparison
                normalized_heading = ' '.join(original_heading.upper().split()).strip()
                normalized_heading_to_original_map[normalized_heading] = original_heading

        for line in lines:
            stripped_line = line.strip()
            normalized_stripped_line = ' '.join(stripped_line.upper().split()).strip()

            if normalized_stripped_line in normalized_heading_to_original_map:
                # If we found a heading that matches a normalized heading
                if current_heading is not None:
                    # Filter out empty strings before joining
                    # This ensures that if the description was just blank lines, it becomes empty string
                    # If it had actual content, it will be preserved
                    cleaned_description = [d for d in current_description_lines if d.strip()]
                    data[current_heading] = "\n".join(cleaned_description).strip()

                # Use the original heading from the map as the key in the data dictionary
                current_heading = normalized_heading_to_original_map[normalized_stripped_line]
                current_description_lines = []
            elif current_heading is not None:
                current_description_lines.append(
                    line)  # Append original line to preserve formatting as much as possible

        if current_heading is not None:
            cleaned_description = [d for d in current_description_lines if d.strip()]
            data[current_heading] = "\n".join(cleaned_description).strip()
        
        return data

    @staticmethod
    def format_analysis(raw_data_maps: dict[str, dict[str, str]], selected_params: dict) -> str:
        """Форматирует данные анализа в структурированный текст на основе выбранных параметров"""
        result = []

        # Use class attributes now
        option_to_heading_map = AnalysisFormatter._option_to_heading_map
        file_category_map = AnalysisFormatter._file_category_map

        for category_key, selected_option in selected_params.items():
            if selected_option == "skip":  # Пропускаем, если параметр пропущен
                continue

            # Получаем соответствующий заголовок из map
            heading = option_to_heading_map.get(category_key, {}).get(selected_option)

            if heading:
                # Определяем, из какого файла брать данные
                file_name_for_category = file_category_map.get(category_key)
                if file_name_for_category and file_name_for_category in raw_data_maps:
                    # Получаем описание по заголовку
                    description = raw_data_maps[file_name_for_category].get(heading)
                    if description:
                        result.append(f"{heading}\n{description}\n")
                    else:
                        result.append(f"{heading}\nОписание не найдено.\n")
                else:
                    result.append(f"{heading}\nДанные для категории {category_key} не найдены.\n")
            else:
                result.append(f"{category_key}: {selected_option}\nСоответствующий заголовок не найден.\n")

        return "\n".join(result)

    @staticmethod
    def save_to_pdf(content: str, filename: str):
        """Сохраняет отформатированный текст в PDF файл с красивым оформлением"""
        # Регистрируем шрифт Bebas
        font_path = os.path.join(os.path.dirname(__file__), "Bebas.ttf")
        pdfmetrics.registerFont(TTFont('Bebas', font_path))

        # Стандартные поля документа
        margin_left = 72
        margin_right = 72
        margin_top = 72
        margin_bottom = 72

        # Определяем рамку и шаблон для полностраничных изображений
        full_page_frame = Frame(
            0, 0, A4[0], A4[1],
            leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0,
            id='full_page_frame'
        )
        full_page_template = PageTemplate(id='FullPageImage', frames=[full_page_frame])

        # Определяем рамку и шаблон для стандартного содержимого
        normal_frame = Frame(
            margin_left, margin_bottom,
            A4[0] - margin_left - margin_right,
            A4[1] - margin_top - margin_bottom,
            id='normal_frame'
        )
        normal_template = PageTemplate(id='normal', frames=[normal_frame])

        # Создаем PDF документ
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=margin_right,
            leftMargin=margin_left,
            topMargin=margin_top,
            bottomMargin=margin_bottom
        )

        # Устанавливаем шаблоны страниц для документа
        doc.addPageTemplates([full_page_template, normal_template])

        # Создаем стили - УБИРАЕМ leftIndent!
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='Bebas',
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2C3E50'),
            alignment=0  # Выравнивание по левому краю
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontName='Bebas',
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#34495E'),
            alignment=0  # Выравнивание по левому краю
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName='Bebas',
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#2C3E50'),
            alignment=0  # Выравнивание по левому краю
        )

        # Разбиваем контент на секции
        sections = content.split("\n")
        story = []

        # Добавляем каждый абзац контента как отдельный Paragraph
        for section_line in sections:
            if not section_line.strip():
                continue

            # Проверяем, является ли строка заголовком
            is_heading = False
            normalized_section_line = ' '.join(section_line.strip().upper().split())
            for category_map in AnalysisFormatter._option_to_heading_map.values():
                if normalized_section_line in [' '.join(h.upper().split()) for h in category_map.values()]:
                    is_heading = True
                    break

            if is_heading:
                story.append(Paragraph(section_line.strip(), subtitle_style))
            else:
                story.append(Paragraph(section_line.strip(), body_style))
            story.append(Spacer(1, 6))  # Добавляем небольшой отступ между абзацами

        final_story = []

        # Добавляем изображение первой страницы, используя полностраничный шаблон
        first_page_path = os.path.join(os.path.dirname(__file__), "first.jpg")
        if os.path.exists(first_page_path):
            final_story.append(NextPageTemplate('FullPageImage'))
            first_image = Image(first_page_path, width=A4[0], height=A4[1])
            final_story.append(first_image)
            final_story.append(PageBreak())

            # Добавляем пустую вторую страницу для сброса форматирования
            final_story.append(NextPageTemplate('normal'))
            final_story.append(Paragraph("", body_style))  # Пустой абзац
            final_story.append(PageBreak())

        # Добавляем основной контент
        final_story.extend(story)

        # Добавляем изображение последней страницы, используя полностраничный шаблон
        last_page_path = os.path.join(os.path.dirname(__file__), "last.jpg")
        if os.path.exists(last_page_path):
            final_story.append(NextPageTemplate('FullPageImage'))
            last_image = Image(last_page_path, width=A4[0], height=A4[1])
            final_story.append(PageBreak())
            final_story.append(last_image)
            final_story.append(
                NextPageTemplate('normal'))  # Переключаемся обратно на обычный шаблон, хотя это последняя страница

        doc.build(final_story)

        # Удаляем вторую страницу (пустую) если она была добавлена
        first_page_path = os.path.join(os.path.dirname(__file__), "first.jpg")
        if os.path.exists(first_page_path):
            AnalysisFormatter.remove_second_page(filename)

    @staticmethod
    def remove_second_page(filename: str):
        """Удаляет вторую страницу из PDF файла"""
        try:
            reader = PdfReader(filename)
            writer = PdfWriter()

            # Добавляем все страницы кроме второй (индекс 1)
            for i, page in enumerate(reader.pages):
                if i != 1:  # Пропускаем вторую страницу
                    writer.add_page(page)

            # Перезаписываем файл
            with open(filename, 'wb') as output_file:
                writer.write(output_file)
        except Exception as e:
            print(f"Ошибка при удалении второй страницы: {e}")