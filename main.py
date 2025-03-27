import asyncio
import logging, uuid
import sys, json
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
#exit()

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
SPONSORS = [-1001591752959, -1002563183053]
ADMIN_ID = 7161421601
USER_STATES = {}
TASKS = []


dp = Dispatcher()

kb = [
    [KeyboardButton(text="Заработать вирты 💲"),
    KeyboardButton(text="Мой баланс 💳")],
    [KeyboardButton(text="Продать/купить вирты 🤝")],
    [KeyboardButton(text="Вывести вирты 💱"),
    KeyboardButton(text="Отзывы о выводах ✅")],
    [KeyboardButton(text="Хочу стать спонсором ⚜️"),
    KeyboardButton(text="Задания💎")],
]
keyboard = ReplyKeyboardMarkup(keyboard=kb)


async def check_sponsor(message: Message):
    if str(message.from_user.id) in USER_STATES:
        USER_STATES.pop(str(message.from_user.id))

    user_id = message.from_user.id
    builder = InlineKeyboardBuilder()

    for id in SPONSORS:
        chat = await bot.get_chat(id)

        builder.row(InlineKeyboardButton(
        text=chat.full_name, url=await bot.export_chat_invite_link(id))
    )


    for id in SPONSORS:
        try:
            chat_member = await bot.get_chat_member(id, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                
                await message.answer("🖲️ Чтобы использовать данного бота, вам необходимо подписаться на всех спонсоров ↓", reply_markup=builder.as_markup())
                return False                

        except Exception as e:
            print(e)

    return True


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    with open("users.json", "r", encoding="UTF-8") as f:
        data_users = json.load(f)

    with open("referals.json", "r", encoding="UTF-8") as f:
        data_referal = json.load(f)

    ref = False
    if len(message.text.split()) > 1:
        if str(message.from_user.id) in data_users and data_users[str(message.from_user.id)]["url_used"] == True:
            pass
        else:
            ref = True
            custom_parameter = message.text.split()[1]
            print(custom_parameter)
            if custom_parameter in data_referal:
                data_users[data_referal[custom_parameter]]["money"] += 50000
                await bot.send_message(int(data_referal[custom_parameter]), f"Новый Реферал!\nИмя: {message.from_user.full_name}")
                with open("users.json", "w", encoding="UTF-8") as f:
                    json.dump(data_users, f, ensure_ascii=False, indent=4)
            
    if str(message.from_user.id) not in data_users:
        id = str(uuid.uuid4())
        user_data = {
            "url_used": bool(ref),
            "referal": id,
            "money": 0,
            "tasks": []
        }

        data_users[str(message.from_user.id)] = user_data
        data_referal[id] = str(message.from_user.id)

    else:
        data_users[str(message.from_user.id)]["url_used"] = True

    with open("users.json", "w", encoding="UTF-8") as f:
        json.dump(data_users, f, ensure_ascii=False, indent=4)

    with open("referals.json", "w", encoding="UTF-8") as f:
        json.dump(data_referal, f, ensure_ascii=False, indent=4)

        

    if not await check_sponsor(message):
        return

    await message.answer("Добро пожаловать в нашего телеграм бота «FarmVirt»! 👋\n\nИменно здесь у вас есть уникальная возможность заработать вирты на проекте Matreshka RP, всего лишь приглашая друзей по своей реферальной ссылке 👤", reply_markup=keyboard)

@dp.message(F.text == "Заработать вирты 💲")
async def earn(message: Message):
    if not await check_sponsor(message):
        return
    
    with open("users.json", "r", encoding="UTF-8") as f:
        data_users = json.load(f)

    url = data_users[str(message.from_user.id)]["referal"]
    await message.reply(f"Получай по 50.000 игровой валюты за одного приглашенного вами друга который перейдёт по вашей реферальной ссылке 👤\n\nСвою реферальную ссылку вы можете отправлять в личные сообщения своих друзей, группах и в различных телеграм каналах 🌐\n\nЧем больше вы приведете друзей, тем больше игровой валюты вы сможете заработать 🆙\n——————————\n🔗 Ваша реферальная ссылка: https://t.me/Damkrad_bot?start={url}")

@dp.message(F.text == "Мой баланс 💳")
async def balance(message: Message):
    if not await check_sponsor(message):
        return
    
    with open("users.json", "r", encoding="UTF-8") as f:
        data_users = json.load(f)

    money = data_users[str(message.from_user.id)]["money"]
    await message.reply(f"Ого! Вы привели так много друзей, продолжайте в том же духе ⚡️\n\n📋 Ваш баланс составляет: " + str(money))


@dp.message(F.text == "Продать/купить вирты 🤝")
async def buy_sell(message: Message):
    if not await check_sponsor(message):
        return
    
    await message.reply(f"Если вы желаете продать или купить вирты, то вы можете обратится к @Magnat_77 и совершить сделку ✅\n\nУ нас так же есть свой телеграм канал с отзывами о продажах и покупок виртов, поэтому просим вас ознакомиться @otzivi_magnat там 👀\n\nПродажа и скупка виртов исключительно от 1.000.000 игровой валюты (не меньше) ❗️")

@dp.message(F.text == "Отзывы о выводах ✅")
async def reviews(message: Message):
    if not await check_sponsor(message):
        return
    
    await message.reply(f"Не переживайте, мы категорически против обмана, поэтому именно у нас мы можете чувствовать себя спокойно 🤗\n\n🧑‍💻 Наш телеграм канал с отзывами о выводах виртов:\n\n@otizivi_vivod_magnat")

@dp.message(F.text == "Хочу стать спонсором ⚜️")
async def sponsor(message: Message):
    if not await check_sponsor(message):
        return
    
    await message.reply(f"Нажав на кнопку Хочу стать спонсором, должен быть текст:\nПредоставляем вам нашу услугу «Спонсор», она даёт вам возможность получать недорогую, и живую аудиторию в ваш телеграм канал 👥\n\nВ нашем телеграм боте действует ограничение на пользование, его можно будет использовать после подписок на всех спонсоров ✅\n\nПриобрести услугу «Спонсор» вы можете у @Magnat_77 (сверяйте юзер) ❗️")

@dp.message(F.text == "Вывести вирты 💱")
async def sponsor(message: Message):
    if not await check_sponsor(message):
        return
    
    USER_STATES[str(message.from_user.id)] = {
        "state": "server",
        "server": None,
        "bank": None,
        "virts": None
    }
    

    await message.reply(f"📝 Пожалуйста, введите номер вашего сервера ↓")

@dp.message(F.text == "Задания💎")
async def virt_giver(message: Message):
    print(123)
    if not await check_sponsor(message):
        return
    user_id = message.from_user.id

    with open("users.json", "r", encoding="UTF-8") as f:
        data_user = json.load(f)
    
    for task in TASKS:
        print(task)
        if task not in data_user[str(user_id)]["tasks"]:
            print(1)
            chat_member = await bot.get_chat_member(task, user_id)
            chat = await bot.get_chat(task)
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text=chat.full_name, url=await bot.export_chat_invite_link(task)))
            builder.row(InlineKeyboardButton(text="Проверить", callback_data="check_task"))
            await message.reply(f"Подпишитесь на канал и нажмите «Проверить»\n\nВознаграждение: +50000 виртов", reply_markup=builder.as_markup())
            return
            
    await message.reply(f"На данный момент заданий нет. Вы пока продолжайте приглашать рефералов, и возвращайтесь к нам позже.", reply_markup=keyboard)
    



