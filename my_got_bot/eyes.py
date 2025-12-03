"""
ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ / МОДУЛЬ:
Обрабатывает мультимодальный контент (изображения, PDF, документы) для передачи
в vision-модель Llama-4-Maverick. Конвертирует изображения в base64, извлекает
текст из документов (PDF, DOCX, TXT) и формирует правильную структуру сообщений
для API Together.ai с нативной поддержкой vision.
"""

import base64
import os
from pathlib import Path
from typing import List, Dict, Union


def process_visual_content(input_data: Union[str, Path]) -> List[Dict]:
    """
    Обрабатывает визуальный и текстовый контент.
    
    Параметры:
    - input_data: путь к файлу (str/Path) или просто текст (str)
    
    Возвращает: List[Dict] в формате для Together.ai messages API
    """
    print("\n" + "=" * 60)
    print("=== EYES ===")
    print("=" * 60)
    
    # Если это просто текст (не путь к файлу)
    if isinstance(input_data, str) and not os.path.exists(input_data):
        print("📝 Обработка текстового сообщения")
        return [{"type": "text", "text": input_data}]
    
    # Если это путь к файлу
    file_path = Path(input_data)
    
    if not file_path.exists():
        print(f"⚠️  Файл не найден: {file_path}")
        return [{"type": "text", "text": str(input_data)}]
    
    file_ext = file_path.suffix.lower()
    
    # Обработка изображений
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        print(f"🖼️  Обработка изображения: {file_path.name}")
        return process_image(file_path)
    
    # Обработка PDF
    elif file_ext == '.pdf':
        print(f"📄 Извлечение текста из PDF: {file_path.name}")
        return process_pdf(file_path)
    
    # Обработка DOCX
    elif file_ext in ['.docx', '.doc']:
        print(f"📝 Извлечение текста из DOCX: {file_path.name}")
        return process_docx(file_path)
    
    # Обработка TXT
    elif file_ext == '.txt':
        print(f"📝 Чтение текстового файла: {file_path.name}")
        return process_text_file(file_path)
    
    else:
        print(f"⚠️  Неподдерживаемый формат: {file_ext}")
        return [{"type": "text", "text": f"Файл {file_path.name} (формат не поддерживается)"}]


def process_image(file_path: Path) -> List[Dict]:
    """
    Конвертирует изображение в base64 для отправки в vision API.
    """
    try:
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
            b64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Определяем MIME тип
        ext = file_path.suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        print(f"✅ Изображение закодировано ({len(b64_image)} символов)")
        
        return [{
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{b64_image}"
            }
        }]
    
    except Exception as e:
        print(f"❌ Ошибка обработки изображения: {e}")
        return [{"type": "text", "text": f"Ошибка обработки изображения: {e}"}]


def process_pdf(file_path: Path) -> List[Dict]:
    """
    Извлекает текст из PDF файла.
    """
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(file_path)
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(f"--- Страница {page_num + 1} ---\n{page.get_text()}")
        
        doc.close()
        
        extracted_text = "\n\n".join(text_parts)
        print(f"✅ Извлечено {len(extracted_text)} символов из {len(text_parts)} страниц")
        
        return [{"type": "text", "text": f"Содержимое PDF файла '{file_path.name}':\n\n{extracted_text}"}]
    
    except ImportError:
        print("⚠️  PyMuPDF не установлен. Установите: pip install pymupdf")
        return [{"type": "text", "text": f"PDF файл '{file_path.name}' (требуется PyMuPDF для чтения)"}]
    
    except Exception as e:
        print(f"❌ Ошибка чтения PDF: {e}")
        return [{"type": "text", "text": f"Ошибка чтения PDF: {e}"}]


def process_docx(file_path: Path) -> List[Dict]:
    """
    Извлекает текст из DOCX файла.
    """
    try:
        from docx import Document
        
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        extracted_text = "\n\n".join(paragraphs)
        
        print(f"✅ Извлечено {len(extracted_text)} символов из {len(paragraphs)} параграфов")
        
        return [{"type": "text", "text": f"Содержимое DOCX файла '{file_path.name}':\n\n{extracted_text}"}]
    
    except ImportError:
        print("⚠️  python-docx не установлен. Установите: pip install python-docx")
        return [{"type": "text", "text": f"DOCX файл '{file_path.name}' (требуется python-docx для чтения)"}]
    
    except Exception as e:
        print(f"❌ Ошибка чтения DOCX: {e}")
        return [{"type": "text", "text": f"Ошибка чтения DOCX: {e}"}]


def process_text_file(file_path: Path) -> List[Dict]:
    """
    Читает обычный текстовый файл.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"✅ Прочитано {len(text)} символов")
        
        return [{"type": "text", "text": f"Содержимое файла '{file_path.name}':\n\n{text}"}]
    
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return [{"type": "text", "text": f"Ошибка чтения файла: {e}"}]
