# Main.py

# Библиотеки, тут немало

import re as R 
import sys 
import os

import asyncio as AS
import logging as LG
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram import F


# \/------------------------------------------<__________>--------------------------------------\/

#                                            < Переменные >

# \/------------------------------------------<‾‾‾‾‾‾‾‾‾‾>--------------------------------------\/


# ------------------- < Токен Сюда > -------------------
TOKEN = os.getenv("BOT_TOKEN")
# ------------------- <  /\ /\ /\  > ------------------


if not Token:
    if len(sys.argv) > 1:
        Token = sys.argv[1]
    else:
        print("❌ Ошибка: ТОКЕН НЕ НАЙДЕН! Задайте BOT_TOKEN в Amvera или передайте аргументом.")
        sys.exit(1)

config_path = "Config" # без .txt
TxtName = "Texts" # без .txt
TextData = {}

CrError = False

LG.basicConfig(level=LG.INFO)
bot = Bot(token=Token)
dp = Dispatcher()


# \/-----------------------------------------<_______>---------------------------------------\/

#                                            < Debug >

# \/-----------------------------------------<‾‾‾‾‾‾‾>---------------------------------------\/


class PrivatManager:
    def __init__(self, state, mode, usrList):
        
        if type(state) == bool:
            self.State = state
        else:
            self.State = False
        
        if type(mode) == str:
            self.Mode = mode.lower()
        else:
            self.Mode = "w"

        if type(usrList) == list:
            self.List = usrList
        else:
            self.List = []
        
    def ChangeConf(self, obj, NewVal):

        if obj in self.__dict__ and obj != "List":
            setattr(self, obj, NewVal)
            return True
            
        return False

    def ChangeList(self, key, obj):

        if key == "a":
            if type(obj) == str:
                if obj not in self.List: self.List.append(obj)

            elif type(obj) == list:
                for i in obj:
                    if i not in self.List: self.List.append(i)
        
        elif key == "d":

            if type(obj) == str:
                if obj in self.List: self.List.remove(obj)

            elif type(obj) == list:
                for i in obj:
                    if i in self.List: self.List.remove(i)
        
        elif key == "c":

            self.List.clear()

    def CheakList(self, obj):

        if type(obj) == list:
            finded = []

            for i in obj:
                if i in self.List:
                    finded.append(i)
            
            return finded

        if obj in self.List:
            return True
        
        return False

def IsAccessAllowed(manager, message):
    if not manager.State:
        return True

    username = message.from_user.username
    username = f"@{username}" if username else ""

    if manager.Mode == "w" and username not in manager.List:
        return False

    if manager.Mode == "b" and username in manager.List:
        return False

    return True 

MyPrivatManager = PrivatManager(False,"w",[]) 

# \/-----------------------------------------<_________>--------------------------------------\/

#                                            < Функции >

# \/-----------------------------------------<‾‾‾‾‾‾‾‾‾>--------------------------------------\/


# \/ --------------------------------------- < Работа с файлами > -- \/


#Все для удобства изменения , фильтер тут менять
def FileToDict():
    global TextData  

    try:
        with open(TxtName + ".txt", 'r', encoding='utf-8') as f:
            content = f.read()
            
            #--------------------------------------------------------------------------------------------
            # ТУТ ФИЛЬТР \/\/\/\/\/\/\/\/\/  переводя с кодерского s<КакоеТоСлово> Любой текст e<ТожеСлово>
            pattern = r"s<(\w+)>(.*?)e<\1>"
            #--------------------------------------------------------------------------------------------

            parsed = R.findall(pattern, content, R.DOTALL)
            
            TextData = {key: text.strip() for key, text in parsed}
            print(f"[Успешно] База TextData сформирована. Найдено блоков: {len(TextData)}")
            return True
            
    except FileNotFoundError:
        print(f"[Ошибка] Файл {TxtName}.txt нема! Создай его рядом с кодом.")
        return False
    
    except Exception as e:
        print(f"[Ошибка] Не удалось собрать TextData: {e}")
        return False
    
