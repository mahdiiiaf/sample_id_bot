from telegram import Update, KeyboardButton, ReplyKeyboardMarkup , KeyboardButtonRequestUser
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3 , os
from dotenv import load_dotenv


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button to request a saved contact."""
    user = update.message.from_user
    button = [[KeyboardButton("اشتراک دوستات", 
        request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False, user_is_premium=False)),
        # KeyboardButtonRequestUser('sdfdsf'),
        KeyboardButton("اشتراک شماره خودتان",  request_contact=True) ,
    ]]
    # print(f'{user = }')
    reply_markup = ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
    connection = sqlite3.connect('IdDataBase.db')
    connection.execute(f'''
            INSERT INTO IDS ( TELEGRAM_ID , USERNAME , NAME , FAMILY_NAME )
                VALUES ( {user.id} , '{user.username if user.username else ''}' , 
                    '{user.first_name if user.first_name else ''}' , '{user.last_name if user.last_name else ''}'    )
                ON CONFLICT(TELEGRAM_ID) DO NOTHING 
        ''')
    connection.commit()
    connection.close()
    await update.message.reply_text(
        # text="برای گرفتن ایدی یکی از گزینه‌های زیر را انتخاب نمایید\n\nٰVandM Bot",
        text         = f'Id: `{update.message.from_user.id}`\nVandM Company' ,
        reply_markup = reply_markup ,
        parse_mode   = 'MarkDownV2'
    )

# Handler for receiving contact information
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the contact information sent by the user."""
    contact = update.message.contact
    if not ( update.message.contact or  update.message.user_shared ) : return 0
    # {'users_shared': {'user_ids': [7431256270], 'users': [{'user_id': 7431256270}], 'request_id': 1}}, channel_chat_created=False, chat=Chat(first_name='Mahdi', id=6702317393, type=<ChatType.PRIVATE>, username='mahdiiiaf'), date=datetime.datetime(2025, 1, 8, 4, 18, 59, tzinfo=<UTC>), delete_chat_photo=False, from_user=User(first_name='Mahdi', id=6702317393, is_bot=False, language_code='en', username='mahdiiiaf'), group_chat_created=False, message_id=43, supergroup_chat_created=False, user_shared=UserShared(request_id=1, user_id=7431256270))
    # print(f'{update.message.user_shared.user_id = }')
    if contact:
        contact_info = (
            # f"Contact shared!\n"
            f'Id: `{update.message.from_user.id}`\nVandM Company'
            # f"Name: {contact.first_name} {contact.last_name or ''}\n"
            # f"Phone: {contact.phone_number}"
        )
        await update.message.reply_text(
                text       = contact_info ,
                parse_mode = 'MarkDownV2'
            )
        connection = sqlite3.connect('IdDataBase.db')
        connection.execute(f'''
                UPDATE IDS SET TELEGRAM_ID = {update.message.from_user.id} , USERNAME = '{update.message.from_user.username}' , 
                        NAME = '{contact.first_name}' , FAMILY_NAME = '{contact.last_name }' ,
                        PHONE_NUMBER = '{contact.phone_number}'
                    WHERE TELEGRAM_ID = {update.message.from_user.id}
            ''')
        connection.commit()
        connection.close()
    else:
        await update.message.reply_text(
                text       = f"Id: `{update.message.user_shared.user_id}`\nVandM Company" ,
                parse_mode = 'MarkDownV2'
            )
        connection = sqlite3.connect('IdDataBase.db')
        connection.execute(f'''
                INSERT INTO IDS ( TELEGRAM_ID )
                    VALUES ( {update.message.user_shared.user_id} )
                    ON CONFLICT(TELEGRAM_ID) DO NOTHING 
            ''')
        connection.commit()
        connection.close()

# Main function to start the bot
def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_TOKEN_HERE' with your bot token
    application = ApplicationBuilder().token(TOKEN).build()

    # Command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    application.add_handler(MessageHandler(~ filters.COMMAND, contact_handler))
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    load_dotenv('key.env')
    TOKEN    = os.getenv('TOKEN')
    USERNAME = os.getenv('USERNAME')
    main()
