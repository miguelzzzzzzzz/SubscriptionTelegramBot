from typing import Final
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import json
import datetime
from tabulate import tabulate
from nextdnsapi.api import *

header = account.login("ezekielbruno96@icloud.com", "Bosshate1996X")

df = pd.read_csv('subss.csv')
json_data = df.to_json()
dict_data = json.loads(json_data)
table = tabulate(df, headers='keys', tablefmt='psql')

print(datetime.datetime.now())

TOKEN: Final = '7185691826:AAHT-v_7ijKGI2JsY6XyDcIveM0SEQUhDmg'
BOT_USERNAME: Final = '@countdownerrbot'
async def get_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Wait for a new update from the user
    new_update = await context.bot.get_updates()

    # Retrieve the text of the new update
    message = new_update[-1].message
    return message.text

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    df = pd.read_csv('subss.csv')

    # Format the DataFrame as a list of strings
    items = []
    for index, row in df.iterrows():
        # Check if the item is expired
        sub_ex = row['subEx']
        if sub_ex != 'indefinite':
            sub_ex = datetime.datetime.strptime(sub_ex, '%Y-%m-%d')
            if datetime.datetime.now() > sub_ex:
                status = 'Expired'
                validity = 'Expired'
                key = row['key']

            else:
                status = 'Active'
                validity = sub_ex - datetime.datetime.now()
                validity = f"{validity.days} days, {validity.seconds // 3600} hours"
        else:
            status = 'Active'
            validity = 'Indefinite'

        item = f"DNS {index}\nName: {row['Name']}\nStart Date: {row['subStart']}\nProfile Status: {row['subStat']}\nExpiration Date: {row['subEx']}\nStatus: {status}\nValidity: {validity}\n"
        items.append(item)
    # Join the list of strings into a single string
    output = '\n'.join(items)

    # Delete the previous message sent by the bot, if it exists
    if 'previous_message' in context.chat_data:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.chat_data['previous_message'])
        except telegram.error.BadRequest:
            pass

    # Send the new message
    message = await update.message.reply_text(output)

    # Store the message ID of the new message
    context.chat_data['previous_message'] = message.message_id
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except telegram.error.BadRequest:
        pass



def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'hello puking inamo'
    elif 'add_item' in processed:
        # Extract the item attributes from the input string
        attributes = processed.split('add_item')[1].strip().split(',')

        # Check that the input string contains the correct number of attributes
        if len(attributes) != 4:
            return "Invalid input. Please enter the item attributes as a single string, separated by commas:\nName, Subscription Start Date (YYYY-MM-DD), Subscription Status, Key"

        # Extract the attributes from the list
        name = attributes[0].strip()
        sub_start = datetime.datetime.strptime(attributes[1].strip(), '%Y-%m-%d')
        sub_stat = attributes[2].strip()
        key = attributes[3].strip()

        # Calculate the subscription expiration date based on the subscription status
        if sub_stat == 'free':
            sub_ex = sub_start + datetime.timedelta(days=15)
        elif sub_stat == 'paid':
            sub_ex = 'indefinite'
        else:
            return "Invalid subscription status. Please enter 'free' or 'paid'."

        # Append a new row to the DataFrame with the extracted attributes
        new_item = pd.DataFrame(
            {'Name': [name], 'subStart': [sub_start.strftime('%Y-%m-%d')], 'subStat': [sub_stat], 'subEx': [sub_ex], 'key': [key]})
        global df
        df = pd.concat([df, new_item], ignore_index=True)

        # Save the updated DataFrame to the CSV file
        df.to_csv('subss.csv', index=False)

        # Confirm that the new item was added successfully
        return f"Added new item:\n{new_item.to_string(index=False)}"
    elif 'remove_item' in processed:
        # Extract the index number from the input string
        index = int(processed.split('remove_item')[1].strip())

        # Check that the index number is valid
        if index < 0 or index >= len(df):
            return f"Invalid index number. Please enter a number between 0 and {len(df) - 1}."

        # Remove the item from the DataFrame using the index number
        removed_item = df.iloc[index]
        df.drop(index, inplace=True)

        # Save the updated DataFrame to the CSV file
        df.to_csv('subss.csv', index=False)

        # Confirm that the item was removed successfully
        return f"Removed item:\n{removed_item.to_string()}"
    else:
        pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caught error {context.error}')\


if __name__ == '__main__':
    print("starting")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # update
    print("polling...")
    app.run_polling(poll_interval=5)