def LoadConfig(manager):
    global CrError
    config_path = "Config.txt"

    if not os.path.exists(config_path):
        print(f"Крит удар по боту, Файл {config_path} не найден")
        CrError = True
        return

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Обновленная регулярка: ищет блок <P> с 3 строками и блок <M> с 1 строкой
        privacy_match = R.search(r"<P>\s*([^\n]+)\s*([^\n]+)\s*([^\n]+)", content)
        maintenance_match = R.search(r"<M>\s*([^\n]+)", content)

        if privacy_match and maintenance_match:
            raw_state = privacy_match.group(1).strip().lower()
            raw_mode = privacy_match.group(2).strip().lower()
            raw_users = privacy_match.group(3).strip()
            raw_roots = maintenance_match.group(1).strip()

            # Загоняем данные приватности
            manager.State = True if raw_state == "true" else False
            manager.Mode = raw_mode if raw_mode in ["w", "b"] else "w"
            
            if raw_users and raw_users.lower() != "none":
                manager.List = [user.strip() for user in raw_users.split(",")]
            else:
                manager.List = []

            # Загоняем Root-админов (создаем новый параметр на лету или в __init__)
            if raw_roots and raw_roots.lower() != "none":
                manager.Root = [root.strip() for root in raw_roots.split(",")]
            else:
                manager.Root = []

            print("Приватность и Root-права успешно загружены через RE")
            print(f"> Статус: {manager.State} | Режим: {manager.Mode} | Юзеров: {len(manager.List)} | Админов: {len(manager.Root)}")
        else:
            print("Крит удар, блоки <P> или <M> обработаны некорректно!")
            CrError = True
    except Exception as e:
        print(f"Bot убит(а) игроком Critical Error используя: {e}")
        CrError = True

def SaveConfig(manager):
    global config_path

    try:
        users_str = ",".join(manager.List) if manager.List else "None"
        roots_str = ",".join(manager.Root) if manager.Root else "None"
        
        new_content = (
            f"<P>\n{manager.State}\n{manager.Mode}\n{users_str}\n\n"
            f"<M>\n{roots_str}"
        )

        with open(config_path + ".txt", "w", encoding="utf-8") as file:
            file.write(new_content)
        return True
    
    except Exception as e:
        print(f"А мама говорила, выберай web и не парься об: {e}")
        return False


# \/ --------------------------------------- < Команды для бота > - \/


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if not IsAccessAllowed(MyPrivatManager, message): return

    text = TextData.get("start", "Текста для <'start'> нет в файле.")
    await message.answer(text)


# \/ ---------------- < Создание Команд в промышленном масштабе > - \/


def create_handler(command_name):
    
    async def dynamic_handler(message: types.Message):
        if not IsAccessAllowed(MyPrivatManager, message): return
        
        text = TextData.get(command_name, f"Текста для <{command_name}> нет в файле.")
        await message.answer(text)

    return dynamic_handler


def MakeAllCommandsFromFile(dp):
    if not FileToDict():
        return False
        
    try:
        all_tags = list(TextData.keys())
        
        if not all_tags:
            print("В файле не найдено ни одного тега s<...>")
            return False
            
        print(f"Найдено тегов в файле: {len(all_tags)} -> {all_tags}")

        for word in all_tags:
            if word == "start":
                continue
                
            handler = create_handler(word)
            dp.message.register(handler, Command(word))
            print(f"Команда /{word} успешно создана автоматически!")
            
        return True

    except Exception as e:
        print(f"Что то не так, тут написано: {e}")
        return False


# \/ ---------------------------------------- < Ловим сообщения > - \/

@dp.message(F.text.startswith("!privat"))
async def EmulateCMD(message: types.Message):

    if not message.text or not message.text.startswith("!privat"):
        return

    username = message.from_user.username
    username = f"@{username}" if username else ""


    if not hasattr(MyPrivatManager, 'Root') or username not in MyPrivatManager.Root:
        await message.answer("Ты думал, что это роблокс?")
        return

    parts = message.text.split()
    
    if len(parts) < 2:
        await message.answer("Справка по командам( ЧИТАЙ README ):\n`!privat state true/false`\n`!privat mode w/b`\n`!privat add @user`\n`!privat del @user`\n`!privat clear`")
        return

    action = parts[1].lower()

    if action in ["state", "mode"]:
        if len(parts) < 3:
            await message.answer(f" А значние к {action} забыл")
            return
        
        raw_val = parts[2]

        if action == "state":
            new_val = True if raw_val.lower() == "true" else False
            param_name = "State"

        else:
            new_val = raw_val.lower()
            param_name = "Mode"

        if MyPrivatManager.ChangeConf(param_name, new_val):
            SaveConfig(MyPrivatManager)
            await message


# \/-----------------------------------------<________>--------------------------------------\/

#                                            < Запуск >

# \/-----------------------------------------<‾‾‾‾‾‾‾‾>--------------------------------------\/


async def main():
    global Token, CrError, bot

    if "--token" in sys.argv:
        TWidx = sys.argv.index("--token")
        Token = sys.argv[TWidx + 1]

    bot = Bot(token=Token)

    LoadConfig(MyPrivatManager)

    if CrError:
        print("Что-то легло, опять. Запуск отменен.")
        return

    try:
        MakeAllCommandsFromFile(dp)
        await bot.delete_webhook(drop_pending_updates=True)

        print(" Бот запущен, уже лучше чем у Яндекса ")
        await dp.start_polling(bot)

    except Exception as E:
        CrError = True
        print(f"боту kaputt, тут написано {E}.")

if __name__ == "__main__":
    AS.run(main())
