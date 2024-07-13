from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import asyncio
from modules.libraries.database import get_user, update_currency, update_goal

router = Router()

class SetupStates(StatesGroup):
    waiting_for_currency = State()
    waiting_for_goal = State()

class PiggyBankStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_currency = State()
    awaiting_goal = State()

class keyboards():
    main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu")]
    ])
    
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_name = message.from_user.full_name
    user = get_user(message.from_user.id)
    
    if user[1] == None and user[3] is None:
        await message.answer(f"👋 Привет, {user_name}! Я твоя личная копилка!\n🛠️ Для начала, давай настроим твою копилку.")
        await asyncio.sleep(1)
        await message.answer("Выбери валюту для твоей копилки (например, USD, BYN, KZT):")
        await state.set_state(SetupStates.waiting_for_currency)
    else:
        await show_main_menu(message)

@router.message(SetupStates.waiting_for_currency)
async def process_new_currency(message: Message, state: FSMContext):
    new_currency = message.text.upper()
    if len(new_currency) == 3 and new_currency.isalpha():
        update_currency(message.from_user.id, new_currency)
        user = get_user(message.from_user.id)
        await message.answer(f"✔ Валюта успешно изменена на {user[1]}.", reply_markup=keyboards.main_menu)
        await state.clear()
        await state.set_state(SetupStates.awaiting_goal)
    else:
        await message.answer("❌ Пожалуйста, введите корректный код валюты (например, USD, BYN, KZT).", reply_markup=keyboards.main_menu)

@router.message(PiggyBankStates.awaiting_goal)
async def set_goal(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    try:
        goal = float(message.text)
        update_goal(user_id, goal)
        updated_user = get_user(user_id)
        await message.answer(f"✔ Супер!\nТвоя цель накопления установлена на {goal:.2f} {updated_user[1]}.", reply_markup=keyboards.main_menu)
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введи корректную сумму для цели.", reply_markup=keyboards.main_menu)

        
@router.callback_query(F.data == 'main_menu')
async def show_main_menu(event: Message | CallbackQuery):
    is_callback = isinstance(event, CallbackQuery)
    user = event.from_user
    user_name = user.full_name
    user_data = get_user(user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить", callback_data="add"),
         InlineKeyboardButton(text="Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="Настройки", callback_data="settings")]
    ])
    
    text = f"👋 Привет, {user_name}!\n❕ Сейчас твоя цель {user_data[3]} {user_data[1]}.\n\nВыбери действие:"

    if is_callback:
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboard)