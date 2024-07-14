from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from modules.libraries.database import get_user, get_balance, update_balance, update_currency, update_goal
from modules.libraries.tfzolib import generators, keyboards, orders
import asyncio

router = Router()

@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    await callback.message.answer(f"🛠️ Настройки:", reply_markup=keyboards.settings)

@router.callback_query(F.data == 'add')
async def process_add(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    await callback.answer()
    await state.set_state(orders.PiggyBankStates.waiting_for_amount)
    await callback.message.answer(f"❕ Введите сумму в {user[1]} для добавления:", reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'remove')
async def process_remove(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    await callback.answer()
    await state.set_state(orders.PiggyBankStates.waiting_for_decrease_amount)
    await callback.message.answer(f"❕ Введите сумму в {user[1]} для удаления:", reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'change_currency')
async def process_change_currency(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(orders.PiggyBankStates.waiting_for_currency)
    await callback.message.answer("❕ Введите новую валюту (например: USD, BYN, KZT):", reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'change_goal')
async def change_goal(event: CallbackQuery | Message, state: FSMContext):
    if isinstance(event, CallbackQuery):
        user_id = event.from_user.id
        await event.message.answer("❔ Введите цель накопления:", reply_markup=keyboards.main_menu)
    elif isinstance(event, Message):
        user_id = event.from_user.id
        await event.answer("❔ Введите цель накопления:", reply_markup=keyboards.main_menu)
        return

    await state.update_data(user_id=user_id)
    await state.set_state(orders.PiggyBankStates.awaiting_goal)

@router.message(orders.PiggyBankStates.awaiting_goal)
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

@router.message(orders.PiggyBankStates.waiting_for_decrease_amount, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_decrease_amount(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)   
    try:
        damount = float(message.text)
        user_id = message.from_user.id
        u_b = update_balance(user_id, damount, True)
        updated_user = get_user(user_id)
        await message.answer(f"{u_b}", reply_markup=keyboards.main_menu)
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму.", reply_markup=keyboards.main_menu)

@router.message(orders.PiggyBankStates.waiting_for_amount, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_amount(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)   
    
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        u_b = update_balance(user_id, amount)
        updated_user = get_user(user_id)
        await message.answer(f"{u_b} {generators.motivation_gen()}.", reply_markup=keyboards.main_menu)
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму.", reply_markup=keyboards.main_menu)

@router.message(orders.PiggyBankStates.waiting_for_currency)
async def process_new_currency(message: Message, state: FSMContext):
    new_currency = message.text.upper()
    if len(new_currency) == 3 and new_currency.isalpha():
        update_currency(message.from_user.id, new_currency)
        user = get_user(message.from_user.id)
        await message.answer(f"✔ Валюта успешно изменена на {user[1]}.", reply_markup=keyboards.main_menu)
        await state.clear()
    else:
        await message.answer("❌ Пожалуйста, введите корректный код валюты (например, USD, EUR, RUB).", reply_markup=keyboards.main_menu)

@router.message(orders.PiggyBankStates.waiting_for_amount)
async def process_invalid_amount(message: Message):
    await message.answer("❌ Пожалуйста, введите корректную сумму (только цифры и точка).", reply_markup=keyboards.main_menu)

