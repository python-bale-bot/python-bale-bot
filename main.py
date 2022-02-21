from bale_api import Update
import datetime
import jdatetime
from requests import post, get 
from requests.exceptions import ConnectTimeout
from jdatetime import timedelta
from sqlite3 import connect, OperationalError
from keyboard import wait
from time import sleep

class BaleApp():
    def __init__(self, token:str, base_url:str, base_file_url:str, offset : int = None):
        self.token = token
        self.base_url = base_url
        self.base_file_url = base_file_url
        print("Check Token...")
        checkbot = get(f"{self.base_url}bot{token}/getme", timeout = (20, 20))
        if not checkbot.ok:
            raise "Token is Invalid"

        self.bot = checkbot.json()["result"]
        self.wait_for = {}
        print('Bot Started!')

        while True:
            try:
                if offset:
                    updates = post(f"{self.base_url}bot{self.token}/getupdates", json = {"offset" : offset + 1})
                    if updates.json()["result"] == []:
                        pass
                    elif int(updates.json()["result"][-1]["update_id"]) == offset:
                        pass
                    else:
                        offset = int(updates.json()["result"][-1]["update_id"])
                        updates = updates.json()["result"]
                        for update in updates:
                            if "callback_query" in update:
                                update = Update(update, self)
                                self.button_click(update, None, self.bot)
                            else:
                                update = Update(update, self)
                                self.on_message(update, None, self.bot)
                
                elif offset is None:
                    updates = post(f"{self.base_url}bot{self.token}/getupdates")
                    if updates.json()["result"] != []:
                        offset = int(updates.json()["result"][-1]["update_id"])
                        updates = updates.json()["result"]
                        for update in updates:
                            if "callback_query" in update:
                                update = Update(update, self)
                                self.button_click(update, None, self.bot)
                            else:
                                update = Update(update, self)
                                self.on_message(update, None, self.bot)
                sleep(5.0)
            except Exception as error:
                print(error)
     
    def send_message(self, chat_id, text, reply_markup = None, reply_to_message_id = None, token : str =  None):
        json = {}
        json["chat_id"] = f"{chat_id}"
        json["text"] = f"{text}"
        if reply_markup:
            json["reply_markup"] = reply_markup
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        msg = post(url = f"{self.base_url}bot"+ (f"{token}" if token is not None else f"{self.token}") +"/sendMessage", json = json, timeout = (10, 15)) 
        return msg.json()
    
    def delete_message(self, chat_id, message_id, token : str = None):
        msg = get(f"{self.base_url}bot"+ f"{token}" if token is not None else f"{self.token}" +"/deletemessage", params = {
            "chat_id": f"{chat_id}",
            "message_id": f"{message_id}"
        }, timeout = (10, 15))
        return msg.json()
    
    def check_command(self, update, if_message = True):
        if if_message:
            user_id = str(update.message.chat_id)
            if user_id in self.wait_for:
                del self.wait_for[user_id]
                update.message.reply_message(text = '*📛عملیات لغو شد!📛*')       
        else:
            user_id = str(update.message.chat_id)
            data = update.data
            if self.wait_for.get(user_id) is None:
                if data == 'cancel':
                    return False
            elif self.wait_for.get(user_id) == data:
                return False
            elif data.startswith(self.wait_for.get(user_id)):
                pass         
            else:
                del self.wait_for[user_id]
                update.message.reply_message(text = '*📛عملیات لغو شد!📛*')
                self.setting(update, None, self.bot)
                if data == 'cancel':
                    return False
        return True
    
    def check_message_command(self, update, context, bot):
        user_id = str(update.message.message_id)
        if self.wait_for.get(user_id) is not None:
            if self.wait_for[user_id] == 'set_start_present_time':
                self.set_start_present_time(update, context, self.bot, status = update.message.text)
            elif self.wait_for[user_id] == 'set_end_present_time':
                self.set_end_present_time(update, context, self.bot, status = update.message.text)
            else:
                pass
            
    def check_error(self, update, context, error, send_error = False):
        if type(error) is OperationalError:
            return update.message.reply_message(text = '❌ *در ارتباط با دیتا بیس به مشکل خوردم!* ❌')    
        elif type(error) is ConnectTimeout:
            pass
        else:
            print("new error")
            errorfile = open ("./erros.txt", "a+")
            errorfile.write(f"{error}\n\n")
            print(error)
            errorfile.close()
            if send_error:
                return update.message.reply_message(text = '❌ *به یک مشکل نا شناخته برخوردم!* ❌')   
            
    
    def on_message(self ,update, context, bot):
        try:
            if update.message.chat_type == 'private' and str(update.message.author.id) != bot["id"]:
                db = connect('./data.db')
                cursor = db.cursor()
                sql = ('INSERT INTO messages(chat_id, message_id, time, text, user_name, user_id, first_name, last_name, type) VALUES(?,?,?,?,?,?,?,?,?)')
                val = (update.message.chat_id, update.message.message_id, f"{update.message.date}", update.message.text, '@' + update.message.author.username, str(update.message.author.id), update.message.author.first_name, update.message.author.last_name, 'message')
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                
                if update.message.text == '/start' or update.message.text == '/help' or update.message.text == 'شروع':
                    if not self.check_command(update):
                        return
                    return self.start(update, context, bot)
                elif update.message.text == 'سازندگان':
                    if not self.check_command(update):
                        return
                    return self.developers(update, context, bot) 
                elif update.message.text.startswith("/send_message"):
                    m = self.send_message(chat_id = update.message.text.split("|")[1], text = update.message.text.split("|")[2])
                    update.message.reply_message(text = f"""```[اطلاعات پیام ارسال شده]
Message ID = {m['result']['message_id']}
Text : {m['result']['text']}
Chat ID : {m['result']['chat']['id']}```""")
                else:
                    return self.check_message_command(update, context, bot)
        except Exception as error:
            self.check_error(update, context, error)
            
    def start(self, update, context, bot):
        try:
            if update.message.author.is_bot_admin():
                return update.message.reply_message(text = '* در خدمتم🙏\n👇لطفا برای استفاده از دستورات گزینه موردنظر را از منوی زیر انتخاب نمایید! 👇 *', reply_markup = { "inline_keyboard": [[{"text" : 'دریافت لیست حاضران', "callback_data" : 'get_present_list'}, {"text" : 'تنظیمات بات', "callback_data" : 'setting'}], [{"text" : 'سازندگان', "callback_data" : 'developer'}]]})
            else:
                db = connect('./data.db')
                cursor = db.cursor()
                cursor.execute("SELECT condition_present FROM setting")
                (status,) = cursor.fetchone()
                if status:
                    date = update.message.date.strftime('%Y-%m-%d-%H-%M').split('-')
                    cursor.execute("SELECT start_present_time, end_present_time FROM setting")
                    (start_time, time_end) = cursor.fetchone()
                    cursor.close()
                    db.close()
                    (hour_start, minute_start) = str(start_time).split(':')
                    (hour_end, minute_end) = str(time_end).split(':')
                    start_time = jdatetime.datetime.strptime(f'{date[0]}/{date[1]}/{date[2]}/{hour_start}/{minute_start}', '%Y/%m/%d/%H/%M')
                    time_end = jdatetime.datetime.strptime(f'{date[0]}/{date[1]}/{date[2]}/{hour_end}/{minute_end}', '%Y/%m/%d/%H/%M')
                    time_now = update.message.date
                    if int(hour_start) > int(hour_end):
                        time_end += timedelta(days = 1)
                    if time_now >= start_time and time_now <= time_end:
                        msg = update.message.reply_message(text = '👇لطفا از طریق منوی زیر، گزینه *من حاضرم* را برای تائید حضور خود انتخاب نمایید',reply_markup = {"keyboard": [[{"text":"شروع"}]]})
                        return update.message.reply_message(text = '[در صورتی که گزینه ای نمیبینید بله خود را آپدیت نمایید](https://bale.ai/#download)\n\n[سازندگان بات](send:سازندگان)', reply_markup = { "inline_keyboard": [[{"text": "من حاضرم", "callback_data": f'run_command|{msg["message_id"]}'}]]})
                    else:
                        return update.message.reply_message(text = f'📛کاربر گرامی شما فقط میتوانید در بین ساعت `{hour_start}:{minute_start}` تا `{hour_end}:{minute_end}` درخواست حضور خود را تائید کنید📛', reply_markup = { "inline_keyboard": [[{"text": "سازندگان بات", "callback_data": "developer"}]]})
                else:
                    cursor.close()
                    db.close()
                    return update.message.reply_message(text = f"❌ *وضعیت حضور و غیاب توسط ادمین غیر فعال شده است!* ❌", reply_markup = {"keyboard": [[{"text":"شروع"}]]})
        except Exception as error:
            return self.check_error(update, context, error)
        
    def button_click(self, update, _, bot):
        try:
            db = connect('./data.db')
            cursor = db.cursor()
            sql = ('INSERT INTO messages(chat_id, message_id, time, text, user_name, user_id, first_name, last_name, type) VALUES(?,?,?,?,?,?,?,?,?)')
            val = (update.message.chat_id, update.message.message_id, f"{update.message.date}", 'None', '@' + update.message.author.username, update.message.author.id, update.message.author.first_name,update.message.author.last_name, 'InlineKeyboard - ' + update.data)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            if not self.check_command(update, if_message = False):
                return
            
            
            if update.data.startswith('run_command'):
                return self.action(update, _, bot)
            elif update.data == 'developer':
                return self.developers(update, _, bot)
            elif update.data == 'setting':
                return self.setting(update, _, bot)
            elif update.data in ['condition_present','condition_present_yes','condition_present_no']:
                if update.message.author.is_bot_admin(return_msg_to_user = True):
                    if update.data == 'condition_present':
                        return self.condition_present(update, _, bot)
                    elif update.data == 'condition_present_yes' or update.data == 'condition_present_no':
                        return self.condition_present(update, _, bot, status = update.data.split('condition_present_')[1])
                        
            elif update.data == 'set_start_present_time':
                if update.message.author.is_bot_admin(return_msg_to_user = True):
                    return self.set_start_present_time(update, _, bot)
                    
            elif update.data == 'set_end_present_time':
                if update.message.author.is_bot_admin(return_msg_to_user = True):
                    return self.set_end_present_time(update, _, bot)
            else:
                return update.message.reply_message(text = '*✅این بخش در حال آپدیت است تا آپدیت کامل صبر کنید📛*', reply_markup = { "inline_keyboard": [[{"text": "سازندگان بات", "callback_data": "developer"}]]})
        
        except Exception as error:
            self.check_error(update, _, error)       

    def action(self, update, context, bot):
        try:
            if update.message.author.is_bot_admin(return_msg_to_user = False):
                update.message.reply_message(chat_id = update.message.author.id, text = '* 📛ادمین گرامی این بخش مخصوص کاربران عادی است!📛 *' )
            else:
                db = connect('./data.db')
                cursor = db.cursor()
                cursor.execute("SELECT condition_present FROM setting")
                (status,) = cursor.fetchone()
                if status:
                    try:
                        date = (jdatetime.datetime.fromgregorian(datetime = datetime.datetime.fromtimestamp(update.message.date_code)) + timedelta(hours = 3, minutes = 30)).strftime('%Y-%m-%d-%H-%M').split('-')
                        y, m, d, H, M  = jdatetime.datetime.now().strftime('%Y-%m-%d-%H-%M').split('-')
                        if y == date[0] and m == date[1] and d == date[2]:
                            cursor.execute("SELECT start_present_time, end_present_time FROM setting")
                            (time_start, time_end) = cursor.fetchone()
                            (hour_start, minute_start) = str(time_start).split(':')
                            (hour_end, minute_end) = str(time_end).split(':')
                            time_start = jdatetime.datetime.strptime(f'{y}/{m}/{d}/{hour_start}/{minute_start}', '%Y/%m/%d/%H/%M')
                            time_end = jdatetime.datetime.strptime(f'{y}/{m}/{d}/{hour_end}/{minute_end}', '%Y/%m/%d/%H/%M')
                            time_now = jdatetime.datetime.fromgregorian(datetime = datetime.datetime.fromtimestamp(update.message.date_code)) + timedelta(hours = 3, minutes = 30)
                            if hour_start > hour_end:
                                time_end += timedelta(days = 1)
                            if time_now >= time_start and time_now <= time_end:
                                update.message.delete_message()
                                cursor.execute(f'SELECT first_name, last_name, middle_name, id FROM student')
                                result = cursor.fetchall()
                                for user in result:
                                    if user[0] in update.message.author.first_name and user[1] in update.message.author.first_name and (user[2] is None or user[2] in update.message.author.first_name):
                                        val = (user[3], update.message.author.id, f'{date[0]}-{date[1]}-{date[2]}')
                                        cursor.execute('SELECT * FROM present WHERE id = ? AND user_id = ? AND date = ?', val)
                                        sql = ('INSERT INTO present(id, user_id, date) VALUES(?,?,?)')
                                        print("salam")
                                        
                                        result = cursor.fetchone()
                                        if result is None or result == []:
                                            cursor.execute(sql, val)
                                            db.commit()
                                            cursor.close()
                                            db.close()
                                            self.send_message(chat_id = update.message.chat_id, text = f'[{update.message.author.username}](https://ble.ir/@{update.message.author.username})\n*حضور شما تایید شد!✅*', reply_markup = {"keyboard": [[{"text":"شروع"}]]})
                                            return self.delete_message(chat_id = f'{update["callback_query"]["message"]["chat"]["id"]}', message_id = f'{update["callback_query"]["data"].split("|")[1]}')
                                        else:
                                            cursor.close()
                                            db.close()
                                            self.send_message(chat_id = update["callback_query"]["message"]["chat"]["id"], text = '* 📛حضور شما از قبل ثبت شده است.📛 *')
                                            return self.delete_message(chat_id = f'{update["callback_query"]["message"]["chat"]["id"]}', message_id = f'{update["callback_query"]["data"].split("|")[1]}')
                                cursor.close()
                                db.close()
                                self.send_message(chat_id = update["callback_query"]["message"]["chat"]["id"], text = f'* 📛نام شما  در دیتا بیس پیدا نشد، درصورتی که نام شما در اپلیکشن بله با نام واقعی شما مغایرت دارد لطفا اصلاح کرده و مجددا امتحان نمایید📛 *\nنام فعلی شما در بله : {update["callback_query"]["message"]["chat"]["first_name"]}')
                                return self.delete_message(chat_id = f'{update["callback_query"]["message"]["chat"]["id"]}', message_id = f'{update["callback_query"]["data"].split("|")[1]}')
                            else:
                                msg = self.send_message(chat_id = update["callback_query"]["message"]["chat"]["id"], text = f'📛کاربر گرامی شما فقط میتوانید در بین ساعت `{hour_start}:{minute_start}` تا `{hour_end}:{minute_end}` درخواست حضور خود را تائید کنید📛', reply_markup = {"keyboard": [[{"text":"شروع"}]]})
                                return self.delete_message(chat_id = f'{update["callback_query"]["message"]["chat"]["id"]}', message_id = f'{update["callback_query"]["data"].split("|")[1]}')
                        else:
                            cursor.close()
                            db.close()
                            self.delete_message(chat_id=update["callback_query"]["message"]["chat"]["id"],message_id=update["callback_query"]["message"]["message_id"])
                            return self.delete_message(chat_id = f'{update["callback_query"]["message"]["chat"]["id"]}', message_id = f'{update["callback_query"]["data"].split("|")[1]}')
                    except Exception as error:
                        print(error)
                else:
                    cursor.close()
                    db.close()
                    return self.send_message(chat_id = update.message.chat_id, text = f"❌ *وضعیت حضور و غیاب توسط ادمین غیر فعال شده است!* ❌", reply_markup = {"keyboard": [[{"text":"شروع"}]]})
        except Exception as error:
            self.check_error(update, context, error)
        
    def developers(self, update, context, bot):
        try:
            update.message.reply_message(text = '''*سلام، این بات توسط ```[گروه ایران]🔰گروه ایران توسط *کیان احمدیان* ساخته شده است.\n👇اعضای گروه:\n👤 - کیان احمدیان\n👤 -  علی و عرفان سلیمی\n👤 - امیر حسین دولابی\n👤 - امین شهرابی\n👤 - آریا آشوری``` ساخته شده است. *
* 🔰این بات به قصد استفاده برای بخش حضور و غیاب مدرسه علامه حلی4 ساخته شده است و * قصد دیگری در ساخت این بات نبوده است.
* 📛در صورتی که شخصی در بات اسپم کند بن خواهد شد و به استاد راهنمای دانش آموز هم اطلاع داده خواهد شد📛 *
* ⚠تمامی پیام های ارسالی هر کاربر در دیتا بیس بات ذخیره خواهد شد و در صورت لزوم از آن استفاده میشود⚠ *

* 😊در پایان امیدواریم از این بات لذت ببرید! *
با احترام فراوان - گروه ایران

'''+'\n\n\n[ارتباط با ما](https://mrpy.ir/bots/hozor-bot)', reply_markup = {"keyboard": [[{"text":"شروع"}]]})
        
        except Exception as error:
            self.check_error(update, context, error)

    def setting(self, update, context, bot):
        try:
            if update.message.author.is_bot_admin(return_msg_to_user = True):
                db = connect('./data.db')
                cursor = db.cursor()
                cursor.execute("SELECT * FROM setting")
                setting = cursor.fetchone()
                cursor.execute(f"SELECT name FROM admin WHERE user_id = '{update.message.author.id}'")
                (name, ) = cursor.fetchone()
                update.message.reply_message(text = f"""{name} *عزیز به تنظیمات بات خوش آمدید🔰* ،  شما میتوانید با استفاده تنظیمات زیر بات را کنترل نمایید 👇

⚙️ - امکان فعال یا غیر فعال کردن حضور و غیاب برای دانش آموزان : *{'فعال' if setting[2] else 'غیر فعال'}*
⚙️ - تعین زمان شروع حاضری زدن : *{setting[0]}*
⚙️ - تعیین زمان پایان حاضری زدن (و تا پنج دقیقه بعد از آن تاخیر حساب میشود) : *{setting[1]}*
""", reply_markup = { "inline_keyboard": [[{"text" : 'تعیین وضعیت حضوری توسط دانش آموزان', "callback_data" : 'condition_present'}, {"text" : 'تعیین زمان شروع حاضری زدن', "callback_data" : 'set_start_present_time'}, {"text": 'تعیین زمان پایان حاضری زدن', "callback_data": 'set_end_present_time'}]]})
        
        except Exception as error:
            self.check_error(update, context, error)
        
    def condition_present(self, update, context, bot, status = None):
        try:
            if status is not None:
                if self.wait_for.get(str(update.message.author.id)) == 'condition_present':
                    status = True if status == 'yes' else False
                    db = connect('./data.db')
                    cursor = db.cursor()
                    cursor.execute("SELECT condition_present FROM setting")
                    (status_c,) = cursor.fetchone()
                    if status_c == status:
                        del self.wait_for[str(update.message.author.id)]
                        self.send_message(chat_id = update.message.chat_id, text = f"❌ *این قسمت از قبل {'فعال' if status else 'غیر فعال'} بوده است!* ❌", reply_markup = {"keyboard": [[{"text":"شروع"}]]})
                        return self.setting(update, context, bot)
                    else:
                        sql = (f"UPDATE setting SET condition_present = {status}")
                        cursor.execute(sql)
                        db.commit()
                        cursor.close()
                        db.close()
                    
                        del self.wait_for[str(update.message.author.id)]
                        self.send_message(chat_id = update.message.chat_id, text = f"✅ *حاضری زدن توسط دانش آموزان با موفقیت {'فعال' if status else 'غیر فعال'} شد* ✅", reply_markup = {"keyboard": [[{"text":"شروع"}]]})
                        return self.setting(update, context, bot)
                else:
                    self.start(update, context, bot)
            else:
                update.message.reply_message(text = f"""*لطفا با استفاده از بخش های زیر وضعیت حاضری زدن را تعیین کنید👇*""", reply_markup = { "inline_keyboard": [[{"text": "فعال شود", "callback_data": "condition_present_yes"}, {"text": "غیر فعال شود", "callback_data": "condition_present_no"}], [{"text": "لغو", "callback_data": "cancel"}]]})
                self.wait_for[str(update.message.author.id)] = 'condition_present'
        except Exception as error:
            self.check_error(update, context, error)
        
    def set_start_present_time(self, update, context, bot, status = None):
        try:
            if status is not None:
                if self.wait_for.get(str(update.message.author.id)) == 'set_start_present_time':
                    if ':' in str(status):
                        try:
                            hour = int(str(status).split(':')[0])
                            minute = int(str(status).split(':')[1])
                            if hour <= 24 and minute >= 0 and hour <= 60 and hour >= 1:
                                db = connect('./data.db')
                                cursor = db.cursor()
                                sql = (f"UPDATE setting SET start_present_time = '{int(str(status).split(':')[0])}:{int(str(status).split(':')[1])}' ")
                                cursor.execute(sql)
                                db.commit()
                                cursor.close()
                                db.close()
                                del self.wait_for[str(update.message.author.id)]
                                update.message.reply_message(text = f"✅ *زمان شروع حاضری زدن توسط دانش آموزان با موفقیت تغییر کرد* ✅", reply_markup = {"keyboard": [[{"text":"شروع"}]]})
                                return self.setting(update, context, bot)
                            else:
                                del self.wait_for[str(update.message.author.id)]
                                update.message.reply_message(text = '*📛مقدار به اشتباه وارد شده است!\nعملیات لغو شد لطفا مجدد امتحان کنید!📛*')  
                                return self.setting(update, context, bot)
                        except:
                            del self.wait_for[str(update.message.author.id)]
                            update.message.reply_message(text = '*📛مقدار به اشتباه وارد شده است!\nعملیات لغو شد لطفا مجدد امتحان کنید!📛*') 
                            return self.setting(update, context, bot)
                    else:
                        del self.wait_for[str(update.message.author.id)]
                        update.message.reply_message(text = '*📛مقدار به اشتباه وارد شده است!\nعملیات لغو شد لطفا مجدد امتحان کنید!📛*')  
                        return self.setting(update, context, bot)
                else:
                    self.start(update, context, bot)
            else:
                update.message.reply_message(text = f"""*لطفا زمان حاضری زدن را در پیام بعدی خود وارد نمایید👇*
مثال:
`7:30`""", reply_markup = { "inline_keyboard": [[{"text": "لغو", "callback_data": "cancel"}]]})
                self.wait_for[str(update.message.author.id)] = 'set_start_present_time'
        except Exception as error:
            self.check_error(update, context, error)

    def set_end_present_time(self, update, context, bot, status = None):
        try:
            if status is not None:
                if self.wait_for.get(str(update.message.author.id)) == 'set_end_present_time':
                    if ':' in str(status):
                        try:
                            hour = int(str(status).split(':')[0])
                            minute = int(str(status).split(':')[1])
                            if hour <= 24 and minute >= 0 and hour <= 60 and hour >= 1:
                                db = connect('./data.db')
                                cursor = db.cursor()
                                sql = (f"UPDATE setting SET end_present_time = '{int(str(status).split(':')[0])}:{int(str(status).split(':')[1])}' ")
                                cursor.execute(sql)
                                db.commit()
                                cursor.close()
                                db.close()
                                del self.wait_for[str(update.message.author.id)]
                                update.message.reply_message(text = f"✅ *زمان پایان حاضری زدن توسط دانش آموزان با موفقیت تغییر کرد* ✅", reply_markup = {"keyboard": [[{"text":"شروع"}]]})
                                return self.setting(update, context, bot)
                            else:
                                del self.wait_for[str(update.message.author.id)]
                                update.message.reply_message(text = '*📛مقدار به اشتباه وارد شده است!\nعملیات لغو شد لطفا مجدد امتحان کنید!📛*')  
                                return self.setting(update, context, bot)
                        except:
                            del self.wait_for[str(update.message.author.id)]
                            update.message.reply_message(text = '*📛مقدار به اشتباه وارد شده است!\nعملیات لغو شد لطفا مجدد امتحان کنید!📛*') 
                            return self.setting(update, context, bot)
                    else:
                        del self.wait_for[str(update.message.author.id)]
                        update.message.reply_message(text = '*📛مقدار به اشتباه وارد شده است!\nعملیات لغو شد لطفا مجدد امتحان کنید!📛*')  
                        return self.setting(update, context, bot)
                else:
                    self.start(update, context, bot)
            else:
                update.message.reply_message(text = f"""*لطفا زمان حاضری زدن را در پیام بعدی خود وارد نمایید👇*
مثال:
`7:30`""", reply_markup = { "inline_keyboard": [[{"text": "لغو", "callback_data": "cancel"}]]})
                self.wait_for[str(update.message.author.id)] = 'set_end_present_time'
        except Exception as error:
            self.check_error(update, context, error)
    
    def send_msg(self, user_id, text):
        return post(f"{self.base_url}bot{self.token}/sendMessage", json = {
            "chat_id": f"{user_id}",
            "text": f"{text}"
        })        
    

    
if __name__ == '__main__':
    print('App is Started!\nPlease Press "Enter" for Start Bot!\nMade By: IRAN TEAM')
    wait('enter')
    BaleApp(token = "1705600104:blTu9Ti8GK4Lv6rLvpnegORBTVpgYgbdPFa21WlY", base_url = "https://tapi.bale.ai/", base_file_url = 'https://tapi.bale.ai/file')