@dp.callback_query()
async def virt_giver(call: CallbackQuery):
    print("callback")
    message = call.message
    user_id = call.from_user.id
    
    with open("users.json", "r", encoding="UTF-8") as f:
        data_user = json.load(f)
    
    for task in TASKS:
        if task not in data_user[str(user_id)]["tasks"]:
            chat_member = await bot.get_chat_member(task, user_id)
            if chat_member.status in ['member', 'administrator', 'creator']:
                
                data_user[str(user_id)]["tasks"].append(task)
                data_user[str(user_id)]["money"]+=50000

                with open("users.json", "w", encoding="UTF-8") as f:
                    json.dump(data_user, f, ensure_ascii=False, indent=4)

                await message.reply(f"Задание выполнено!\n\nВознаграждение: +50000 виртов", reply_markup=keyboard)
                return
    await message.reply(f"Похоже вы не выполнили задание или оно уже было выполненно", reply_markup=keyboard)
    
                

                



@dp.message()
async def virt_giver(message: Message):
    user_id = message.from_user.id
    if str(user_id) not in USER_STATES:
        return
    
    if USER_STATES[str(user_id)]["state"] == "server":
        try:
            int(message.text)
        except:
            await message.reply(f"Номер Сервера должен содержать только цифры")
            return
        
        USER_STATES[str(user_id)]["server"] = int(message.text)
        USER_STATES[str(user_id)]["state"] = "bank"
        await message.reply(f"📝 Пожалуйста, введите номер вашего банковского счёта ↓")
    
    elif USER_STATES[str(user_id)]["state"] == "bank":
        try:
            int(message.text)
        except:
            await message.reply(f"Номер Банковского счета должен содержать только цифры")
            return
        
        USER_STATES[str(user_id)]["bank"] = int(message.text)
        USER_STATES[str(user_id)]["state"] = "virt"
        await message.reply(f"💸 Отлично! Теперь укажите сумму для вывода виртов: ")

    elif USER_STATES[str(user_id)]["state"] == "virt":
        try:
            int(message.text)
        except:
            await message.reply(f"Количество виртов должно содержать только цифры")
            return
        
        with open("users.json", "r", encoding="UTF-8") as f:
            data_users = json.load(f)
        print(int(message.text) < 10**6)
        if data_users[str(user_id)]["money"] < int(message.text) or int(message.text) < 10**6:
            await message.reply(f"Упс! Кажется, что на вашем балансе недостаточно средств, видимо вы привели слишком мало друзей или вы ввели сумму меньше 1.000.000\n\n📋 Ваш баланс составляет: {data_users[str(user_id)]["money"]}", reply_markup=keyboard)
            USER_STATES.pop(str(user_id))
            return

        USER_STATES[str(user_id)]["virts"] = int(message.text)
        USER_STATES[str(user_id)]["state"] = "none"
        
        message_to_admin = f"Новая заявка на вывод виртов:\n\nСервер: {USER_STATES[str(user_id)]["server"]}\nБанк: {USER_STATES[str(user_id)]["bank"]}\nКол-во виртов: {USER_STATES[str(user_id)]["virts"]}"
        await bot.send_message(ADMIN_ID, message_to_admin)

        USER_STATES.pop(str(user_id))

        data_users[str(user_id)]["money"] -= int(message.text)

        with open("users.json", "w", encoding="UTF-8") as f:
            json.dump(data_users, f, ensure_ascii=False, indent=4)

        await message.reply("Готово! Ваша заявка на вывод виртов была отравлена модерации, обработка занимает до недели (обычно за сутки) ✅")


async def main() -> None:
    global bot
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())