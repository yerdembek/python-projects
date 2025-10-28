# Telegram Translator Bot (Python)

## 📖 Описание
Простой бот‑переводчик для Telegram на Python. Определяет язык входящего сообщения и переводит его в выбранный целевой язык.  
Поддерживает **инлайн‑кнопки языков** под ответами и отдельную **reply‑клавиатуру** через команды `/menu` и `/menu_off`.

---

## ⚙️ Основные возможности
- 🌍 Автоопределение исходного языка.
- 🔁 Перевод текста в целевой язык (по умолчанию: `en`).
- ⚡ Быстрая смена языка через инлайн‑кнопки.
- 🎛️ Дополнительная reply‑клавиатура с популярными языками (`/menu`, `/menu_off`).
- 💬 Команды: `/start`, `/help`, `/setlang`, `/langs`, `/menu`, `/menu_off`.

---

## 🚀 Установка (Windows / PowerShell)
```bash
python -m venv .venv
.\.venv\Scriptsctivate
pip install --no-cache-dir -r requirements.txt
```
или вручную:
```bash
pip install python-telegram-bot==21.6 deep-translator==1.11.4 python-dotenv==1.0.1
```

---

## ▶️ Запуск
```bash
python main.py
```

---

## 💡 Использование
- Напишите боту любой текст — он переведёт его.  
- Сменить язык:
  - Нажмите инлайн‑кнопку под ответом, или
  - Введите `/setlang en`, или
  - Используйте большие кнопки после `/menu`.

**Команды:**

| `/start` | Приветствие, выбор языка и инлайн‑кнопки |\
| `/help` | Справка |\
| `/setlang <код>` | Установить язык перевода |\
| `/langs` | Список популярных языков |\
| `/menu` | Включить большие кнопки |\
| `/menu_off` | Скрыть большие кнопки |

---

## 🌐 Поддерживаемые языки
`en`, `ru`, `kk`, `tr`, `de`, `es`, `fr`, `zh-cn`  
(можно расширить в списке `LANG_CHOICES` в `main.py`).

---

## ⚠️ Частые проблемы
### 1. Импорты подсвечиваются красным
- Проверь, что в PyCharm/VS Code выбран **интерпретатор из `.venv`**.
- Убедись, что пакеты установлены:
  ```bash
  pip show python-telegram-bot
  pip show deep-translator
  pip show python-dotenv
  ```
- Удали файлы `telegram.py`, `dotenv.py`, `deep_translator.py`, если они есть рядом.

### 2. Ошибка с `Updater` или `polling`
- Полностью переустановите библиотеку:
  ```bash
  pip uninstall -y python-telegram-bot telegram
  pip cache purge
  pip install --no-cache-dir python-telegram-bot==21.6
  ```

### 3. Ошибка `No current event loop`
- В `main.py` уже предусмотрено создание цикла событий для Python 3.14.

---

## 🧾 Лицензия
Этот шаблон можно свободно использовать и изменять для собственных проектов.
