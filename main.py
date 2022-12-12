import logging
import random
import string

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Класс позволяет хранить данные в оперативной памяти
from aiogram.dispatcher import Dispatcher, FSMContext  # Машина состояний
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram.dispatcher.filters import Text
from aiogram_dialog import DialogManager, ChatEvent
from aiogram_dialog.widgets.kbd import Checkbox, ManagedCheckboxAdapter
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import Dialog
from aiogram_dialog import DialogRegistry
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
import operator

from aiogram_dialog.widgets.kbd import Multiselect
from aiogram_dialog.widgets.text import Format

from config import botToken

# Монго и аюредис

logging.basicConfig(level=logging.INFO)

bot = Bot(token=botToken)
dp = Dispatcher(bot, storage=MemoryStorage())



button_yes = KeyboardButton('Да')
button_no = KeyboardButton('Нет')
button_test = KeyboardButton('Setting')


button_case = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).add(button_yes) \
    .add(button_no).add(button_test)

inline_button = InlineKeyboardButton(text="Инлайн кнопка",
                                     url='vk.com')
button_inline_case = InlineKeyboardMarkup(row_width=1).add(inline_button)

numbers = string.digits
upper_letters = string.ascii_uppercase
symbols = string.punctuation
password = string.ascii_lowercase
numb = 5

class MySG(StatesGroup):
    numberOfCharacters = State()
    special_characters = State()
    numbers = State()
    upperLetterts = State()
    passw = State()


async def check_changed(event: ChatEvent, checkbox: ManagedCheckboxAdapter, manager: DialogManager):
    print("Check status changed:", checkbox.is_checked())

# async def go_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
#     await c.message.answer("Going on!")

# go_btn = Button(
#     Const("Go"),
#     id="go",  # id is used to detect which button is clicked
#     on_click=go_clicked,
# )


main_window = Window(
    Const(f"<b>Привет, я помогу тебе придумать надежный пароль</b>!\nСколько символов будет в пароле?"),  # just a constant text
    Checkbox(
        Const("✓ Добавить символы"),
        Const("Убрать символы"),
        id="check",
        default=True,  # so it will be checked by default,
        on_state_changed=check_changed,
    ),  # button with text and id
    Checkbox(
        Const("✓ Добавить цифры"),
        Const("Убрать цифры"),
        id="check",
        default=True,  # so it will be checked by default,
        on_state_changed=check_changed,
    ),
    state=MySG.numberOfCharacters,  # state is used to identify window between dialogs
)

dialog = Dialog(main_window)



registry = DialogRegistry(dp)  # this is required to use `aiogram_dialog`
registry.register(dialog)

@dp.message_handler(commands="sd", state=None)
async def load_numberOfCharacters(message: types.Message,  dialog_manager: DialogManager):
    global password
    await dialog_manager.start(f"<b>Привет, я помогу тебе придумать надежный пароль</b>!\nСколько символов будет в пароле?",
                         )


@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(MySG.numberOfCharacters, mode=StartMode.RESET_STACK)


class FSMAdmin(StatesGroup):
    numberOfCharacters = State()
    special_characters = State()
    numbers = State()
    upperLetterts = State()
    passw = State()


@dp.message_handler(commands="ki", state=None)
async def load_numberOfCharacters(message: types.Message):
    global password
    await FSMAdmin.numberOfCharacters.set()
    await message.answer(f"<b>Привет, я помогу тебе придумать надежный пароль</b>!\nСколько символов будет в пароле?",
                         parse_mode="HTML")

# @dp.message_handler(state="*", commands='Setting')

@dp.message_handler(state=FSMAdmin.numberOfCharacters)
async def load_numberOfCharacters(message: types.Message, state: FSMContext):
    global password
    async with state.proxy() as data:
        try:
            data['numberOfCharacters'] = int(message.text)
        except ValueError:
            await message.reply("Сколько символов будет в пароле?")
            data['numberOfCharacters'] = int(message.text)

    await FSMAdmin.next()
    print(data['numberOfCharacters'])
    await message.reply("Добавить спец.символы?", reply_markup=button_case)


@dp.message_handler(state=FSMAdmin.special_characters)
async def load_special_characters(message: types.Message, state: FSMContext):
    global password
    async with state.proxy() as data:
        data['specialСharacters'] = message.text
    await FSMAdmin.next()
    await message.reply("Добавить цифры?", reply_markup=button_case)
    password += symbols


@dp.message_handler(state=FSMAdmin.numbers)
async def load_numbers(message: types.Message, state: FSMContext):
    global password
    async with state.proxy() as data:
        data['numbers'] = message.text
    await FSMAdmin.next()
    await message.reply("Добавить буквы в верхнем регистре?", reply_markup=button_case)
    password += numbers


@dp.message_handler(state=FSMAdmin.upperLetterts)
async def load_upperLetterts(message: types.Message, state: FSMContext):
    global password
    async with state.proxy() as data:
        data['upperLetterts'] = message.text
    password += upper_letters
    await message.reply("Сгенерировать?", reply_markup=button_case)
    if message.text == "Да":
        await FSMAdmin.next()
        await message.reply("Сгенерировать?", reply_markup=button_case)
    else:
        print("ddd")


@dp.message_handler(state=FSMAdmin.passw)
async def load_passw(message: types.Message, state: FSMContext):
    global password
    async with state.proxy() as data:
        x = "".join(random.sample(password, data['numberOfCharacters']))

    await message.answer(f'<b>Ваш пароль:</b> <code>{x}</code>', parse_mode="HTML")
    await state.reset_data()
    await state.finish()





@dp.message_handler(commands=["Setting"])
async def get_data(message: types.Message):

    await bot.send_message(chat_id=message.from_user.id,
                           text='Кнопка',
                           reply_markup=button_inline_case)





executor.start_polling(dp, skip_updates=True, )
