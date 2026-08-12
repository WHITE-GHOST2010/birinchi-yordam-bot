import asyncio
import os
import logging
import re
import html
from datetime import datetime, time, timedelta
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    LabeledPrice, ContentType, TelegramObject
)
from typing import Callable, Dict, Any, Awaitable

class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            is_banned, ban_msg = database.is_user_banned(user.id)
            if is_banned:
                contact_info = f"Murojaat uchun: @{ADMIN_USERNAME}" if (ADMIN_USERNAME and ADMIN_USERNAME != "YOUR_ADMIN_USERNAME") else "Murojaat uchun administratorga yozing."
                if isinstance(event, types.Message):
                    await event.answer(
                        f"❌ <b>Siz botdan foydalanishdan chetlashtirilgansiz (Banned)!</b>\n\n"
                        f"{ban_msg}\n\n"
                        f"⚠️ {contact_info}",
                        parse_mode="HTML"
                    )
                elif isinstance(event, types.CallbackQuery):
                    await event.answer(
                        f"Siz bloklangansiz.\n{ban_msg}",
                        show_alert=True
                    )
                return
        return await handler(event, data)

class FsmResetMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, types.Message) and event.text:
            skip_texts = [
                "📋 Holatlar ro'yxati", "🚨 Favqulodda raqamlar",
                "📚 Kasalliklar Ro'yxati (100+)", "💬 AI Konsultatsiya (Chat)",
                "🏥 Eng yaqin kasalxona", "💎 Premium olish",
                "👤 Tibbiy Profilim", "💊 Dori Eslatmalari",
                "⚖️ Sog'liq Kalkulyatori", "🔔 Kunlik Maslahatlar"
            ]
            if event.text in skip_texts or event.text.startswith('/'):
                state = data.get("state")
                if state:
                    await state.clear()
        return await handler(event, data)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types

# Ma'lumotlarni import qilamiz
from data import FIRST_AID_DATA, DISEASES
import database

# ═══════════════════════════════════════════════════════════════════
# MARKDOWN → HTML CONVERTER
# ═══════════════════════════════════════════════════════════════════

