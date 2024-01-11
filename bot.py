from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient

# Replace 'YOUR_API_ID' and 'YOUR_API_HASH' with your Telegram API credentials.
api_id = '4783634'
api_hash = 'f6c33f46599246676f75e153b615dbbc'
bot_token = '6729277794:AAEUsO6oPaecOvmpCQJXEU-MqBNmgaOsVgA'

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Replace 'your_mongo_uri' with your MongoDB URI.
mongo_uri = 'mongodb+srv://Complex:Complex@cluster0.e6wgtmq.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(mongo_uri)
db = client['user_db']
user_collection = db['users']

# Custom filter to check if the user is authorized
async def is_authorized_user(_, __, message: Message):
    if message.from_user:
        user_id = message.from_user.id
        user_data = user_collection.find_one({})
    
        return user_data and 'user_ids' in user_data and user_id in user_data['user_ids']

    return False 

# Command to add user IDs to the database
@app.on_message(filters.command("adduser") & filters.private)
def add_user_to_db(client, message):
    user_ids_to_add = message.text.split()[1:]  # Extract user IDs from the command
    user_ids_to_add = [int(user_id) for user_id in user_ids_to_add if user_id.isdigit()]  # Ensure they are integers

    if not user_ids_to_add:
        message.reply_text("Invalid user IDs provided.")
        return

    user_data = user_collection.find_one({})
    existing_user_ids = user_data.get('user_ids', []) if user_data else []

    # Separate user IDs into already added and not added
    already_added_ids = [user_id for user_id in user_ids_to_add if user_id in existing_user_ids]
    new_user_ids = [user_id for user_id in user_ids_to_add if user_id not in existing_user_ids]

    # Add new user IDs to the database
    if new_user_ids:
        user_collection.update_one({}, {'$addToSet': {'user_ids': {'$each': new_user_ids}}})
        message.reply_text(f"Added {len(new_user_ids)} new user(s) to the database.")

    # Reply with already added user IDs
    if already_added_ids:
        message.reply_text(f"User IDs {', '.join(map(str, already_added_ids))} already added and ignored.")

    # Reply with the whole list of users finally added to the database
    final_user_list = user_collection.find_one({})['user_ids']
    message.reply_text(f"Final list of user IDs in the database: {', '.join(map(str, final_user_list))}")

# Command to check if the user is authorized and reply with "I am alive"
@app.on_message(filters.create(is_authorized_user) & filters.command("start") & filters.private)
def start_command(client, message):
    message.reply_text("I am alive!")

app.run()
