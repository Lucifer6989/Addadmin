from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient

# Replace 'YOUR_API_ID' and 'YOUR_API_HASH' with your Telegram API credentials.
api_id = '16844842'
api_hash = 'f6b0ceec5535804be7a56ac71d08a5d4"'
bot_token = '6729277794:AAEUsO6oPaecOvmpCQJXEU-MqBNmgaOsVgA'

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Replace 'your_mongo_uri' with your MongoDB URI.
mongo_uri = 'mongodb+srv://Complex:Complex@cluster0.e6wgtmq.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(mongo_uri)
db = client['user_db']
user_collection = db['users']

# Custom filter to check if the user is authorized
async def is_authorized_user(_, __, message: Message):
    user_id = message.from_user.id
    user_data = user_collection.find_one({})
    
    return user_data and 'user_ids' in user_data and user_id in user_data['user_ids']

# Command to add user IDs to the database
@app.on_message(filters.command("adduser") & filters.private)
def add_user_to_db(client, message):
    user_ids = message.text.split()[1:] #Extract user IDs from the command
    user_ids = [int(user_id) for user_id in user_ids if user_id.isdigit()] # Ensure they are integers
    
    if user_ids: # Insert user IDs into the database
        user_collection.update_one({}, {'$addToSet': {'user_ids': {'$each': user_ids}}}, upsert=True)
        message.reply_text(f"User IDs {user_ids} added to the database.")
    else:
        message.reply_text("Invalid user IDs provided.")

# Command to check if the user is authorized and reply with "I am alive"
@app.on_message(is_authorized_user & filters.command("start") & filters.private)
def start_command(client, message):
    message.reply_text("I am alive!")

app.run()
