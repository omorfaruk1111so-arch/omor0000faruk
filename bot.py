import telebot										
import requests										
import time										
import random										
import string										
import threading										
import re										
import os										
import pandas as pd										
from flask import Flask										
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton										
										
# Bot Configuration (Updated)										
TOKEN = '8604465538:AAGIO9hgU0pgcVaSxywmdILVFER6X1ZxH-Q'										
CHANNEL_USERNAME = https://t.me/newbulkaccountsell										
ADMIN_ID = 7444321226  # নতুন এডমিন আইডি										
bot = telebot.TeleBot(TOKEN)										
										
# BulkMail.shop API Configuration										
BULKMAIL_API_KEY = 'Sk_live_745f7e42059431dc0a40fa60f5d1d482dee83bf5c267c142cbdbe9bf468dd732'										
BULKMAIL_BASE_URL = 'https://bulkmail.shop/api/v1'										
										
# In-memory Database										
users = {}										
active_mails = {}										
blocked_users = set()										
user_hotmail_tokens = {}										
waiting_for_hotmail_token = set()										
										
def get_session():										
session = requests.Session()										
adapter = requests.adapters.HTTPAdapter(max_retries=5)										
session.mount('https://', adapter)										
return session										
										
session = get_session()										
										
def is_subscribed(user_id):										
try:										
member = bot.get_chat_member(CHANNEL_USERNAME, user_id)										
return member.status in ['creator', 'administrator', 'member']										
except Exception:										
return False										
										
def main_keyboard(user_id):										
markup = ReplyKeyboardMarkup(resize_keyboard=True)										
"markup.row(KeyboardButton(""📧 Gen Mail""), KeyboardButton(""📩 Check OTP""))"										
"markup.row(KeyboardButton(""➕ Add Hotmail Token""), KeyboardButton(""🛑 Stop Mail""))"										
"markup.row(KeyboardButton(""💰 Balance""), KeyboardButton(""👥 Referral""))"										
"markup.row(KeyboardButton(""💳 Withdraw""))"										
										
if user_id == ADMIN_ID:										
"markup.row(KeyboardButton(""🛡️ Admin Panel""))"										
										
return markup										
										
def check_join_keyboard():										
markup = InlineKeyboardMarkup()										
"markup.add(InlineKeyboardButton(""📢 Join Channel"", url=f""https://t.me/{CHANNEL_USERNAME.replace('@', '')}""))"										
"markup.add(InlineKeyboardButton(""✅ Verify Subscription"", callback_data=""check_subscription""))"										
return markup										
										
