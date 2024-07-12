from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from modules.libraries.database import get_user, get_balance, update_balance, update_currency, update_goal
import modules.libraries.tfzolib as lib
import asyncio

router = Router()

class PiggyBankStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_currency = State()
    awaiting_goal = State()

class keyboards():
    main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu")]
    ])

@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💱 Изменить валюту", callback_data="change_currency"),
         InlineKeyboardButton(text="💰 Изменить цель", callback_data="change_goal")]
    ])
    await callback.message.answer(f"🛠️ Настройки:", reply_markup=keyboard)

@router.callback_query(F.data == 'add')
async def process_add(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    await callback.answer()
    await state.set_state(PiggyBankStates.waiting_for_amount)
    await callback.message.answer(f"❕ Введите сумму в {user[1]} для добавления:", reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'balance')
async def process_balance(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(f"✔ Ваш текущий баланс: {user[2]:.2f} {user[1]}", reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'change_currency')
async def process_change_currency(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(PiggyBankStates.waiting_for_currency)
    await callback.message.answer("❕ Введите новую валюту (например: USD, BYN, KZT):", reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'change_goal')
async def change_goal(event: CallbackQuery | Message, state: FSMContext):
    if isinstance(event, CallbackQuery):
        user_id = event.from_user.id
        await event.message.answer("❕ Теперь давай установим цель накопления.\nВведи сумму:", reply_markup=keyboards.main_menu)
    elif isinstance(event, Message):
        user_id = event.from_user.id
        await event.answer("❕ Теперь давай установим цель накопления.\nВведи сумму:", reply_markup=keyboards.main_menu)
        return

    await state.update_data(user_id=user_id)
    await state.set_state(PiggyBankStates.awaiting_goal)

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

@router.message(PiggyBankStates.waiting_for_amount, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_amount(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)   
    
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        update_balance(user_id, amount)
        updated_user = get_user(user_id)
        await message.answer(f"✔ Отлично!\n{amount:.2f} {updated_user[1]} добавлено к вашим сбережениям! {lib.generators.motivation_gen()}.", reply_markup=keyboards.main_menu)
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму.", reply_markup=keyboards.main_menu)

@router.message(PiggyBankStates.waiting_for_currency)
async def process_new_currency(message: Message, state: FSMContext):
    new_currency = message.text.upper()
    if len(new_currency) == 3 and new_currency.isalpha():
        update_currency(message.from_user.id, new_currency)
        user = get_user(message.from_user.id)
        await message.answer(f"✔ Валюта успешно изменена на {user[1]}.", reply_markup=keyboards.main_menu)
        await state.clear()
    else:
        await message.answer("❌ Пожалуйста, введите корректный код валюты (например, USD, EUR, RUB).", reply_markup=keyboards.main_menu)

@router.message(PiggyBankStates.waiting_for_amount)
async def process_invalid_amount(message: Message):
    await message.answer("❌ Пожалуйста, введите корректную сумму (только цифры и точка).", reply_markup=keyboards.main_menu)

