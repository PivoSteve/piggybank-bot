from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import asyncio
from modules.libraries.database import get_user, update_currency, update_goal, reset
from modules.libraries.tfzolib import keyboards, orders

router = Router()
    
@router.message(Command("start"))
async def cmd_start(event: Message | CallbackQuery, state: FSMContext):
    is_callback = isinstance(event, CallbackQuery)
    user_name = event.from_user.full_name
    user_data = get_user(event.from_user.id)
    user = get_user(event.from_user.id)
    
    if is_callback:
        if user[1] == None and user[3] is None:
            await event.message.edit_text(f"👋 Привет, {user_name}! Я твоя личная копилка!\n🛠️ Для начала, давай настроим всё что нужно...")
            await asyncio.sleep(.3)
            await event.message.answer("❔ Выбери валюту для твоей копилки (например, USD, BYN, KZT):")
            await event.answer()
            await state.set_state(orders.SetupStates.waiting_for_currency)
        else:
            await show_main_menu(event)
    else:
        if user[1] == None and user[3] is None:
            await event.answer(f"👋 Привет, {user_name}! Я твоя личная копилка!\n🛠️ Для начала, давай настроим всё что нужно.")
            await asyncio.sleep(.3)
            await event.answer("❔ Выбери валюту для твоей копилки (например, USD, BYN, KZT):")
            await state.set_state(orders.SetupStates.waiting_for_currency)
        else:
            await show_main_menu(event)

@router.callback_query(F.data == 'reset')
@router.message(Command("reset"))
async def cmd_reset(event: Message | CallbackQuery, state: FSMContext):
    is_callback = isinstance(event, CallbackQuery)
    user = event.from_user
    user_name = user.full_name
    user_data = get_user(user.id)
    
    if is_callback:
        if user_data[1] == None and user_data[3] is None:
            await event.message.edit_text(f"👋 Привет, {user_name}! Я твоя личная копилка!\n🛠️ Для начала, давай настроим всё что нужно.")
            await asyncio.sleep(.3)
            await event.message.edit_text("❔ Выбери валюту для твоей копилки (например, USD, BYN, KZT):")
            await event.answer()
            await state.set_state(orders.SetupStates.waiting_for_currency)
        else:
            if user_data[4] == True:
                await event.message.edit_text(f"❕ Вы уверены, что хотите сбросить копилку?\n💰 Ваш текущий баланс: {user_data[2]:.2f} {user_data[1]}", reply_markup=keyboards.reset)
                await event.answer()
            else:
                await event.message.edit_text(f"❕ Вы уверены, что хотите сбросить копилку?\n💰 Ваш текущий баланс: {user_data[2]:.2f} {user_data[1]}\n⚠️ Цель {user_data[3]} {user_data[1]} еще не достигнута!", reply_markup=keyboards.reset)
                await event.answer()
    else:
        if user_data[1] == None and user_data[3] is None:
            await event.answer(f"👋 Привет, {user_name}! Я твоя личная копилка!\n🛠️ Для начала, давай настроим всё что нужно.")
            await asyncio.sleep(.3)
            await event.answer("❔ Выбери валюту для твоей копилки (например, USD, BYN, KZT):")
            await state.set_state(orders.SetupStates.waiting_for_currency)
        else:
            if user_data[4] == True:
                await event.answer(f"❕ Вы уверены, что хотите сбросить копилку?\n💰 Ваш текущий баланс: {user_data[2]:.2f} {user_data[1]}", reply_markup=keyboards.reset)
            else:
                await event.answer(f"❕ Вы уверены, что хотите сбросить копилку?\n💰 Ваш текущий баланс: {user_data[2]:.2f} {user_data[1]}\n⚠️ Цель {user_data[3]} {user_data[1]} еще не достигнута!", reply_markup=keyboards.reset)

    
@router.message(orders.SetupStates.waiting_for_currency)
async def process_new_currency(message: Message, state: FSMContext):
    new_currency = message.text.upper()
    user_id = message.from_user.id
    if len(new_currency) == 3 and new_currency.isalpha():
        update_currency(user_id, new_currency)
        user = get_user(user_id)
        await message.answer(f"✔ Отлично!\n❔ Теперь введи цель накопления:")
        await state.clear()
        await state.update_data(user_id=user_id)
        await state.set_state(orders.SetupStates.awaiting_goal)
    else:
        await message.answer("❌ Пожалуйста, введите корректный код валюты (например, USD, BYN, KZT).", reply_markup=keyboards.main_menu)
    

@router.message(orders.SetupStates.awaiting_goal)
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
    
    text = f"👋 Привет, {user_name}!\n❕ Сейчас твоя цель {user_data[3]} {user_data[1]}.\n💰 Ваш текущий баланс: {user_data[2]:.2f} {user_data[1]}\n\nВыбери действие:"

    if is_callback:
        await event.message.edit_text(text, reply_markup=keyboards.main)
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboards.main)

@router.callback_query(F.data == 'reset_confirmed')
async def reset_confirmed_handler(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    reset(callback.from_user.id)
    await callback.message.edit_text(f"❕ Ваша копилка была сброшена.\nСекунду...")
    await asyncio.sleep(1)
    await cmd_start(callback, state)
    