def markdown_to_html(text: str) -> str:
    """Markdown formatidagi matnni Telegram HTML formatiga xavfsiz o'tkazish"""
    if not text:
        return ""
    text = html.escape(text)
    code_blocks = []
    def save_code_block(match):
        code = match.group(1)
        code_blocks.append(code)
        return f"___CODE_BLOCK_{len(code_blocks)-1}___"
    text = re.sub(r'```(?:[a-zA-Z0-9_-]+)?\n?(.*?)\n?```', save_code_block, text, flags=re.DOTALL)
    inline_codes = []
    def save_inline_code(match):
        code = match.group(1)
        inline_codes.append(code)
        return f"___INLINE_CODE_{len(inline_codes)-1}___"
    text = re.sub(r'`(.*?)`', save_inline_code, text)
    text = re.sub(r'^#{1,6}\s+(.*?)$', r'<b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
    text = re.sub(r'\*(?!\s)([^\*]+?)(?<!\s)\*', r'<i>\1</i>', text)
    text = re.sub(r'(^|\s)_(?!\s)([^_]+?)(?<!\s)_(?=$|\s|[.,!?;:])', r'\1<i>\2</i>', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    for i, code in enumerate(inline_codes):
        text = text.replace(f"___INLINE_CODE_{i}___", f"<code>{code}</code>")
    for i, code in enumerate(code_blocks):
        text = text.replace(f"___CODE_BLOCK_{i}___", f"<pre>{code}</pre>")
    return text

# ═══════════════════════════════════════════════════════════════════
# ASOSIY SOZLAMALAR
# ═══════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
load_dotenv()

TOKEN          = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID       = os.getenv("ADMIN_ID", "YOUR_ADMIN_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "YOUR_ADMIN_USERNAME")
CARD_NUMBER         = os.getenv("CARD_NUMBER", "8600 1234 5678 9012")
CARD_NAME           = os.getenv("CARD_NAME", "Karta Egasi Ismi")
PROVIDER_TOKEN      = os.getenv("PROVIDER_TOKEN", "")  # Feature 6: To'lov uchun (eski)
MINI_APP_URL        = os.getenv("MINI_APP_URL", "")
PREMIUM_STARS_PRICE = int(os.getenv("PREMIUM_STARS_PRICE", "50"))  # Stars narxi (default: 50 ⭐)


if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    raise ValueError("Iltimos, .env fayliga haqiqiy BOT_TOKEN ni kiriting!")

# Gemini AI sozlamalari
gemini_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

bot = Bot(token=TOKEN)
dp  = Dispatcher(storage=MemoryStorage())  # FSM uchun MemoryStorage

# ═══════════════════════════════════════════════════════════════════
# FSM STATES (Feature 1: Tibbiy profil, Feature 2: Eslatma)
# ═══════════════════════════════════════════════════════════════════

class MedicalProfileStates(StatesGroup):
    blood_group       = State()
    age               = State()
    weight            = State()
    height            = State()
    chronic_diseases  = State()
    allergies         = State()

class ReminderStates(StatesGroup):
    medicine_name = State()
    times         = State()

class BmiStates(StatesGroup):
    weight = State()
    height = State()

class WaterStates(StatesGroup):
    weight = State()

class AiChatStates(StatesGroup):
    chatting = State()

class PaymentStates(StatesGroup):
    waiting_for_receipt = State()

# ═══════════════════════════════════════════════════════════════════
# GEMINI AI
# ═══════════════════════════════════════════════════════════════════

GEMINI_SYSTEM_INSTRUCTION = (
    "Siz o'zbek tilida gaplashadigan Birinchi Yordam va Salomatlik bo'yicha aqlli sun'iy intellekt yordamchisiz. "
    "Foydalanuvchilarga favqulodda vaziyatlarda birinchi yordam ko'rsatish, salomatlik, foydali ovqatlar, vitaminlar, "
    "tavsiya etiladigan xavfsiz dorilar va shifobaxsh mashqlar haqida batafsil va to'g'ri maslahatlar bering. "
    "Agar savol tibbiyot yoki salomatlikka aloqador bo'lmasa, muloyimlik bilan faqat salomatlik va birinchi yordamga oid savollarga javob berishingizni ayting. "
    "Har doim javoblaringiz oxirida, zarur bo'lsa, shifokor bilan maslahatlashishni va jiddiy holatlarda 103 ga qo'ng'iroq qilishni eslatib o'ting."
)

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

async def _try_generate(prompt: str, model: str) -> str:
    response = await gemini_client.aio.models.generate_content(
        model=model,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            system_instruction=GEMINI_SYSTEM_INSTRUCTION,
            temperature=0.7,
        )
    )
    return response.text

async def get_gemini_response(prompt: str) -> str:
    if not gemini_client:
        return "⚠️ Sun'iy intellekt hozir sozlanmagan.\nIltimos, administratorga murojaat qiling."
    last_error = None
    for model in GEMINI_MODELS:
        try:
            logging.info(f"Model sinashda: {model}")
            return await _try_generate(prompt, model)
        except Exception as e:
            err = str(e)
            if "429" in err or "404" in err or "RESOURCE_EXHAUSTED" in err or "NOT_FOUND" in err:
                logging.warning(f"{model} ishlamadi, keyingisiga o'tilmoqda...")
                last_error = e
                continue
            return _handle_gemini_error(e)
    return _handle_gemini_error(last_error or Exception("Hech bir model ishlamadi"))

def _handle_gemini_error(e: Exception) -> str:
    error_msg = str(e)
    logging.error(f"Gemini API xatoligi: {error_msg[:300]}")
    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
        return "⏳ AI so'rovlar limiti oshib ketdi. 30 soniya kutib, qayta yuboring.\n\n📞 Favqulodda: 103 (Tez yordam)"
    elif "API_KEY_INVALID" in error_msg or "INVALID_ARGUMENT" in error_msg or "400" in error_msg:
        return "❌ AI kaliti xato. Administrator bilan bog'laning.\n\n📞 Favqulodda: 103 (Tez yordam)"
    elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
        return "⏳ Internet aloqasi sekin. Biroz kutib, qayta yuboring.\n\n📞 Favqulodda: 103 (Tez yordam)"
    else:
        return (
            "😔 AI vaqtincha ishlamayapti. Bir oz kutib qayta yuboring.\n\n"
            "📞 Shu orada favqulodda raqamlar:\n"
            "🚑 Tez tibbiy yordam: **103**\n🚒 Yong'in: **101**\n👮 Militsiya: **102**"
        )

async def stream_gemini_to_message(
    prompt: str,
    message: types.Message,
    placeholder_text: str = "⏳ Javob tayyorlanmoqda...",
    reply_markup=None
) -> str:
    if not gemini_client:
        error_text = "⚠️ Sun'iy intellekt hozir sozlanmagan.\nIltimos, administratorga murojaat qiling."
        await message.edit_text(markdown_to_html(error_text), parse_mode="HTML", reply_markup=reply_markup)
        return error_text

    try:
        sent_msg = await message.edit_text(placeholder_text, parse_mode="HTML")
    except Exception:
        sent_msg = message

    last_error = None
    for model in GEMINI_MODELS:
        full_text = ""
        last_edit_time = asyncio.get_event_loop().time()
        edit_interval = 1.5
        min_chars_before_edit = 80
        chars_since_last_edit = 0

        try:
            stream = await gemini_client.aio.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                    temperature=0.7,
                )
            )
            async for chunk in stream:
                if chunk.text:
                    full_text += chunk.text
                    chars_since_last_edit += len(chunk.text)
                    now = asyncio.get_event_loop().time()
                    if now - last_edit_time >= edit_interval and chars_since_last_edit >= min_chars_before_edit:
                        try:
                            await sent_msg.edit_text(markdown_to_html(full_text) + " ✍️", parse_mode="HTML")
                            last_edit_time = now
                            chars_since_last_edit = 0
                        except Exception:
                            pass

            if full_text:
                try:
                    await sent_msg.edit_text(
                        markdown_to_html(full_text),
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
                except Exception:
                    pass
                return full_text
            else:
                logging.warning(f"{model} bo'sh javob qaytardi, keyingisiga o'tilmoqda...")
                continue

        except Exception as e:
            err = str(e)
            if "429" in err or "404" in err or "RESOURCE_EXHAUSTED" in err or "NOT_FOUND" in err:
                logging.warning(f"Streaming: {model} ishlamadi, keyingisiga o'tilmoqda...")
                last_error = e
                continue
            error_text = _handle_gemini_error(e)
            await sent_msg.edit_text(markdown_to_html(error_text), parse_mode="HTML", reply_markup=reply_markup)
            return error_text

    logging.warning("Barcha streaming modellari ishlamadi, oddiy javobga o'tilmoqda...")
    fallback_text = await get_gemini_response(prompt)
    try:
        await sent_msg.edit_text(markdown_to_html(fallback_text), parse_mode="HTML", reply_markup=reply_markup)
    except Exception:
        pass
    return fallback_text

# ═══════════════════════════════════════════════════════════════════
# KLAVIATURALAR (KEYBOARDS)
# ═══════════════════════════════════════════════════════════════════

def get_start_keyboard():
    """Asosiy reply menyu tugmalari"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Holatlar ro'yxati"),
                KeyboardButton(text="🚨 Favqulodda raqamlar")
            ],
            [
                KeyboardButton(text="📚 Kasalliklar Ro'yxati (100+)"),
                KeyboardButton(text="💬 AI Konsultatsiya (Chat)")
            ],
            [
                KeyboardButton(text="🏥 Eng yaqin kasalxona"),
                KeyboardButton(text="💎 Premium olish")
            ],
            [
                KeyboardButton(text="👤 Tibbiy Profilim"),
                KeyboardButton(text="💊 Dori Eslatmalari")
            ],
            [
                KeyboardButton(text="⚖️ Sog'liq Kalkulyatori"),
                KeyboardButton(text="🔔 Kunlik Maslahatlar")
            ],
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard

def get_conditions_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Kuyish",              callback_data="aid_kuyish")
    builder.button(text="🩸 Qon ketishi",         callback_data="aid_qon_ketishi")
    builder.button(text="🦴 Suyak sinishi",       callback_data="aid_sinish")
    builder.button(text="🫣 Bo'g'ilish",          callback_data="aid_bogilish")
    builder.button(text="💔 Yurak xuruji",        callback_data="aid_yurak_xuruji")
    builder.button(text="😵 Hushidan ketish",     callback_data="aid_hushdan_ketish")
    builder.button(text="💀 Zaharlanish",         callback_data="aid_zaharlanish")
    builder.button(text="☀️ Issiqlik urishi",    callback_data="aid_issiqlik_urishi")
    builder.button(text="⚡ Talvasa (epilepsiya)", callback_data="aid_talvasa")
    builder.button(text="⚡ Elektr toki urishi",  callback_data="aid_elektr_toki")
    builder.button(text="🤧 Kuchli allergiya",    callback_data="aid_allergiya")
    builder.button(text="🧠 Insult belgilari",    callback_data="aid_insult")
    builder.button(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")
    builder.adjust(2, 2, 2, 2, 2, 2, 1)
    return builder.as_markup()

def get_back_to_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")
    return builder.as_markup()

def get_location_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📍 Joylashuvni yuborish", request_location=True)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_diseases_keyboard(page: int = 1):
    builder = InlineKeyboardBuilder()
    page_index = page - 1
    if 0 <= page_index < len(DISEASES):
        page_diseases = DISEASES[page_index]
        for idx, disease in enumerate(page_diseases):
            builder.button(text=disease, callback_data=f"dis_{page}_{idx}")
    if page > 1:
        builder.button(text="⬅️", callback_data=f"page_{page-1}")
    builder.button(text=f"{page}/10", callback_data="page_noop")
    if page < 10:
        builder.button(text="➡️", callback_data=f"page_{page+1}")
    builder.button(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")
    layout = [2, 2, 2, 2, 2]
    layout.append(3 if page > 1 and page < 10 else 2)
    layout.append(1)
    builder.adjust(*layout)
    return builder.as_markup()

def get_premium_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Premium olish", callback_data="buy_premium")
    return builder.as_markup()

# ═══════════════════════════════════════════════════════════════════
# PREMIUM UPSELL
# ═══════════════════════════════════════════════════════════════════

async def premium_upsell(event):
    text = (
        "🛑 <b>Bepul AI so'rovlar limiti tugadi!</b>\n\n"
        "AI bilan cheksiz ishlash uchun <b>Premium</b> xarid qiling.\n\n"
        f"⭐ <b>{PREMIUM_STARS_PRICE} Telegram Stars</b> yoki karta orqali.\n\n"
        "Quyidagi tugmani bosing:"
    )
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=get_premium_keyboard(), parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=get_premium_keyboard(), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
# START VA MENYU
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """/start yuborilganda"""
    await state.clear()
    user = message.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or None
    username = user.username or None
    database.register_user(user.id, full_name=full_name, username=username)
    await message.answer(
        markdown_to_html(FIRST_AID_DATA["start"] + "\n\nKerakli bo'limni tanlang yoki sun'iy intellektga to'g'ridan-to'g'ri savol yozing:"),
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyu:", reply_markup=get_start_keyboard())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "ℹ️ <b>Bot imkoniyatlari:</b>\n\n"
        "📋 <b>Holatlar ro'yxati</b> — 12 ta birinchi yordam holati\n"
        "📚 <b>Kasalliklar</b> — 100+ kasallik haqida AI ma'lumot\n"
        "💬 <b>AI Konsultatsiya</b> — Gemini AI bilan suhbat\n"
        "🏥 <b>Kasalxona</b> — Yaqin shifoxona va dorixonalar\n"
        "💎 <b>Premium</b> — Cheksiz AI so'rovlari\n"
        "👤 <b>Tibbiy Profil</b> — Sizning shaxsiy tibbiy ma'lumotlaringiz\n"
        "💊 <b>Dori Eslatmalari</b> — Dorilarni vaqtida ichish uchun budilnik\n"
        "⚖️ <b>Sog'liq Kalkulyatori</b> — BMI va suv balansi\n"
        "🔔 <b>Kunlik Maslahatlar</b> — Har kuni sog'liq bo'yicha tavsiya\n\n"
        "📞 <b>Favqulodda:</b> 103 (Tez yordam) | 101 (Yong'in) | 102 (Militsiya)"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_start_keyboard())

@dp.message(Command("contacts"))
async def cmd_contacts(message: types.Message):
    await message.answer(
        markdown_to_html(
            "🚨 **Favqulodda tezkor yordam telefon raqamlari:**\n\n"
            "🚑 **Tez tibbiy yordam:** 103\n🚒 **Yong'in xavfsizligi:** 101\n"
            "👮 **Militsiya:** 102\n👨‍🚒 **Favqulodda vaziyatlar (FVV):** 1050\n\n"
            "Tezkor raqamlarga qo'ng'iroq qilish bepul va 24/7 ishlaydi."
        ),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════════
# REPLY KEYBOARD HANDLERLARI
# ═══════════════════════════════════════════════════════════════════

@dp.message(F.text == "📋 Holatlar ro'yxati")
async def reply_conditions(message: types.Message):
    await message.answer("Quyidagi holatlardan birini tanlang:", reply_markup=get_conditions_keyboard())

@dp.message(F.text == "📚 Kasalliklar Ro'yxati (100+)")
async def reply_diseases_list(message: types.Message):
    await message.answer("Kasallikni tanlang (sahifa 1/10):", reply_markup=get_diseases_keyboard(1))

@dp.message(F.text == "💬 AI Konsultatsiya (Chat)")
async def reply_diseases_ai(message: types.Message, state: FSMContext):
    await state.set_state(AiChatStates.chatting)
    text = (
        "🤖 **Sun'iy Intellekt (Gemini AI) Yordami (Chat rejimida):**\n\n"
        "Menga istalgan kasallik, simptom, dorilar, foydali ovqatlar yoki jismoniy mashqlar haqida yozing.\n\n"
        "**Masalan yozib ko'ring:**\n"
        "• *Bosh og'rig'ini qoldirish uchun nima qilish kerak?*\n"
        "• *Sog'lom ovqatlanish qoidalari qanday?*\n"
        "• *Bel og'rig'iga qanday mashqlar foydali?*\n\n"
        "⚠️ <i>Chatdan chiqish uchun boshqa biror menyu tugmasini bosing yoki /cancel deb yozing.</i>"
    )
    await message.answer(markdown_to_html(text), reply_markup=get_start_keyboard(), parse_mode="HTML")

@dp.message(F.text == "🏥 Eng yaqin kasalxona")
async def reply_hospital(message: types.Message):
    await message.answer(
        markdown_to_html(
            "🏥 **Eng yaqin kasalxona va dorixonani topish:**\n\n"
            "Iltimos, joylashuvingizni yuboring — men sizga eng yaqin shifoxonalar **va dorixonalarni** haritada ko'rsataman:"
        ),
        reply_markup=get_location_keyboard(),
        parse_mode="HTML"
    )

@dp.message(F.text == "💎 Premium olish")
async def reply_premium_info(message: types.Message):
    await _show_premium_page(message)

@dp.message(F.text == "🚨 Favqulodda raqamlar")
async def reply_contacts(message: types.Message):
    text = (
        "🚨 **Favqulodda tezkor yordam telefon raqamlari:**\n\n"
        "🚑 **Tez tibbiy yordam:** 103\n🚒 **Yong'in xavfsizligi:** 101\n"
        "👮 **Militsiya:** 102\n👨‍🚒 **Favqulodda vaziyatlar (FVV):** 1050\n\n"
        "Tezkor raqamlarga qo'ng'iroq qilish bepul va 24/7 ishlaydi."
    )
    await message.answer(markdown_to_html(text), reply_markup=get_start_keyboard(), parse_mode="HTML")

# ─── Yaqin kasalxona + dorixona (Feature 4) ───────────────────────

@dp.message(F.location)
async def handle_location(message: types.Message):
    """Foydalanuvchi joylashuvini qabul qilib — kasalxona VA dorixona haritasini ko'rsatish"""
    lat = message.location.latitude
    lon = message.location.longitude

    hospitals_google  = f"https://www.google.com/maps/search/hospital/@{lat},{lon},14z"
    hospitals_yandex  = f"https://yandex.com/maps/?ll={lon}%2C{lat}&mode=search&text=hospital&z=14"
    pharmacy_google   = f"https://www.google.com/maps/search/pharmacy/@{lat},{lon},15z"
    pharmacy_yandex   = f"https://yandex.com/maps/?ll={lon}%2C{lat}&mode=search&text=dorixona&z=15"

    text = (
        "📍 **Joylashuvingiz qabul qilindi!**\n\n"
        "🏥 **Eng yaqin shifoxonalar:**\n"
        f"🌐 [Google Maps orqali ko'rish]({hospitals_google})\n"
        f"🗺️ [Yandex Maps orqali ko'rish]({hospitals_yandex})\n\n"
        "💊 **Eng yaqin dorixonalar:**\n"
        f"🌐 [Google Maps orqali ko'rish]({pharmacy_google})\n"
        f"🗺️ [Yandex Maps orqali ko'rish]({pharmacy_yandex})\n\n"
        "ℹ️ Haritada sizga eng yaqin nuqtalar ko'rsatiladi."
    )
    await message.answer(
        markdown_to_html(text),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    # Asosiy menyuni qaytarish
    await message.answer("Bosh menyu:", reply_markup=get_start_keyboard())

# ═══════════════════════════════════════════════════════════════════
# INLINE CALLBACK HANDLERLARI (asosiy)
# ═══════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        markdown_to_html(FIRST_AID_DATA["start"] + "\n\nKerakli bo'limni tanlang yoki savolingizni to'g'ridan-to'g'ri yozing:"),
        parse_mode="HTML"
    )
    await callback.message.answer("Bosh menyu:", reply_markup=get_start_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "main_conditions")
async def main_conditions(callback: types.CallbackQuery):
    await callback.message.edit_text("Quyidagi holatlardan birini tanlang:", reply_markup=get_conditions_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "main_contacts")
async def main_contacts(callback: types.CallbackQuery):
    text = (
        "🚨 **Favqulodda tezkor yordam telefon raqamlari:**\n\n"
        "🚑 **Tez tibbiy yordam:** 103\n🚒 **Yong'in xavfsizligi:** 101\n"
        "👮 **Militsiya:** 102\n👨‍🚒 **Favqulodda vaziyatlar (FVV):** 1050\n\n"
        "Tezkor raqamlarga qo'ng'iroq qilish bepul va 24/7 ishlaydi."
    )
    await callback.message.edit_text(markdown_to_html(text), reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("aid_"))
async def process_aid_callback(callback: types.CallbackQuery):
    action_key = callback.data.replace("aid_", "")
    text = FIRST_AID_DATA.get(action_key, "Ma'lumot topilmadi.")
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Holatlar ro'yxatiga qaytish", callback_data="main_conditions")
    await callback.message.edit_text(markdown_to_html(text), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("page_"))
async def process_page_callback(callback: types.CallbackQuery):
    if callback.data == "page_noop":
        await callback.answer()
        return
    page = int(callback.data.replace("page_", ""))
    await callback.message.edit_text(f"Kasallikni tanlang (sahifa {page}/10):", reply_markup=get_diseases_keyboard(page))
    await callback.answer()

@dp.callback_query(F.data.startswith("dis_"))
async def process_disease_callback(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    # Kasalliklar ro'yxatidan qisqa ma'lumot — BEPUL (Premium talab emas)
    _, page_str, index_str = callback.data.split("_")
    page, index = int(page_str), int(index_str)
    disease_name = DISEASES[page - 1][index]
    await callback.message.bot.send_chat_action(chat_id=callback.message.chat.id, action="typing")

    # Premium foydalanuvchilar uchun batafsil tugmasi ko'rinadi
    is_premium_user, _ = database.get_premium_info(user_id)
    builder = InlineKeyboardBuilder()
    if is_premium_user:
        builder.button(text="🔍 Batafsil ma'lumot (AI)", callback_data=f"det_{page}_{index}")
    else:
        builder.button(text="🔍 Batafsil ma'lumot (💎 Premium)", callback_data=f"det_{page}_{index}")
    builder.button(text="⬅️ Ro'yxatga qaytish", callback_data=f"page_{page}")
    builder.adjust(1, 1)

    # Tibbiy profilni AI ga qo'shish
    profile = database.get_medical_profile(user_id)
    profile_context = _build_profile_context(profile)

    prompt = (
        f"Menga '{disease_name}' kasalligi haqida faqat o'zbek tilida juda qisqa va aniq ma'lumot beruvchi matn yozib ber.\n"
        f"Javob aynan quyidagi qat'iy formatda (emojilar bilan) bo'lishi shart:\n\n"
        f"🩺 **{disease_name}**\n\n"
        f"📌 **Yuqish yo'li:** [Qisqacha]\n"
        f"🛠️ **Yechim:** [1-2 ta birinchi yordam]\n"
        f"🍏 **Parhez:** [Nimalarni yeyish kerak]\n"
        f"💊 **Xavfsiz dorilar:** [1-2 ta]\n"
        + profile_context
    )
    await stream_gemini_to_message(
        prompt=prompt,
        message=callback.message,
        placeholder_text=f"⏳ <b>{disease_name}</b> haqida ma'lumot yuklanmoqda...",
        reply_markup=builder.as_markup()
    )
    database.increment_usage(user_id)

@dp.callback_query(F.data.startswith("det_"))
async def process_disease_detail_callback(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    # "Batafsil ma'lumot" — FAQAT PREMIUM foydalanuvchilar uchun
    is_premium_user, premium_expires_at = database.get_premium_info(user_id)
    import datetime as _dt
    if is_premium_user and premium_expires_at:
        expires = _dt.datetime.fromisoformat(premium_expires_at)
        if _dt.datetime.now() > expires:
            is_premium_user = 0
    if not is_premium_user:
        text = (
            "🔒 <b>Bu bo'lim faqat Premium foydalanuvchilar uchun!</b>\n\n"
            "📚 <b>Batafsil ma'lumot (AI)</b> — kasallik haqida to'liq:\n"
            "• Sabablari va tarqalish yo'llari\n"
            "• Barcha simptomlar\n"
            "• Davolash va dorilar\n"
            "• Parhez va profilaktika\n\n"
            f"⭐ <b>{PREMIUM_STARS_PRICE} Telegram Stars</b> — oylik Premium.\n\n"
            "Quyidagi tugmani bosing:"
        )
        builder = InlineKeyboardBuilder()
        builder.button(text="💎 Premium olish", callback_data="buy_premium")
        builder.button(text="⬅️ Ro'yxatga qaytish", callback_data=f"page_{callback.data.split('_')[1]}")
        builder.adjust(1)
        try:
            await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        except Exception:
            await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        return
    _, page_str, index_str = callback.data.split("_")
    page, index = int(page_str), int(index_str)
    disease_name = DISEASES[page - 1][index]
    await callback.message.bot.send_chat_action(chat_id=callback.message.chat.id, action="typing")
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Kasallik sahifasiga qaytish", callback_data=f"dis_{page}_{index}")
    builder.button(text="📋 Kasalliklar ro'yxatiga qaytish", callback_data=f"page_{page}")
    builder.adjust(1, 1)

    profile = database.get_medical_profile(user_id)
    profile_context = _build_profile_context(profile)

    prompt = (
        f"Menga '{disease_name}' kasalligi haqida juda batafsil, ilmiy va tushunarli tibbiy ma'lumot tayyorlab ber.\n"
        f"Javob o'zbek tilida bo'lsin. Quyidagi bo'limlarni o'z ichiga olsin:\n\n"
        f"🩺 **{disease_name} haqida batafsil ma'lumot**\n\n"
        f"❓ **Kasallik nima va u qanday paydo bo'ladi?**\n"
        f"📌 **Yuqish va tarqalish yo'llari:**\n"
        f"⚠️ **Asosiy simptomlar va belgilari:**\n"
        f"🛠️ **Birinchi yordam va davolash yechimlari:**\n"
        f"🍏 **Tavsiya etiladigan parhez:**\n"
        f"💊 **Xavfsiz dorilar (xavfsiz dozalar):**\n"
        f"🛡️ **Profilaktika (oldini olish):**\n\n"
        f"Matn oxirida shifokor bilan maslahatlashishni va 103 eslatib o'ting.\n"
        + profile_context
    )
    await stream_gemini_to_message(
        prompt=prompt,
        message=callback.message,
        placeholder_text=f"⏳ <b>{disease_name}</b> haqida to'liq ma'lumot tayyorlanmoqda...",
        reply_markup=builder.as_markup()
    )
    database.increment_usage(user_id)



# ═══════════════════════════════════════════════════════════════════
# FEATURE 1: 👤 TIBBIY PROFIL
# ═══════════════════════════════════════════════════════════════════

@dp.message(F.text == "👤 Tibbiy Profilim")
async def medical_profile_menu(message: types.Message):
    user_id = message.from_user.id
    profile = database.get_medical_profile(user_id)
    blood_group, age, weight, height, chronic, allergies = profile if profile else (None,)*6

    text = (
        "👤 <b>Sizning Tibbiy Profilingiz</b>\n\n"
        f"🩸 <b>Qon guruhi:</b> {blood_group or '—'}\n"
        f"🎂 <b>Yosh:</b> {age or '—'}\n"
        f"⚖️ <b>Vazn:</b> {f'{weight} kg' if weight else '—'}\n"
        f"📏 <b>Bo'y:</b> {f'{height} sm' if height else '—'}\n"
        f"🏥 <b>Surunkali kasalliklar:</b> {chronic or '—'}\n"
        f"⚠️ <b>Allergiyalar:</b> {allergies or '—'}\n\n"
        "ℹ️ Bu ma'lumotlar AI konsultatsiyada hisobga olinadi va aniqroq maslahat beradi."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Profilni to'ldirish / tahrirlash", callback_data="edit_profile")
    builder.button(text="🗑️ Profilni o'chirish",               callback_data="clear_profile")
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "edit_profile")
async def edit_profile_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(MedicalProfileStates.blood_group)
    builder = InlineKeyboardBuilder()
    for bg in ["I (O+)", "I (O-)", "II (A+)", "II (A-)", "III (B+)", "III (B-)", "IV (AB+)", "IV (AB-)"]:
        builder.button(text=bg, callback_data=f"bg_{bg}")
    builder.button(text="O'tkazib yuborish ➡️", callback_data="bg_skip")
    builder.adjust(2, 2, 2, 2, 1)
    try:
        await callback.message.edit_text(
            "🩸 <b>1/6 — Qon guruhingizni tanlang:</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception:
        pass

@dp.callback_query(MedicalProfileStates.blood_group, F.data.startswith("bg_"))
async def profile_blood_group(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    value = callback.data.replace("bg_", "")
    if value != "skip":
        await state.update_data(blood_group=value)
    await state.set_state(MedicalProfileStates.age)
    try:
        await callback.message.edit_text(
            "🎂 <b>2/6 — Yoshingizni kiriting</b> (masalan: 25):\n\n"
            "Yoki /skip yuboring.",
            parse_mode="HTML"
        )
    except Exception:
        pass

@dp.message(MedicalProfileStates.age)
async def profile_age(message: types.Message, state: FSMContext):
    if message.text and message.text.strip() != "/skip":
        try:
            age = int(message.text.strip())
            if 1 <= age <= 120:
                await state.update_data(age=age)
            else:
                await message.answer("⚠️ Yosh 1 dan 120 gacha bo'lishi kerak. Qaytadan kiriting:")
                return
        except ValueError:
            await message.answer("⚠️ Faqat raqam kiriting (masalan: 25):")
            return
    await state.set_state(MedicalProfileStates.weight)
    await message.answer("⚖️ <b>3/6 — Vazningizni kiriting (kg):</b> masalan: 70\n\nYoki /skip yuboring.", parse_mode="HTML")

@dp.message(MedicalProfileStates.weight)
async def profile_weight(message: types.Message, state: FSMContext):
    if message.text and message.text.strip() != "/skip":
        try:
            weight = float(message.text.strip().replace(",", "."))
            if 20 <= weight <= 300:
                await state.update_data(weight=weight)
            else:
                await message.answer("⚠️ Vazn 20 dan 300 gacha bo'lishi kerak:")
                return
        except ValueError:
            await message.answer("⚠️ Faqat raqam kiriting (masalan: 70):")
            return
    await state.set_state(MedicalProfileStates.height)
    await message.answer("📏 <b>4/6 — Bo'yingizni kiriting (sm):</b> masalan: 175\n\nYoki /skip yuboring.", parse_mode="HTML")

@dp.message(MedicalProfileStates.height)
async def profile_height(message: types.Message, state: FSMContext):
    if message.text and message.text.strip() != "/skip":
        try:
            height = float(message.text.strip().replace(",", "."))
            if 50 <= height <= 250:
                await state.update_data(height=height)
            else:
                await message.answer("⚠️ Bo'y 50 dan 250 gacha bo'lishi kerak:")
                return
        except ValueError:
            await message.answer("⚠️ Faqat raqam kiriting (masalan: 175):")
            return
    await state.set_state(MedicalProfileStates.chronic_diseases)
    await message.answer(
        "🏥 <b>5/6 — Surunkali kasalliklaringiz</b> (vergul bilan yozing):\n"
        "Masalan: <i>Diabet, Gipertenziya</i>\n\n"
        "Agar yo'q bo'lsa /skip yuboring.",
        parse_mode="HTML"
    )

@dp.message(MedicalProfileStates.chronic_diseases)
async def profile_chronic(message: types.Message, state: FSMContext):
    if message.text and message.text.strip() != "/skip":
        await state.update_data(chronic_diseases=message.text.strip())
    await state.set_state(MedicalProfileStates.allergies)
    await message.answer(
        "⚠️ <b>6/6 — Dorilarga allergiyalaringiz:</b>\n"
        "Masalan: <i>Aspirin, Penitsullin</i>\n\n"
        "Agar yo'q bo'lsa /skip yuboring.",
        parse_mode="HTML"
    )

@dp.message(MedicalProfileStates.allergies)
async def profile_allergies(message: types.Message, state: FSMContext):
    if message.text and message.text.strip() != "/skip":
        await state.update_data(allergies=message.text.strip())

    data = await state.get_data()
    await state.clear()

    database.save_medical_profile(
        user_id=message.from_user.id,
        blood_group=data.get("blood_group"),
        age=data.get("age"),
        weight=data.get("weight"),
        height=data.get("height"),
        chronic_diseases=data.get("chronic_diseases"),
        allergies=data.get("allergies"),
    )
    await message.answer(
        "✅ <b>Tibbiy profilingiz saqlandi!</b>\n\n"
        "Endi AI konsultatsiyada sizning ma'lumotlaringiz hisobga olinadi va aniqroq maslahat beriladi. 🎯",
        parse_mode="HTML",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(F.data == "clear_profile")
async def clear_profile(callback: types.CallbackQuery):
    database.save_medical_profile(callback.from_user.id)  # Hammasini None qiladi
    await callback.message.edit_text(
        "🗑️ Tibbiy profilingiz tozalandi.",
        parse_mode="HTML"
    )
    await callback.answer("Profil tozalandi!")

# ═══════════════════════════════════════════════════════════════════
# FEATURE 2: 💊 DORI ESLATMALARI
# ═══════════════════════════════════════════════════════════════════

@dp.message(F.text == "💊 Dori Eslatmalari")
async def reminder_menu(message: types.Message):
    user_id = message.from_user.id
    reminders = database.get_user_reminders(user_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Yangi eslatma qo'shish", callback_data="add_reminder")

    text = "💊 <b>Dori Eslatmalari</b>\n\n"
    if reminders:
        text += "📋 <b>Faol eslatmalaringiz:</b>\n\n"
        for rem_id, name, times in reminders:
            times_display = times.replace(",", ", ")
            text += f"• <b>{name}</b> — {times_display}\n"
            builder.button(text=f"🗑️ {name} o'chirish", callback_data=f"del_rem_{rem_id}")
    else:
        text += "Hozircha hech qanday eslatma yo'q.\n\nQuyidagi tugmadan yangi eslatma qo'shishingiz mumkin:"

    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "add_reminder")
async def add_reminder_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ReminderStates.medicine_name)
    await callback.message.edit_text(
        "💊 <b>Yangi dori eslatmasi</b>\n\n"
        "<b>1/2</b> — Dori nomini kiriting:\n"
        "Masalan: <i>Paracetamol</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(ReminderStates.medicine_name)
async def reminder_medicine_name(message: types.Message, state: FSMContext):
    await state.update_data(medicine_name=message.text.strip())
    await state.set_state(ReminderStates.times)
    await message.answer(
        "⏰ <b>2/2 — Ichish vaqtlarini kiriting</b>\n\n"
        "Vaqtlarni vergul bilan ajrating:\n"
        "Masalan: <code>08:00,14:00,20:00</code>\n\n"
        "Yoki bitta vaqt: <code>09:00</code>",
        parse_mode="HTML"
    )

@dp.message(ReminderStates.times)
async def reminder_times(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    # Vaqtlarni tekshirish
    times_list = [t.strip() for t in raw.split(",")]
    valid_times = []
    for t in times_list:
        try:
            h, m = t.split(":")
            if 0 <= int(h) <= 23 and 0 <= int(m) <= 59:
                valid_times.append(f"{int(h):02d}:{int(m):02d}")
            else:
                raise ValueError
        except:
            await message.answer(
                f"⚠️ <code>{t}</code> noto'g'ri vaqt formati!\n"
                "Iltimos <code>HH:MM</code> ko'rinishida kiriting (masalan: 08:00,14:00):",
                parse_mode="HTML"
            )
            return

    data = await state.get_data()
    await state.clear()

    medicine_name = data["medicine_name"]
    times_str = ",".join(valid_times)
    database.add_reminder(message.from_user.id, medicine_name, times_str)

    await message.answer(
        f"✅ <b>Eslatma qo'shildi!</b>\n\n"
        f"💊 <b>Dori:</b> {medicine_name}\n"
        f"⏰ <b>Vaqtlar:</b> {times_str.replace(',', ', ')}\n\n"
        f"Bot belgilangan vaqtlarda sizga eslatma yuboradi! 🔔",
        parse_mode="HTML",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(F.data.startswith("del_rem_"))
async def delete_reminder_handler(callback: types.CallbackQuery):
    rem_id = int(callback.data.replace("del_rem_", ""))
    database.delete_reminder(rem_id, callback.from_user.id)
    await callback.answer("✅ Eslatma o'chirildi!", show_alert=True)
    # Ro'yxatni yangilash
    await reminder_menu_refresh(callback.message, callback.from_user.id)

async def reminder_menu_refresh(message: types.Message, user_id: int):
    reminders = database.get_user_reminders(user_id)
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Yangi eslatma qo'shish", callback_data="add_reminder")
    text = "💊 <b>Dori Eslatmalari</b>\n\n"
    if reminders:
        text += "📋 <b>Faol eslatmalaringiz:</b>\n\n"
        for rem_id, name, times in reminders:
            text += f"• <b>{name}</b> — {times.replace(',', ', ')}\n"
            builder.button(text=f"🗑️ {name} o'chirish", callback_data=f"del_rem_{rem_id}")
    else:
        text += "Barcha eslatmalar o'chirildi."
    builder.adjust(1)
    try:
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════
# FEATURE 3: 🎙️ OVOZLI XABARLAR
# ═══════════════════════════════════════════════════════════════════

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    """Ovozli xabarlarni Gemini AI orqali matnlashtirish va javob berish"""
    user_id = message.from_user.id
    
    # Admin xabar tarqatish uchun media yuklayotgan bo'lishi mumkin, AI tahlil qilmaydi
    if str(user_id) == str(ADMIN_ID):
        return

    # Agar ovozli xabarda buyruq bo'lsa (masalan captionda)
    if message.caption and message.caption.strip().startswith('/'):
        return

    if not database.check_ai_limit(user_id):
        await premium_upsell(message)
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if not gemini_client:
        await message.answer(
            "⚠️ Ovozli xabarlarni qayta ishlash uchun AI sozlanmagan.\n"
            "Iltimos, matnli savol yuboring.",
            reply_markup=get_start_keyboard()
        )
        return

    # Ovozli xabarni yuklab olish
    status_msg = await message.answer("🎙️ <b>Ovozli xabar qayta ishlanmoqda...</b>", parse_mode="HTML")
    try:
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        file_path = file.file_path

        # Faylni yuklab olish
        import io
        file_bytes = await message.bot.download_file(file_path)
        audio_data = file_bytes.read()

        # Gemini ga audio yuborish (base64)
        import base64
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        prompt_parts = [
            {
                "inline_data": {
                    "mime_type": "audio/ogg",
                    "data": audio_b64
                }
            },
            {
                "text": (
                    "Bu audio xabarni o'zbek yoki rus tilida tinglab, "
                    "mazmunini o'zbekcha yozing va unga tibbiy/sog'liq nuqtai nazaridan javob bering. "
                    "Agar savol tibbiyotga oid bo'lmasa, faqat sog'liq mavzusida gapirishingizni ayting."
                )
            }
        ]

        # Gemini API ga yuborish
        for model in GEMINI_MODELS:
            try:
                response = await gemini_client.aio.models.generate_content(
                    model=model,
                    contents=prompt_parts,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                if response.text:
                    await status_msg.edit_text(
                        f"🎙️ <b>Ovozli xabaringiz qabul qilindi!</b>\n\n"
                        + markdown_to_html(response.text),
                        parse_mode="HTML"
                    )
                    database.increment_usage(user_id)
                    return
            except Exception as e:
                err = str(e)
                if "429" in err or "404" in err or "NOT_FOUND" in err:
                    continue
                break

        # Fallback: API ovozni qayta ishlay olmasa
        await status_msg.edit_text(
            "⚠️ Ovozli xabarni matnlashtirish vaqtincha ishlamayapti.\n\n"
            "Iltimos, savolingizni <b>matn ko'rinishida</b> yuboring. 📝",
            parse_mode="HTML"
        )

    except Exception as e:
        logging.error(f"Voice handler xatosi: {e}")
        await status_msg.edit_text(
            "⚠️ Ovozli xabarni qayta ishlashda xatolik yuz berdi.\n"
            "Iltimos, matnli savol yuboring.",
            parse_mode="HTML"
        )

# ═══════════════════════════════════════════════════════════════════
# FEATURE 5: ⚖️ SOG'LIQ KALKULYATORI (BMI + Suv balansi)
# ═══════════════════════════════════════════════════════════════════

@dp.message(F.text == "⚖️ Sog'liq Kalkulyatori")
async def health_calculator_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="⚖️ BMI (Tana Vazni Indeksi)", callback_data="calc_bmi")
    builder.button(text="💧 Suv balansi kalkulyatori",  callback_data="calc_water")
    builder.adjust(1)
    await message.answer(
        "⚖️ <b>Sog'liq Kalkulyatorlari</b>\n\n"
        "Quyidagi kalkulyatorlardan birini tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "calc_bmi")
async def calc_bmi_start(callback: types.CallbackQuery, state: FSMContext):
    # Profilda ma'lumot bo'lsa, undan foydalanamiz
    profile = database.get_medical_profile(callback.from_user.id)
    if profile and profile[2] and profile[3]:
        weight, height = profile[2], profile[3]
        result = _calculate_bmi(weight, height)
        await callback.message.edit_text(result, parse_mode="HTML")
        await callback.answer()
        return

    await state.set_state(BmiStates.weight)
    await callback.message.edit_text(
        "⚖️ <b>BMI Kalkulyatori</b>\n\n"
        "<b>1/2</b> — Vazningizni kiriting (kg):\n"
        "Masalan: <code>70</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(BmiStates.weight)
async def bmi_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.strip().replace(",", "."))
        if not (20 <= weight <= 300):
            raise ValueError
        await state.update_data(weight=weight)
        await state.set_state(BmiStates.height)
        await message.answer(
            "📏 <b>2/2</b> — Bo'yingizni kiriting (sm):\n"
            "Masalan: <code>175</code>",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("⚠️ 20 dan 300 gacha bo'lgan raqam kiriting:")

@dp.message(BmiStates.height)
async def bmi_height(message: types.Message, state: FSMContext):
    try:
        height = float(message.text.strip().replace(",", "."))
        if not (50 <= height <= 250):
            raise ValueError
        data = await state.get_data()
        await state.clear()
        result = _calculate_bmi(data["weight"], height)
        await message.answer(result, parse_mode="HTML", reply_markup=get_start_keyboard())
    except ValueError:
        await message.answer("⚠️ 50 dan 250 gacha bo'lgan raqam kiriting (sm):")

def _calculate_bmi(weight: float, height: float) -> str:
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    if bmi < 18.5:
        category = "🔵 <b>Tana og'irligi yetarli emas (kam vazn)</b>"
        advice = "Ko'proq kaloriyali va oqsilli ovqatlar iste'mol qiling. Shifokor bilan maslahatlashing."
    elif bmi < 25:
        category = "🟢 <b>Normal vazn (sog'lom)</b>"
        advice = "Ajoyib! Sog'lom hayot tarzini davom ettiring."
    elif bmi < 30:
        category = "🟡 <b>Ortiqcha vazn (pre-obesitas)</b>"
        advice = "Jismoniy faollikni oshiring va ratsionni nazorat qiling."
    elif bmi < 35:
        category = "🟠 <b>1-darajali semizlik</b>"
        advice = "Shifokor yoki dietolog bilan maslahatlashing."
    else:
        category = "🔴 <b>2-darajali va yuqori semizlik</b>"
        advice = "Zudlik bilan shifokor bilan maslahatlashing!"

    return (
        f"⚖️ <b>BMI Hisob natijasi</b>\n\n"
        f"📊 <b>Vazn:</b> {weight} kg\n"
        f"📏 <b>Bo'y:</b> {height} sm\n"
        f"🧮 <b>BMI:</b> {bmi:.1f}\n\n"
        f"{category}\n\n"
        f"💡 <b>Maslahat:</b> {advice}"
    )

@dp.callback_query(F.data == "calc_water")
async def calc_water_start(callback: types.CallbackQuery, state: FSMContext):
    profile = database.get_medical_profile(callback.from_user.id)
    if profile and profile[2]:
        weight = profile[2]
        result = _calculate_water(weight)
        await callback.message.edit_text(result, parse_mode="HTML")
        await callback.answer()
        return

    await state.set_state(WaterStates.weight)
    await callback.message.edit_text(
        "💧 <b>Suv Balansi Kalkulyatori</b>\n\n"
        "Vazningizni kiriting (kg):\n"
        "Masalan: <code>70</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(WaterStates.weight)
async def water_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.strip().replace(",", "."))
        if not (20 <= weight <= 300):
            raise ValueError
        await state.clear()
        result = _calculate_water(weight)
        await message.answer(result, parse_mode="HTML", reply_markup=get_start_keyboard())
    except ValueError:
        await message.answer("⚠️ To'g'ri raqam kiriting (masalan: 70):")

def _calculate_water(weight: float) -> str:
    daily_ml = weight * 35
    glasses  = daily_ml / 250
    sport_ml = daily_ml + 500
    summer_ml = daily_ml + 300
    return (
        f"💧 <b>Kunlik Suv Balansi</b>\n\n"
        f"⚖️ <b>Vazniga qarab ({weight} kg):</b>\n\n"
        f"🥛 Kunlik minimum: <b>{daily_ml:.0f} ml</b> (~{glasses:.0f} ta stakan)\n"
        f"🏃 Sport qilganda: <b>{sport_ml:.0f} ml</b>\n"
        f"☀️ Issiq havoda: <b>{summer_ml:.0f} ml</b>\n\n"
        f"💡 <b>Maslahat:</b>\n"
        f"• Ertalab uyg'onganingizda 1-2 stakan suv iching\n"
        f"• Ovqatdan 30 daqiqa oldin suv iching\n"
        f"• Siydik rangi och sariq bo'lishi — me'yor belgisi"
    )

# ═══════════════════════════════════════════════════════════════════
# FEATURE 6: ⭐ TELEGRAM STARS TO'LOV TIZIMI
# ═══════════════════════════════════════════════════════════════════

async def _show_premium_page(message_or_cb):
    """Premium sahifasini ko'rsatish — Stars to'lov va manual chek"""
    is_callback = isinstance(message_or_cb, types.CallbackQuery)
    user_id = message_or_cb.from_user.id

    is_prem, expires = database.get_premium_info(user_id)
    if is_prem and expires:
        exp_dt = datetime.fromisoformat(expires)
        exp_str = exp_dt.strftime("%d.%m.%Y")
        text = (
            f"💎 <b>Siz allaqachon Premium foydalanuvchisiz!</b>\n\n"
            f"📅 Muddati: <b>{exp_str}</b> gacha\n\n"
            f"✅ Cheksiz AI so'rovlaridan bahramand bo'ling!"
        )
        if is_callback:
            await message_or_cb.message.edit_text(text, parse_mode="HTML")
            await message_or_cb.answer()
        else:
            await message_or_cb.answer(text, parse_mode="HTML")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text=f"⭐ {PREMIUM_STARS_PRICE} Stars bilan to'lash", callback_data="pay_stars")
    builder.adjust(1)

    text = (
        "💎 <b>Premium Obuna</b>\n\n"
        "🚀 <b>Premium afzalliklari:</b>\n"
        "• ♾️ Cheksiz AI so'rovlari\n"
        "• 🎙️ Ovozli xabar orqali konsultatsiya\n"
        "• 🏥 Kasalliklar bo'yicha batafsil tahlil\n"
        "• 🩺 Tibbiy profilga asoslangan shaxsiy maslahat\n\n"
        f"⭐ <b>Narx: {PREMIUM_STARS_PRICE} Telegram Stars</b> (1 oylik)\n\n"
        "👇 Qulay usulni tanlang:"
    )

    if is_callback:
        try:
            await message_or_cb.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        except Exception:
            await message_or_cb.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        await message_or_cb.answer()
    else:
        await message_or_cb.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "buy_premium")
async def process_buy_premium(callback: types.CallbackQuery):
    await _show_premium_page(callback)

@dp.callback_query(F.data == "pay_stars")
async def process_pay_stars(callback: types.CallbackQuery):
    """Telegram Stars invoice yuborish — provider_token shart emas!"""
    try:
        prices = [LabeledPrice(label="Premium obuna (1 oy)", amount=PREMIUM_STARS_PRICE)]
        await callback.message.answer_invoice(
            title="💎 Premium Obuna — 1 oy",
            description=(
                f"Birinchi Yordam Botida 1 oylik Premium obuna.\n"
                f"✅ Cheksiz AI so'rovlari\n"
                f"✅ Ovozli konsultatsiya\n"
                f"✅ Shaxsiy tibbiy maslahat"
            ),
            payload="stars_premium_1month",
            currency="XTR",       # Telegram Stars uchun maxsus valyuta kodi
            prices=prices,
            provider_token="",    # Stars uchun bo'sh qoladi
        )
        await callback.answer()
    except Exception as e:
        logging.error(f"Stars invoice yuborishda xatolik: {e}")
        await callback.answer(
            "⚠️ Invoice yuborishda xatolik yuz berdi. Karta orqali to'lang.",
            show_alert=True
        )

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    """To'lovni tasdiqlash (10 soniya ichida javob berish shart)"""
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    """Muvaffaqiyatli to'lov — Stars yoki oddiy to'lov"""
    user_id = message.from_user.id
    payment = message.successful_payment

    # Stars to'lovi
    if payment.invoice_payload == "stars_premium_1month":
        database.set_premium(user_id, 1, months=1)
        stars_count = payment.total_amount

        await message.answer(
            f"🎉 <b>To'lov muvaffaqiyatli!</b>\n\n"
            f"⭐ <b>{stars_count} Stars</b> qabul qilindi.\n"
            f"💎 <b>Premium obunangiz faollashtirildi!</b>\n"
            f"📅 Muddati: 1 oy\n\n"
            f"Endi AI yordamchisidan cheksiz foydalaning! 🚀",
            parse_mode="HTML",
            reply_markup=get_start_keyboard()
        )

        # Adminga xabar
        username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{user_id}"
        try:
            await message.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"⭐ <b>Stars to'lov qabul qilindi!</b>\n\n"
                    f"👤 Foydalanuvchi: {username}\n"
                    f"🆔 ID: <code>{user_id}</code>\n"
                    f"⭐ Stars: {stars_count}\n"
                    f"✅ Premium avtomatik faollashtirildi!"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Adminga Stars to'lov xabari yuborishda xato: {e}")

    # Eski UZS to'lovi (agar PROVIDER_TOKEN bo'lsa)
    elif payment.invoice_payload == "premium_1month":
        database.set_premium(user_id, 1, months=1)
        amount = payment.total_amount / 100
        await message.answer(
            "🎉 <b>To'lov muvaffaqiyatli amalga oshirildi!</b>\n\n"
            "💎 <b>Premium obunangiz faollashtirildi!</b>\n"
            "📅 Muddati: 1 oy\n\n"
            "Endi AI yordamchisidan cheksiz foydalaning! 🚀",
            parse_mode="HTML",
            reply_markup=get_start_keyboard()
        )
        username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{user_id}"
        try:
            await message.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"💳 <b>Avtomatik to'lov qabul qilindi!</b>\n\n"
                    f"👤 Foydalanuvchi: {username}\n"
                    f"🆔 ID: <code>{user_id}</code>\n"
                    f"💰 Summa: {amount:,.0f} UZS\n"
                    f"✅ Premium avtomatik faollashtirildi!"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Adminga to'lov xabari yuborishda xato: {e}")

# ─── Manual to'lov (karta cheki yuborish) ─────────────────────────

@dp.callback_query(F.data == "send_receipt")
async def process_send_receipt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(PaymentStates.waiting_for_receipt)
    database.set_waiting_receipt(callback.from_user.id, 1)
    await callback.message.edit_text(
        f"💳 <b>Karta orqali to'lov:</b>\n"
        f"<code>{CARD_NUMBER}</code>\n"
        f"👤 {CARD_NAME}\n\n"
        f"💰 Miqdor: <b>10,000 so'm</b> (1 oylik Premium)\n\n"
        f"To'lovdan so'ng <b>chek skrinshotini</b> shu yerga yuboring 👇",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(PaymentStates.waiting_for_receipt, F.photo)
async def handle_receipt_photo(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    database.set_waiting_receipt(user_id, 0)
    username = f"@{message.from_user.username}" if message.from_user.username else "Noma'lum"
    photo_id = message.photo[-1].file_id
    admin_keyboard = InlineKeyboardBuilder()
    admin_keyboard.button(text="✅ Tasdiqlash (Premium berish)", callback_data=f"adm_app_{user_id}")
    admin_keyboard.button(text="❌ Rad etish",                    callback_data=f"adm_rej_{user_id}")
    admin_keyboard.adjust(1, 1)
    try:
        await message.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=(
                f"🔔 <b>Yangi karta to'lov so'rovi!</b>\n\n"
                f"👤 <b>Foydalanuvchi:</b> {username}\n"
                f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
                "Premium faollashtirish yoki rad etish uchun tugmani bosing:"
            ),
            reply_markup=admin_keyboard.as_markup(),
            parse_mode="HTML"
        )
        await message.answer(
            "✅ <b>To'lov cheki qabul qilindi!</b>\n\n"
            "Admin tekshirib, sizga xabar yuboradi. Iltimos kuting...",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Adminga chek yuborishda xatolik: {e}")
        await message.answer("⚠️ Texnik xatolik. Iltimos, to'g'ridan-to'g'ri adminga yozing.")

@dp.message(F.photo)
async def handle_general_photo(message: types.Message):
    user_id = message.from_user.id
    
    # Admin rasm tarqatish uchun yuklayotgan bo'lishi mumkin, AI tahlil qilmaydi
    if str(user_id) == str(ADMIN_ID):
        return

    # Agar rasm ostida buyruq yozilgan bo'lsa (masalan, /broadcast)
    if message.caption and message.caption.strip().startswith('/'):
        return

    if not database.check_ai_limit(user_id):
        await premium_upsell(message)
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if not gemini_client:
        await message.answer(
            "⚠️ Rasmlarni tahlil qilish uchun AI sozlanmagan.\n"
            "Iltimos, matnli savol yuboring.",
            reply_markup=get_start_keyboard()
        )
        return

    status_msg = await message.answer("🔍 <b>Rasm tahlil qilinmoqda...</b>", parse_mode="HTML")
    try:
        # Eng yuqori sifatli rasmni yuklab olamiz
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_path = file.file_path

        # Fayl baytlarini yuklab olamiz
        import io
        file_bytes = await message.bot.download_file(file_path)
        photo_data = file_bytes.read()

        # Base64 formatga o'tkazamiz
        import base64
        photo_b64 = base64.b64encode(photo_data).decode("utf-8")

        # Caption (tavsif) yozilgan bo'lsa uni qo'shib yuboramiz
        user_caption = message.caption or "Ushbu rasmdagi tibbiy holat bo'yicha tushuntirish va birinchi yordam choralarini bering."

        # Tibbiy profil ma'lumotlari
        profile = database.get_medical_profile(user_id)
        profile_context = _build_profile_context(profile)

        prompt_parts = [
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": photo_b64
                }
            },
            {
                "text": (
                    f"Rasmda tasvirlangan tibbiy holat, jarohat, toshma yoki boshqa tibbiyot/salomatlik bilan "
                    f"bog'liq vaziyatni tahlil qiling. Quyidagi savol yoki topshiriq asosida javob bering:\n"
                    f"\"{user_caption}\"\n\n"
                    f"Siz Birinchi Yordam AI botsiz. Javob o'zbek tilida, professional, samimiy va tushunarli bo'lsin. "
                    f"Kasalni davolashga urinmang, birinchi yordam choralarini ko'rsating va zarur bo'lsa "
                    f"tez yordam (103) yoki shifokorga murojaat qilishni qat'iy eslating.\n"
                    + profile_context
                )
            }
        ]

        # Gemini modellari orqali sinab ko'ramiz
        for model in GEMINI_MODELS:
            try:
                response = await gemini_client.aio.models.generate_content(
                    model=model,
                    contents=prompt_parts,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                if response.text:
                    await status_msg.edit_text(
                        f"📸 <b>Rasm tahlili natijasi:</b>\n\n"
                        + markdown_to_html(response.text),
                        parse_mode="HTML"
                    )
                    database.increment_usage(user_id)
                    return
            except Exception as e:
                err = str(e)
                if "429" in err or "404" in err or "RESOURCE_EXHAUSTED" in err or "NOT_FOUND" in err:
                    logging.warning(f"Rasm tahlilida {model} ishlamadi, keyingisiga o'tish...")
                    continue
                break

        await status_msg.edit_text(
            "⚠️ Rasmni tahlil qilish imkoni bo'lmadi.\n"
            "Iltimos, muammoni matn shaklida yozib yuboring. 📝",
            parse_mode="HTML"
        )

    except Exception as e:
        logging.error(f"Rasm tahlili handlerida xatolik: {e}")
        await status_msg.edit_text(
            "⚠️ Rasmni qayta ishlashda xatolik yuz berdi.\n"
            "Iltimos, matnli savol yuboring.",
            parse_mode="HTML"
        )

@dp.callback_query(F.data.startswith("adm_app_"))
async def process_admin_approve(callback: types.CallbackQuery):
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return
    user_id = int(callback.data.replace("adm_app_", ""))
    database.set_premium(user_id, 1)
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ <b>Tasdiqlandi! Premium berildi.</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 <b>Tabriklaymiz!</b>\n\n"
                "To'lovingiz tasdiqlandi va <b>Premium</b> obunangiz faollashtirildi!\n"
                "Endi AI yordamchisidan mutlaqo cheksiz foydalanishingiz mumkin. 🚀"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Foydalanuvchiga Premium xabari yuborib bo'lmadi: {e}")
    await callback.answer("Premium berildi!")

@dp.callback_query(F.data.startswith("adm_rej_"))
async def process_admin_reject(callback: types.CallbackQuery):
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return
    user_id = int(callback.data.replace("adm_rej_", ""))
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ <b>To'lov rad etildi.</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ <b>To'lovingiz tasdiqlanmadi.</b>\n\n"
                "Chek yoki to'lovda muammo aniqlandi. Ma'lumotlarni tekshirib, qaytadan urinib ko'ring."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Foydalanuvchiga rad xabari yuborib bo'lmadi: {e}")
    await callback.answer("To'lov rad etildi!")

# ═══════════════════════════════════════════════════════════════════
# FEATURE 7: 🔔 KUNLIK SOG'LIQ MASLAHATLARI
# ═══════════════════════════════════════════════════════════════════

@dp.message(F.text == "🔔 Kunlik Maslahatlar")
async def daily_tips_menu(message: types.Message):
    user_id = message.from_user.id
    status = database.get_daily_tips_status(user_id)
    builder = InlineKeyboardBuilder()
    if status == 1:
        builder.button(text="🔕 Obunani bekor qilish", callback_data="tips_unsubscribe")
        text = (
            "🔔 <b>Kunlik Sog'liq Maslahatlari</b>\n\n"
            "✅ Siz obuna bo'lgansiz!\n\n"
            "Har kuni ertalab soat <b>08:00</b> da sog'lik bo'yicha yangi maslahat olasiz. 🌅"
        )
    else:
        builder.button(text="🔔 Obuna bo'lish (bepul)", callback_data="tips_subscribe")
        text = (
            "🔔 <b>Kunlik Sog'liq Maslahatlari</b>\n\n"
            "Har kuni ertalab <b>08:00</b> da:\n"
            "• 🍎 Foydali ovqatlanish maslahatlari\n"
            "• 🏃 Kun uchun jismoniy mashqlar\n"
            "• 💊 Vitaminlar va sog'liq sirlari\n"
            "• 🧘 Stress va ruhiy salomatlik\n\n"
            "Obuna <b>mutlaqo bepul!</b>"
        )
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "tips_subscribe")
async def tips_subscribe(callback: types.CallbackQuery):
    database.set_daily_tips_subscription(callback.from_user.id, 1)
    await callback.message.edit_text(
        "✅ <b>Obuna bo'ldingiz!</b>\n\n"
        "Har kuni soat 08:00 da sog'liq bo'yicha yangi maslahat olasiz. 🌅\n\n"
        "Birinchi maslahat ertaga keladi!",
        parse_mode="HTML"
    )
    await callback.answer("✅ Obuna faollashtirildi!")

@dp.callback_query(F.data == "tips_unsubscribe")
async def tips_unsubscribe(callback: types.CallbackQuery):
    database.set_daily_tips_subscription(callback.from_user.id, 0)
    await callback.message.edit_text(
        "🔕 <b>Obuna bekor qilindi.</b>\n\n"
        "Istalgan vaqt qaytadan obuna bo'lishingiz mumkin.",
        parse_mode="HTML"
    )
    await callback.answer("Obuna bekor qilindi!")

async def send_daily_tips():
    """Har kuni ertalab 08:00 da barcha obunachilarga maslahat yuborish"""
    topics = [
        "bugungi kun uchun sabzavot va mevalar haqida eng foydali dietologik maslahat",
        "ertalabki jismoniy mashqlar va ularning foydasi haqida qisqa maslahat",
        "vitaminlar va minerallar: qaysi birlarini qabul qilish kerak va nima uchun",
        "stress va ruhiy salomatlikni yaxshilash uchun 3 ta amaliy tavsiya",
        "uyqu sifatini yaxshilash va salomatlikka ta'siri haqida maslahat",
        "suv ichish odati va organizmga foydasi haqida qiziqarli ma'lumot",
        "immunitetni mustahkamlash uchun tabiiy yo'llar va ovqatlar",
    ]

    import random
    topic = random.choice(topics)
    prompt = (
        f"O'zbek tilida qisqa, iliq va motivatsion sog'liq maslahati yoz ({topic} haqida). "
        f"Matn 200-300 so'zdan oshmaydi. Emoji bilan bezat. "
        f"Boshida 🌅 Bugungi Sog'liq Maslahati sarlavhasini yoz."
    )

    tip_text = await get_gemini_response(prompt)
    subscribers = database.get_daily_tips_subscribers()

    logging.info(f"Kunlik maslahat {len(subscribers)} ta obunachiga yuborilmoqda...")
    sent, failed = 0, 0
    for user_id in subscribers:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=markdown_to_html(tip_text),
                parse_mode="HTML"
            )
            sent += 1
            await asyncio.sleep(0.05)  # Flood limit oldini olish
        except Exception as e:
            logging.warning(f"Foydalanuvchi {user_id} ga maslahat yuborib bo'lmadi: {e}")
            failed += 1
    logging.info(f"Kunlik maslahat: {sent} muvaffaqiyatli, {failed} muvaffaqiyatsiz.")

# ═══════════════════════════════════════════════════════════════════
# FEATURE 2: DORI ESLATMASI SCHEDULER
# ═══════════════════════════════════════════════════════════════════

async def check_and_send_reminders():
    """Har daqiqa ishlab, dori vaqti kelganini tekshiradi"""
    from datetime import timezone, timedelta
    uz_tz = timezone(timedelta(hours=5))
    while True:
        now_time = datetime.now(uz_tz).strftime("%H:%M")
        reminders = database.get_all_active_reminders()
        for rem_id, user_id, medicine_name, times_str in reminders:
            times_list = [t.strip() for t in times_str.split(",")]
            if now_time in times_list:
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"💊 <b>Dori ichish vaqti!</b>\n\n"
                            f"🕐 Vaqt: <b>{now_time}</b>\n"
                            f"💊 Dori: <b>{medicine_name}</b>\n\n"
                            f"Sog'lig'ingizga e'tibor bering! 🌟"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logging.warning(f"Eslatma yuborib bo'lmadi (user: {user_id}): {e}")
        # Har 60 soniyada tekshiramiz
        await asyncio.sleep(60)

# ═══════════════════════════════════════════════════════════════════
# KUNLIK TAVSIYA SCHEDULER (har kuni 08:00 da)
# ═══════════════════════════════════════════════════════════════════

async def daily_tips_scheduler():
    """Har kuni 08:00 da kunlik maslahatlarni yuboradi"""
    from datetime import timezone, timedelta
    uz_tz = timezone(timedelta(hours=5))
    while True:
        now = datetime.now(uz_tz)
        # Keyingi 08:00 ni hisoblash
        target = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        logging.info(f"Keyingi kunlik maslahat {wait_seconds/3600:.1f} soatdan keyin yuboriladi.")
        await asyncio.sleep(wait_seconds)
        await send_daily_tips()

# ═══════════════════════════════════════════════════════════════════
# ADMIN BUYRUQLARI
# ═══════════════════════════════════════════════════════════════════


def _build_premium_list_keyboard(users_info):
    """Premium boshqaruv uchun keyboard quradi"""
    builder = InlineKeyboardBuilder()
    for row in users_info:
        user_id, is_premium = row[0], row[1]
        full_name = row[3] if len(row) > 3 else None
        username = row[4] if len(row) > 4 else None
        display = full_name or f"ID:{user_id}"
        status_icon = "🌟" if is_premium else "👤"
        action = "❌ Olib tashlash" if is_premium else "🌟 Premium berish"
        builder.button(
            text=f"{status_icon} {display} — {action}",
            callback_data=f"pm_toggle_{user_id}"
        )
    builder.button(text="🔄 Yangilash", callback_data="pm_refresh")
    builder.adjust(1)
    return builder.as_markup()


def _build_premium_list_text(users_info, total, premium_count):
    """Premium ro'yxat matni"""
    text = (
        f"💎 <b>Premium Boshqaruvi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"🌟 Premium foydalanuvchilar: <b>{premium_count}</b>\n\n"
        f"<b>So'nggi {len(users_info)} ta foydalanuvchi:</b>\n"
        "─────────────────\n"
    )
    for row in users_info:
        user_id, is_premium = row[0], row[1]
        full_name = row[3] if len(row) > 3 else None
        username = row[4] if len(row) > 4 else None
        icon = "🌟" if is_premium else "👤"
        name_str = full_name or "Noma'lum"
        uname_str = f" (@{username})" if username else ""
        prem_str = "Premium" if is_premium else "Oddiy"
        text += f"{icon} <b>{name_str}</b>{uname_str}\n"
        text += f"   🆔 <code>{user_id}</code>  |  {prem_str}\n\n"
    text += "Tugma bosib premium berishingiz yoki olib tashlashingiz mumkin 👇"
    return text


async def _resolve_users_info(users_info):
    """Foydalanuvchilar ismlari va usernamelarini Telegram'dan yuklab yangilaydi (agar yo'q bo'lsa)"""
    resolved = []
    for row in users_info:
        user_id, is_premium, reg_at = row[0], row[1], row[2]
        full_name = row[3] if len(row) > 3 else None
        username = row[4] if len(row) > 4 else None
        
        if not full_name:
            try:
                chat = await bot.get_chat(user_id)
                full_name = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or f"User {user_id}"
                username = chat.username
                database.register_user(user_id, full_name=full_name, username=username)
            except Exception:
                full_name = f"User {user_id}"
                
        resolved.append((user_id, is_premium, reg_at, full_name, username))
    return resolved


@dp.message(Command("premium"))
async def cmd_premium(message: types.Message):
    """Admin uchun interaktiv Premium boshqaruvi"""
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    raw_users = database.get_all_users_info(limit=15)
    users_info = await _resolve_users_info(raw_users)
    total = database.get_users_count()
    premium_count = database.get_premium_count()
    text = _build_premium_list_text(users_info, total, premium_count)
    markup = _build_premium_list_keyboard(users_info)
    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@dp.callback_query(F.data == "pm_refresh")
async def cb_pm_refresh(callback: types.CallbackQuery):
    """Premium ro'yxatini yangilash"""
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    raw_users = database.get_all_users_info(limit=15)
    users_info = await _resolve_users_info(raw_users)
    total = database.get_users_count()
    premium_count = database.get_premium_count()
    text = _build_premium_list_text(users_info, total, premium_count)
    markup = _build_premium_list_keyboard(users_info)
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("🔄 Yangilandi!")


@dp.callback_query(F.data.startswith("pm_toggle_"))
async def cb_pm_toggle(callback: types.CallbackQuery):
    """Foydalanuvchining premium holatini o'zgartirish"""
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    try:
        target_id = int(callback.data.replace("pm_toggle_", ""))
        # Hozirgi holatni aniq bilish
        raw_all = database.get_all_users_info(limit=100)
        current_status = 0
        for row in raw_all:
            uid = row[0]
            is_prem = row[1]
            if uid == target_id:
                current_status = is_prem
                break
        new_status = 0 if current_status else 1
        database.set_premium(target_id, new_status)
        action_text = "🌟 Premium berildi!" if new_status else "❌ Premium olib tashlandi!"
        await callback.answer(f"{action_text} (ID: {target_id})", show_alert=True)
        # Ro'yxatni yangilash
        raw_users = database.get_all_users_info(limit=15)
        users_info = await _resolve_users_info(raw_users)
        total = database.get_users_count()
        premium_count = database.get_premium_count()
        text = _build_premium_list_text(users_info, total, premium_count)
        markup = _build_premium_list_keyboard(users_info)
        try:
            await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        except Exception:
            pass
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Admin uchun statistika: /stats"""
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    total = database.get_users_count()
    premium = database.get_premium_count()
    subscribers = len(database.get_daily_tips_subscribers())
    reminders_count = len(database.get_all_active_reminders())
    await message.answer(
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"💎 Premium foydalanuvchilar: <b>{premium}</b>\n"
        f"🔔 Kunlik maslahat obunachilari: <b>{subscribers}</b>\n"
        f"💊 Faol dori eslatmalari: <b>{reminders_count}</b>",
        parse_mode="HTML"
    )


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    """Barcha foydalanuvchilarga xabar yuborish: /broadcast <matn> yoki reply qilib /broadcast"""
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    
    reply = message.reply_to_message
    text = None
    
    if not reply:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer(
                "📢 <b>Kanalga xabar tarqatish (Broadcast):</b>\n\n"
                "1. Biror xabarga reply qilib <code>/broadcast</code> deb yozing (rasm, video, ovoz va h.k. o'tadi)\n"
                "2. <code>/broadcast Xabar matni</code> shaklida yozing.",
                parse_mode="HTML"
            )
            return
        text = parts[1]
        
    users = database.get_all_users()
    sent, failed = 0, 0
    status = await message.answer(f"📢 {len(users)} ta foydalanuvchiga yuborilmoqda...")
    
    for user_id in users:
        try:
            if reply:
                # Xabarni barcha formatlari bilan to'liq nusxalab yuboramiz
                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=reply.message_id
                )
            else:
                # HTML parse xatolaridan himoya qilamiz
                try:
                    await bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
                except Exception:
                    await bot.send_message(chat_id=user_id, text=text, parse_mode=None)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
            
    await status.edit_text(
        f"✅ Broadcast tugadi!\n📤 Yuborildi: {sent}\n❌ Yuborib bo'lmadi: {failed}"
    )

@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    """Adminga foydalanuvchini ban qilish: /ban <user_id> [minutes]"""
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "Foydalanish: /ban <code>&lt;user_id&gt;</code> [daqiqalar]\n\n"
            "Masalan:\n"
            "• <code>/ban 12345678</code> (doimiy ban)\n"
            "• <code>/ban 12345678 60</code> (1 soatlik vaqtinchalik ban)",
            parse_mode="HTML"
        )
        return
    try:
        user_id = int(parts[1])
        minutes = int(parts[2]) if len(parts) >= 3 else None
        
        if str(user_id) == str(ADMIN_ID):
            await message.answer("❌ O'zingizni ban qila olmaysiz!")
            return
            
        database.ban_user(user_id, minutes)
        if minutes:
            await message.answer(f"✅ Foydalanuvchi {user_id} {minutes} daqiqaga vaqtinchalik ban qilindi.")
        else:
            await message.answer(f"✅ Foydalanuvchi {user_id} doimiy ban qilindi.")
    except ValueError:
        await message.answer("❌ Xatolik: user_id va daqiqalar soni butun son bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    """Adminga foydalanuvchini bandan chiqarish: /unban <user_id>"""
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "Foydalanish: /unban <code>&lt;user_id&gt;</code>\n\n"
            "Masalan: <code>/unban 12345678</code>",
            parse_mode="HTML"
        )
        return
    try:
        user_id = int(parts[1])
        database.unban_user(user_id)
        await message.answer(f"✅ Foydalanuvchi {user_id} bandan chiqarildi.")
    except ValueError:
        await message.answer("❌ Xatolik: user_id butun son bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# ═══════════════════════════════════════════════════════════════════
# AI CHAT (matnli savol)
# ═══════════════════════════════════════════════════════════════════

@dp.message(AiChatStates.chatting, F.text)
async def handle_ai_chat(message: types.Message, state: FSMContext):
    """Foydalanuvchining matnli savollariga Gemini AI orqali streaming javob"""
    
    # Reply tugmalarni tekshirish (ehtiyot chorasi sifatida qoldiramiz)
    skip_texts = [
        "📋 Holatlar ro'yxati", "🚨 Favqulodda raqamlar",
        "📚 Kasalliklar Ro'yxati (100+)", "💬 AI Konsultatsiya (Chat)",
        "🏥 Eng yaqin kasalxona", "💎 Premium olish",
        "👤 Tibbiy Profilim", "💊 Dori Eslatmalari",
        "⚖️ Sog'liq Kalkulyatori", "🔔 Kunlik Maslahatlar"
    ]
    if message.text in skip_texts:
        return

    user_id = message.from_user.id

    # 1 ta bepul savol tizimi: bepul savol ishlatilganmi tekshiramiz
    if database.check_free_ai_used(user_id):
        # Bepul limit tugagan — premium talab qilamiz
        builder = InlineKeyboardBuilder()
        builder.button(text="💎 Premium olish", callback_data="buy_premium")
        builder.adjust(1)
        await message.answer(
            "🔒 <b>Bepul AI savollar limiti tugadi!</b>\n\n"
            "Siz <b>1 ta bepul savol</b>dan foydalandingiz.\n"
            "AI bilan cheksiz suhbat qurish uchun <b>Premium</b> xarid qiling!\n\n"
            "🚀 <b>Premium afzalliklari:</b>\n"
            "• ♾️ Cheksiz AI so'rovlari\n"
            "• 🎙️ Ovozli konsultatsiya\n"
            "• 📚 Kasalliklar batafsil tahlili\n"
            "• 🩺 Shaxsiy tibbiy maslahat\n\n"
            f"⭐ <b>{PREMIUM_STARS_PRICE} Telegram Stars</b> — 1 oylik.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    placeholder = await message.answer("⏳ <b>Javob tayyorlanmoqda...</b>", parse_mode="HTML")

    # Tibbiy profilni qo'shish
    profile = database.get_medical_profile(user_id)
    profile_context = _build_profile_context(profile)
    full_prompt = message.text + profile_context

    await stream_gemini_to_message(
        prompt=full_prompt,
        message=placeholder,
        placeholder_text="⏳ <b>Javob tayyorlanmoqda...</b>"
    )
    # Bepul savolni ishlatdi deb belgilaymiz
    database.set_free_ai_used(user_id)
    database.increment_usage(user_id)

def _build_profile_context(profile) -> str:
    """Tibbiy profildan AI uchun kontekst yaratish"""
    if not profile:
        return ""
    blood_group, age, weight, height, chronic, allergies = profile
    parts = []
    if blood_group:
        parts.append(f"Qon guruhi: {blood_group}")
    if age:
        parts.append(f"Yoshi: {age}")
    if weight:
        parts.append(f"Vazni: {weight} kg")
    if height:
        parts.append(f"Bo'yi: {height} sm")
    if chronic:
        parts.append(f"Surunkali kasalliklar: {chronic}")
    if allergies:
        parts.append(f"Dorilarga allergiyalar: {allergies}")
    if not parts:
        return ""
    return "\n\n[Foydalanuvchi tibbiy ma'lumotlari (javobda hisobga oling): " + "; ".join(parts) + "]"

# ═══════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════

@dp.errors()
async def error_handler(event: types.ErrorEvent):
    logging.exception(f"Xatolik yuz berdi: {event.exception}")

# ═══════════════════════════════════════════════════════════════════
# BOT BUYRUQLARI RO'YXATI
# ═══════════════════════════════════════════════════════════════════

async def set_bot_commands(bot_instance: Bot):
    commands = [
        types.BotCommand(command="start",   description="Botni ishga tushirish"),
        types.BotCommand(command="menu",    description="Bosh menyu"),
        types.BotCommand(command="help",    description="Yordam va yo'riqnoma"),
        types.BotCommand(command="contacts",description="Tezkor telefon raqamlari"),
    ]
    await bot_instance.set_my_commands(commands)

    # Admin uchun maxsus komandalar (faqat adminga ko'rinadi)
    if ADMIN_ID and str(ADMIN_ID).isdigit():
        admin_commands = commands + [
            types.BotCommand(command="stats",       description="📊 Bot statistikasi"),
            types.BotCommand(command="broadcast",   description="📢 Ommaviy xabar yuborish"),
            types.BotCommand(command="premium",     description="💎 Premium faollashtirish"),
            types.BotCommand(command="ban",         description="🚫 Foydalanuvchini ban qilish"),
            types.BotCommand(command="unban",       description="✅ Bandan chiqarish"),
        ]
        try:
            await bot_instance.set_my_commands(
                commands=admin_commands,
                scope=types.BotCommandScopeChat(chat_id=int(ADMIN_ID))
            )
        except Exception as e:
            logging.error(f"Admin komandalarini o'rnatishda xatolik: {e}")

    # Chap burchakdagi ko'k "Menyu" tugmasini "Mini Ilova" tugmasiga almashtiramiz
    if MINI_APP_URL:
        try:
            await bot_instance.set_chat_menu_button(
                menu_button=types.MenuButtonWebApp(
                    text="🚑 Mini Ilova",
                    web_app=types.WebAppInfo(url=MINI_APP_URL)
                )
            )
            logging.info("Bosh menyu tugmasi Mini Ilova-ga muvaffaqiyatli almashtirildi.")
        except Exception as e:
            logging.error(f"Menu tugmasini Mini Ilovaga almashtirishda xato: {e}")

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

async def main():
    database.init_db()
    
    # Diagnostic: list available models to debug 404 NOT FOUND
    if gemini_client:
        try:
            print("🔍 Qaysi Gemini modellari mavjudligini tekshirmoqdamiz...")
            for m in gemini_client.models.list():
                # supported_actions might be a list or similar, we check if generateContent is supported
                actions = getattr(m, 'supported_actions', [])
                if any("generateContent" in str(a) for a in actions):
                    print(f"  - Model: {m.name}")
        except Exception as e:
            print(f"❌ Modellarni yuklashda xatolik: {e}")
            
    # Middleware-larni ro'yxatdan o'tkazish
    dp.message.outer_middleware(BanMiddleware())
    dp.callback_query.outer_middleware(BanMiddleware())
    dp.message.outer_middleware(FsmResetMiddleware())
    
    await set_bot_commands(bot)
    print("✅ Bot ishga tushdi!")
    print("📊 Barcha 7 ta yangi funksiya faol:")
    print("  1. 👤 Tibbiy Profil")
    print("  2. 💊 Dori Eslatmalari")
    print("  3. 🎙️ Ovozli Xabarlar")
    print("  4. 🗺️ Kasalxona + Dorixona")
    print("  5. ⚖️ Sog'liq Kalkulyatorlari")
    print("  6. 💳 Avtomatik To'lov")
    print("  7. 🔔 Kunlik Maslahatlar")

    # Background tasklar ishga tushiramiz
    asyncio.create_task(check_and_send_reminders())  # Feature 2: Dori eslatmalari
    asyncio.create_task(daily_tips_scheduler())       # Feature 7: Kunlik maslahatlar

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