@bot.message_handler(commands=['start'])										
def start(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
"bot.send_message(user_id, ""❌ আপনাকে এই বট থেকে ব্লক করা হয়েছে!"")"										
return										
										
args = message.text.split()										
										
if user_id not in users:										
users[user_id] = {'balance': 0.0, 'referrals': 0, 'referred_by': None}										
if len(args) > 1 and args[1].isdigit():										
referrer_id = int(args[1])										
if referrer_id != user_id and referrer_id in users:										
users[user_id]['referred_by'] = referrer_id										
users[referrer_id]['balance'] += 1000.0										
users[referrer_id]['referrals'] += 1										
try:										
"bot.send_message(referrer_id, f""🎉 New Referral! You earned <b>$1000</b>!"", parse_mode=""HTML"")"										
except:										
pass										
										
if not is_subscribed(user_id):										
"bot.send_message(user_id, f""⚠️ You must join {CHANNEL_USERNAME} to use this bot!"", reply_markup=check_join_keyboard())"										
return										
										
"bot.send_message(user_id, ""✨ Welcome to Temp Mail Bot! Select an option below:"", reply_markup=main_keyboard(user_id))"										
										
"@bot.callback_query_handler(func=lambda call: call.data == ""check_subscription"")"										
def verify_sub(call):										
user_id = call.from_user.id										
if is_subscribed(user_id):										
"bot.answer_callback_query(call.id, ""✅ Verified!"")"										
"bot.send_message(user_id, ""✨ Welcome! Select an option below:"", reply_markup=main_keyboard(user_id))"										
else:										
"bot.answer_callback_query(call.id, ""❌ You haven't joined yet!"", show_alert=True)"										
										
"@bot.callback_query_handler(func=lambda call: call.data.startswith((""block_"", ""unblock_"")))"										
def handle_block_callback(call):										
if call.from_user.id != ADMIN_ID:										
return										
										
"action, target_id_str = call.data.split(""_"")"										
target_id = int(target_id_str)										
										
"if action == ""block"":"										
blocked_users.add(target_id)										
"bot.answer_callback_query(call.id, f""✅ User {target_id} Blocked!"")"										
"bot.send_message(call.message.chat.id, f""🚫 <b>User <code>{target_id}</code> has been blocked!</b>"", parse_mode=""HTML"")"										
"elif action == ""unblock"":"										
if target_id in blocked_users:										
blocked_users.remove(target_id)										
"bot.answer_callback_query(call.id, f""✅ User {target_id} Unblocked!"")"										
"bot.send_message(call.message.chat.id, f""✅ <b>User <code>{target_id}</code> has been unblocked!</b>"", parse_mode=""HTML"")"										
										
"@bot.message_handler(func=lambda m: m.text == ""🛡️ Admin Panel"")"										
def admin_panel(message):										
user_id = message.from_user.id										
if user_id != ADMIN_ID:										
return										
										
admin_markup = ReplyKeyboardMarkup(resize_keyboard=True)										
"admin_markup.row(KeyboardButton(""👥 Total Users""), KeyboardButton(""🔙 Main Menu""))"										
"bot.send_message(user_id, ""🛡️ <b>Welcome to Admin Panel</b>\n\nChoose an option below or use commands:\n👉 <code>/block UID</code> - Block a user\n👉 <code>/unblock UID</code> - Unblock a user"", reply_markup=admin_markup, parse_mode=""HTML"")"										
										
"@bot.message_handler(func=lambda m: m.text == ""🔙 Main Menu"")"										
def main_menu(message):										
user_id = message.from_user.id										
if user_id in waiting_for_hotmail_token:										
waiting_for_hotmail_token.remove(user_id)										
"bot.send_message(user_id, ""🏠 Returned to Main Menu:"", reply_markup=main_keyboard(user_id))"										
										
"@bot.message_handler(func=lambda m: m.text == ""➕ Add Hotmail Token"")"										
def add_hotmail_token_prompt(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
"bot.send_message(user_id, ""❌ আপনাকে এই বট থেকে ব্লক করা হয়েছে!"")"										
return										
waiting_for_hotmail_token.add(user_id)										
"bot.send_message(user_id, ""🔑 অনুগ্রহ করে আপনার নিজস্ব Hotmail Token গুলো পাঠান (প্রতি লাইনে একটি করে অথবা এক্সেল ফাইল আপলোড করুন):"", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton(""🔙 Main Menu"")))"										
										
@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_hotmail_token)										
def save_user_hotmail_token(message):										
user_id = message.from_user.id										
"if message.text == ""🔙 Main Menu"":"										
waiting_for_hotmail_token.remove(user_id)										
"bot.send_message(user_id, ""🏠 Main Menu:"", reply_markup=main_keyboard(user_id))"										
return										
										
tokens = [t.strip() for t in message.text.split('\n') if t.strip()]										
if tokens:										
if user_id not in user_hotmail_tokens:										
user_hotmail_tokens[user_id] = []										
user_hotmail_tokens[user_id].extend(tokens)										
waiting_for_hotmail_token.remove(user_id)										
"bot.send_message(user_id, f""✅ আপনার ব্যক্তিগত অ্যাকাউন্টে সফলভাবে <b>{len(tokens)}টি</b> Hotmail Token যুক্ত করা হয়েছে!\n📊 আপনার অবশিষ্ট মোট টোকেন: <b>{len(user_hotmail_tokens[user_id])}টি</b>"", parse_mode=""HTML"", reply_markup=main_keyboard(user_id))"										
else:										
"bot.send_message(user_id, ""⚠️ কোনো টোকেন পাওয়া যায়নি। দয়া করে সঠিক টোকেন পাঠান।"")"										
										
@bot.message_handler(content_types=['document'])										
def handle_excel_token_file(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
return										
										
document = message.document										
if not document.file_name.endswith(('.xlsx', '.xls')):										
"bot.send_message(user_id, ""⚠️ দয়া করে একটি সঠিক Excel (.xlsx বা .xls) ফাইল পাঠান।"")"										
return										
										
try:										
file_info = bot.get_file(document.file_id)										
downloaded_file = bot.download_file(file_info.file_path)										
										
"file_path = f""temp_{user_id}_{document.file_name}"""										
with open(file_path, 'wb') as f:										
f.write(downloaded_file)										
										
xls = pd.ExcelFile(file_path)										
df = pd.read_excel(xls, sheet_name=0)										
										
extracted_tokens = []										
for col in df.columns:										
for val in df[col].dropna():										
val_str = str(val).strip()										
if not val_str:										
continue										
extracted_tokens.append(val_str)										
										
if extracted_tokens:										
if user_id not in user_hotmail_tokens:										
user_hotmail_tokens[user_id] = []										
user_hotmail_tokens[user_id].extend(extracted_tokens)										
if user_id in waiting_for_hotmail_token:										
waiting_for_hotmail_token.remove(user_id)										
"bot.send_message(user_id, f""✅ এক্সেল ফাইল থেকে আপনার জন্য সফলভাবে <b>{len(extracted_tokens)}টি</b> টোকেন যুক্ত করা হয়েছে!\n📊 আপনার মোট টোকেন: <b>{len(user_hotmail_tokens[user_id])}টি</b>"", parse_mode=""HTML"", reply_markup=main_keyboard(user_id))"										
else:										
"bot.send_message(user_id, ""⚠️ ফাইলে কোনো বৈধ টোকেন পাওয়া যায়নি!"")"										
										
os.remove(file_path)										
except Exception as e:										
"bot.send_message(user_id, f""❌ ফাইল পড়তে সমস্যা হয়েছে: {str(e)}"")"										
										
"@bot.message_handler(func=lambda m: m.text == ""👥 Total Users"")"										
def admin_total_users(message):										
user_id = message.from_user.id										
if user_id != ADMIN_ID:										
return										
										
if not users:										
"bot.send_message(user_id, ""📭 বটে এখনো কোনো ইউজার নেই!"")"										
return										
										
total_users = len(users)										
"bot.send_message(user_id, f""👥 <b>Total Users: {total_users}</b>"", parse_mode=""HTML"")"										
										
for uid, data in users.items():										
try:										
chat_info = bot.get_chat(uid)										
"name = chat_info.first_name if chat_info.first_name else ""No Name"""										
"username = f""@{chat_info.username}"" if chat_info.username else ""No Username"""										
except:										
"name = ""Unknown"""										
"username = ""N/A"""										
										
balance = data.get('balance', 0.0)										
"status = ""🔴 Blocked"" if uid in blocked_users else ""🟢 Active"""										
										
"info_text = f""👤 <b>Name:</b> {name}\n🆔 <b>UID:</b> <code>{uid}</code>\n🔗 <b>Username:</b> {username}\n💰 <b>Balance:</b> ${balance:.2f}\n📌 <b>Status:</b> {status}"""										
										
markup = InlineKeyboardMarkup()										
if uid != ADMIN_ID:										
if uid in blocked_users:										
"markup.add(InlineKeyboardButton(""✅ Unblock User"", callback_data=f""unblock_{uid}""))"										
else:										
"markup.add(InlineKeyboardButton(""🚫 Block User"", callback_data=f""block_{uid}""))"										
										
"bot.send_message(user_id, info_text, reply_markup=markup, parse_mode=""HTML"")"										
										
@bot.message_handler(commands=['block'])										
def block_user_cmd(message):										
if message.from_user.id != ADMIN_ID:										
return										
args = message.text.split()										
if len(args) > 1 and args[1].isdigit():										
target_id = int(args[1])										
blocked_users.add(target_id)										
"bot.send_message(message.chat.id, f""✅ ইউজার আইডি <code>{target_id}</code> সফলভাবে ব্লক করা হয়েছে।"", parse_mode=""HTML"")"										
else:										
"bot.send_message(message.chat.id, ""⚠️ সঠিক নিয়মে লিখুন। যেমন: <code>/block 123456789</code>"", parse_mode=""HTML"")"										
										
@bot.message_handler(commands=['unblock'])										
def unblock_user_cmd(message):										
if message.from_user.id != ADMIN_ID:										
return										
args = message.text.split()										
if len(args) > 1 and args[1].isdigit():										
target_id = int(args[1])										
if target_id in blocked_users:										
blocked_users.remove(target_id)										
"bot.send_message(message.chat.id, f""✅ ইউজার আইডি <code>{target_id}</code> আনব্লক করা হয়েছে।"", parse_mode=""HTML"")"										
else:										
"bot.send_message(message.chat.id, ""⚠️ এই ইউজারটি ব্লক লিস্টে নেই।"")"										
										
@bot.message_handler(commands=['users'])										
def users_cmd(message):										
admin_total_users(message)										
										
"@bot.message_handler(func=lambda m: m.text == ""📧 Gen Mail"")"										
def gen_mail(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
"bot.send_message(user_id, ""❌ আপনাকে এই বট থেকে ব্লক করা হয়েছে!"")"										
return										
if user_id not in users:										
users[user_id] = {'balance': 0.0, 'referrals': 0, 'referred_by': None}										
										
if not is_subscribed(user_id):										
"bot.send_message(user_id, f""⚠️ Please join {CHANNEL_USERNAME} first!"", reply_markup=check_join_keyboard())"										
return										
										
if user_id in active_mails:										
existing = active_mails[user_id]										
"bot.send_message(user_id, f""⚠️ আপনার ইতিমধ্যে একটি সচল ইমেইল রয়েছে:\n\n<code>{existing['email']}</code>\n\nনতুন মেইল নিতে চাইলে আগে 🛑 Stop Mail এ ক্লিক করুন।"", parse_mode=""HTML"")"										
return										
										
if user_id in user_hotmail_tokens and user_hotmail_tokens[user_id]:										
full_line = user_hotmail_tokens[user_id].pop(0)										
"email = f""outlook_{random.randint(10000,99999)}@outlook.com"""										
token = full_line										
										
if '|' in full_line:										
parts = full_line.split('|')										
if '@' in parts[0]:										
email = parts[0].strip()										
for p in parts:										
p = p.strip()										
if p.startswith('M.') or len(p) > 20:										
token = p										
break										
										
active_mails[user_id] = {'email': email, 'token': token, 'type': 'hotmail', 'last_msg_id': None}										
remaining_count = len(user_hotmail_tokens[user_id])										
										
bot.send_message(										
user_id,										
"f""✅ <b>Your Private Hotmail/Outlook Email:</b>\n\n<code>{email}</code>\n\n📊 আপনার আরও অবশিষ্ট টোকেন আছে: <b>{remaining_count}টি</b>"","										
"parse_mode=""HTML"""										
)										
return										
										
"bot.send_message(user_id, ""⚠️ আপনার কোনো Hotmail টোকেন বাকি নেই! দয়া করে <b>➕ Add Hotmail Token</b> এ ক্লিক করে আরও টোকেন বা এক্সেল ফাইল যুক্ত করুন।"", parse_mode=""HTML"")"										
										
"@bot.message_handler(func=lambda m: m.text == ""🛑 Stop Mail"")"										
def stop_mail(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
"bot.send_message(user_id, ""❌ আপনাকে এই বট থেকে ব্লক করা হয়েছে!"")"										
return										
										
if user_id in active_mails:										
del active_mails[user_id]										
"bot.send_message(user_id, ""🛑 আপনার চলমান ইমেইল সেশন সফলভাবে বন্ধ করা হয়েছে!"", reply_markup=main_keyboard(user_id))"										
else:										
"bot.send_message(user_id, ""⚠️ আপনার কোনো চলমান ইমেইল সেশন নেই!"", reply_markup=main_keyboard(user_id))"										
										
"@bot.message_handler(func=lambda m: m.text == ""📩 Check OTP"")"										
def check_otp(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
"bot.send_message(user_id, ""❌ আপনাকে এই বট থেকে ব্লক করা হয়েছে!"")"										
return										
if user_id not in users:										
users[user_id] = {'balance': 0.0, 'referrals': 0, 'referred_by': None}										
										
if user_id not in active_mails or 'token' not in active_mails[user_id]:										
"bot.send_message(user_id, ""⚠️ আগে একটি নতুন মেইল জেনারেট করুন!"")"										
return										
										
mail_info = active_mails[user_id]										
token = mail_info['token']										
email = mail_info['email']										
										
headers = {										
"Authorization: f""Bearer {BULKMAIL_API_KEY}"","										
"Content-Type: ""application/json"""										
}										
										
try:										
"response = session.get(f""{BULKMAIL_BASE_URL}/messages?email={email}"", headers=headers, timeout=10)"										
										
if response.status_code == 200:										
data = response.json()										
messages = data.get('messages', []) or data.get('data', [])										
										
if messages:										
latest_msg = messages[0]										
body = latest_msg.get('body', '') or latest_msg.get('text', '') or latest_msg.get('content', '')										
										
codes = re.findall(r'\b\d{4,6}\b', body)										
"otp_code = codes[0] if codes else ""No OTP found"""										
										
bot.send_message(										
user_id,										
"f""📩 <b>OTP Code Received via API!</b>\n\n📧 Email: <code>{email}</code>\n🔢 Code: <code>{otp_code}</code>"","										
"parse_mode=""HTML"""										
)										
else:										
"bot.send_message(user_id, f""📩 <b>Active Hotmail:</b> <code>{email}</code>\n\n⌛ ইনবক্সে এখনো কোনো নতুন মেসেজ আসেনি!"", parse_mode=""HTML"")"										
else:										
"graph_headers = {""Authorization"": f""Bearer {token}""}"										
"graph_res = session.get(""https://graph.microsoft.com/v1.0/me/messages?$select=subject,body,receivedDateTime&$top=1"", headers=graph_headers, timeout=10)"										
										
if graph_res.status_code == 200:										
msgs = graph_res.json().get('value', [])										
if msgs:										
body = msgs[0].get('body', {}).get('content', '')										
codes = re.findall(r'\b\d{4,6}\b', body)										
"otp_code = codes[0] if codes else ""No OTP found"""										
"bot.send_message(user_id, f""📩 <b>OTP Code Received!</b>\n\n📧 Email: <code>{email}</code>\n🔢 Code: <code>{otp_code}</code>"", parse_mode=""HTML"")"										
else:										
"bot.send_message(user_id, f""📩 <b>Active Hotmail:</b> <code>{email}</code>\n\n⌛ ইনবক্স ফাঁকা রয়েছে।"", parse_mode=""HTML"")"										
else:										
"bot.send_message(user_id, f""📩 <b>Active Hotmail:</b> <code>{email}</code>\n\n⚠️ ইনবক্স থেকে মেসেজ রিড করা যায়নি (টোকেন বা API রেসপন্স চেক করুন)।"", parse_mode=""HTML"")"										
except Exception as e:										
"bot.send_message(user_id, f""📩 <b>Active Hotmail:</b> <code>{email}</code>\n\n❌ ত্রুটি: ইনবক্স চেক করতে সমস্যা হয়েছে।"", parse_mode=""HTML"")"										
										
"@bot.message_handler(func=lambda m: m.text == ""💰 Balance"")"										
def balance(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
"bot.send_message(user_id, ""❌ আপনাকে এই বট থেকে ব্লক করা হয়েছে!"")"										
return										
if user_id not in users:										
users[user_id] = {'balance': 0.0, 'referrals': 0, 'referred_by': None}										
										
user_data = users[user_id]										
"bot.send_message(user_id, f""👤 <b>Your Account Info</b>\n\n💰 Balance: <b>${user_data['balance']:.2f}</b>\n👥 Total Referrals: <b>{user_data['referrals']}</b>"", parse_mode=""HTML"")"										
										
"@bot.message_handler(func=lambda m: m.text == ""👥 Referral"")"										
def referral(message):										
user_id = message.from_user.id										
if user_id in blocked_users:										
"bot.send_message(user_id, ""❌ আপনাকে এই বট থেকে ব্লক করা হয়েছে!"")"										
return										
bot_username = bot.get_me().username										
"ref_link = f""https://t.me/{bot_username}?start={user_id}"""										
"bot.send_message(user_id, f""🔗 <b>Your Referral Link:</b>\n\n<code>{ref_link}</code>"", parse_mode=""HTML"")"										
										
"@bot.message_handler(func=lambda m: m.text == ""💳 Withdraw"")"										
def withdraw(message):										
user_id = message.from_user.id
