import logging
from telegram.constants import ParseMode
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, CallbackQueryHandler
from telegram.ext import MessageHandler, filters
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram import ForceReply
import re
from functions import *
from sql import *
import mysql.connector
from mysql.connector import Error



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🎉 *Welcome to FairSplitBot!* 🎉\n\n"
        "Struggling to split bills after a trip? *Say no more!* 🚀 With FairSplitBot, simply:\n\n"
        "1️⃣ Create your username with /create\_username 👾\n"
        "2️⃣ Create a group with /create\_group, or join an existing one with /join\_group 🧑👩\n"
        "3️⃣ Add your expenses to the group with /add\_expense 💸\n\n"
        "Let us handle the math and split the bills equally for you! 🧮\n"
        "Enjoy hassle-free payments and more fun times with friends! 🥳\n\n"
        "Check final bills by /split\_bills.\n\n"
        "Need help or more info? Just type /help or contact *@jack_clx*"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message, parse_mode='Markdown')

    user_id = update.effective_user.id

    try:
        username = get_username(user_id)
        group_id = get_user_current_group_id(user_id)
        group_name = get_current_group_name(user_id)
        group_members = get_groupmates(user_id)

        if username and group_id:  # Check if there are group members to format the message accordingly
            formatted_group_members = ', '.join(group_members)  # Join usernames with a comma
            group_info_message = (
                f"👋 Hi *{username}*, your current group is *{group_name}*, "
                f"with members: *{formatted_group_members}*.\n\n"
                "*What would you like to do next?*\n"
                "/add\_expense - Add a new expense.\n"
                "/show\_summary - Show the expense summary.\n"
                "/show\_my\_transactions - Show your transactions.\n"
                "/split\_bills - Split the bills with your group.\n\n"
                "Looking to switch things up?\n"
                "/update\_group - Change your current group.\n"
                "/join\_group - Join a new group.\n"
                "/create\_group - Create a new group."
            )
            await context.bot.send_message(chat_id=update.effective_chat.id, text=group_info_message, parse_mode='Markdown')
        elif username:
            # Handle the case where the user has no group or group members
            no_group_message = (
                f"👋 Hi *{username}*, it looks like you're not in a group yet.\n\n"
                "Get started by creating a new group or joining an existing one:\n"
                "/create\_group - Create a new group.\n"
                "/join\_group - Join an existing group."
            )
            await context.bot.send_message(chat_id=update.effective_chat.id, text=no_group_message, parse_mode='Markdown')
        else:
            no_username_message= (
            "Getting started:\n"
            "Create a username with /create\_username.\n"
            "Need more help? Type /help."
            )
            await context.bot.send_message(chat_id=update.effective_chat.id, text=no_username_message, parse_mode='Markdown')


    except Exception as e:
        pass
        error_message = (
            "Oops, an error occured\n "
            "Getting started:\n"
            "Create a username with /create\_username.\n"
            "Need more help? Type /help."
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message, parse_mode='Markdown')
        print(f"An error occurred: {e}")  # For logging purposes



async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    help_message = (
        "*FairSplitBot Help Guide* 📚\n\n"
        "Getting started and managing your experience:\n"
        "- /start - Begin your FairSplitBot journey.\n"
        "- /create\_username - Set up a unique username for identification.\n"
        "- /create\_group - Create a new group for splitting expenses.\n"
        "- /join\_group - Join an existing group shared by friends.\n"
        "- /update\_group - Switch your active group.\n\n"
        "Managing expenses:\n"
        "- /add\_expense - Log a new expense under your name in your group.\n"
        "- /add\_expense\_all - Add an expense to be split evenly among all group members.\n"
        "- /add\_expense\_one - Record an expense for a specific individual in the group.\n"
        "- /delete\_transaction - Remove a mistakenly added transaction.\n\n"
        "Viewing information:\n"
        "- /show\_my\_transactions - Display all transactions you have logged.\n"
        "- /show\_summary - Get a summary of expenses for your group.\n\n"
        "Finalizing:\n"
        "- /split\_bills - Calculate and split the final bills of your group evenly.\n\n"
        "For additional support or feedback, use /help. Ready to simplify your bill splitting? Let's get started! 🚀"
    )

    if update.message.text == '/help':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message, parse_mode='Markdown')



async def command_create_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    if update.message.text =='/create_username':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the username you want to create:")
        context.user_data['current_state'] = 'create_username'




async def command_create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    username = get_username(user_id)

    if update.message.text =='/create_group':
        if username == None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please create a username first with /create_username.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the group name you want to create:")
            context.user_data['current_state'] = 'create_group'

async def command_update_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    if update.message.text =='/update_group':
        group_names=get_users_groups(user_id)
        output = '\n'.join(f"Group_id {group_id}: {group_name}" for group_id, group_name in group_names)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{output}\n\nEnter the numerical group id you want to change from above:\n(just the number of the group_id)")
        context.user_data['current_state'] = 'update_group'

async def join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    username = get_username(user_id)

    if update.message.text =='/join_group':
        if username == None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please create a username first with /create_username.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the group name you want to join:")
            context.user_data['current_state'] = 'join_group'

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    username = get_username(user_id)

    if update.message.text =='/add_expense':
        if username == None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please create a username first with /create_username.")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Ready to add an expense? Here's how you can do it:\n\n" +
                     "👥 /add_expense_all - Select this if the expense is split equally by everyone.\n" +
                     "👤 /add_expense_one - Select this if the expense is not split equally\n\n" +
                     f"*Kindly select /add_expense_one repeatedly if each person owes you a different amount*"
            )

async def add_expense_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    if update.message.text == '/add_expense_all':
        # Ask for the amount first
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Got it! 🌟 Please tell me the amount you paid. Just type the number (e.g., 150.75) below"
        )
        context.user_data['current_state'] = 'waiting_for_expense_amount'

async def add_expense_one (update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    groupmates = get_groupmates(user_id)
    if len(groupmates) == 0:
        message_text = (
            "Such group did not exist. Check your spelling. 🧐\n\n"
            "Try: 🚀\n"
            "- /join_group to try joining a group again.\n"
            "- /create_group to start a new group.\n"
            "- /update_group to switch to your other group."
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
        return


    # Create a custom keyboard with groupmate usernames
    keyboard = [[KeyboardButton(name)] for name in groupmates]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # Send the message with the custom keyboard
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👤 Who did you pay for? Select a groupmate below",
        reply_markup=reply_markup
    )

    # Set the next step to handle the response
    context.user_data['current_state'] = 'waiting_for_groupmate_name'
    

async def show_my_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = get_username(user_id)
    group_id = get_user_current_group_id(user_id)
    group_name = get_current_group_name(user_id)
    transactions = get_all_transactions_for_user(user_id, group_id)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                               text=f"*Expense Summary for {group_name} Group* 📊\n\n" +
                                    f"{my_transactions(transactions, username)}\n\n" +
                                    "What's next? 🚀\n" +
                                    "- /add_expense to log a new expense.\n" +
                                    "- /delete_transaction if you need to remove an expense.\n" +
                                    "- /show_summary to view this summary again.\n" +
                                    "\nFeel free to choose any option above to continue managing your expenses efficiently!")

async def command_delete_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_state = context.user_data.get('current_state', None)
    user_id = update.effective_user.id
    username = get_username(user_id)
    group_id = get_user_current_group_id(user_id)
    group_name = get_current_group_name(user_id)
    transactions = get_all_transactions_for_user(user_id, group_id)
    if update.message.text == '/delete_transaction':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"This is your *{group_name}* expense summary: \n\n{my_transactions(transactions,username)}\n\nType the numerical ID of the transaction that you would like to delete:")
        context.user_data['current_state'] = 'delete_transaction'


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group_id = get_user_current_group_id(user_id)
    group_name = get_current_group_name(user_id)
    transactions = get_all_transactions_in_group(group_id)

    # Assume summary() function formats transactions into a readable string
    formatted_summary = summary(transactions)

    if transactions:
        message_text = (
            f"*Expense Summary for {group_name} Group* 📊\n\n"
            f"{formatted_summary}\n\n"
            "What's next? 🚀\n"
            "- /add\_expense to log a new expense.\n"
            "- /split\_bills to calculate and split the final bills."
        )
    else:
        # Handle case with no transactions
        message_text = (
            f"*Oops!* It looks like there are no transactions in *{group_name}* group yet. 🤷‍♂️\n\n"
            "Get started by adding some expenses!\n"
            "- /add\_expense to add a new expense to your group."
        )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, parse_mode='Markdown')


async def split_bills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group_id = get_user_current_group_id(user_id)
    transactions = get_all_transactions_in_group(group_id)
    group_members = get_groupmates(user_id)  # Function to get all group members
    dic = transaction_dic(transactions, group_members)
    # dic1 ={'A':100,"B":1000,"C":400,"D":300,"E":700}
    
    names = list(dic.keys())
    spent = list(dic.values())

    # Step 1: Compute the total spent by all the friends.
    total = sum(spent)

    # Step 2: Determine the equal expense per person.
    expense_per_person = total / len(spent)

    # Step 3: Compute how much each person owes or gets owed.
    # Negative values mean they owe money, positive values mean they are owed money.
    owe = [i - expense_per_person for i in spent]

    # Step 4: Settle the debts.
    def settle_debts(names, owe):
        transactions = []
        tolerance = 0.01
        while max(owe) > tolerance:  # while someone still owes something
            payer_index = owe.index(min(owe))
            payee_index = owe.index(max(owe))

            amount_to_transfer = min(-owe[payer_index], owe[payee_index])

            transactions.append((names[payer_index], names[payee_index], amount_to_transfer))
            owe[payer_index] += amount_to_transfer
            owe[payee_index] -= amount_to_transfer

        return transactions

    transactions = settle_debts(names, owe)
    transaction_messages = ""

    for transaction in transactions:
        payer, payee, amount = transaction
        transaction_messages += f"{payer} should transfer {round(amount, 1)} to {payee}.\n"

    # Send the combined transaction messages as a single message
    if transaction_messages:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=transaction_messages)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No transactions needed.")



async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_state = context.user_data.get('current_state', None)
    user_id = update.effective_user.id
    text = update.message.text
    try:
        if current_state == 'create_username':
            username = text
            try:
                create_username(user_id, username)
                message_text = (
                    f"Hi {username}, your username has been created. 🎉\n\n"
                    "What's next? 🚀\n"
                    "- /create_group to start a new group.\n"
                    "- /join_group to join an existing group.\n"
                    "- /add_expense to log a new expense."
                )
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
                del context.user_data['current_state']

            except:
                username = get_username(user_id)
                message_text = (
                    f"You have already created a username: {username}.\n\n"
                    "What's next? 🚀\n"
                    "- /create_group to start a new group.\n"
                    "- /join_group to join an existing group.\n"
                    "- /add_expense to log a new expense."
                )
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
                del context.user_data['current_state']




        elif current_state == 'create_group':
            groupname = text
            try:
                group_id = create_group_name(groupname)
                add_user_to_group(user_id, group_id)
                update_current_group(user_id,group_id)
                message_text = (
                    f"Group '{groupname}' created. You are now a member. 🌟\n\n"
                    "What's next? 🚀\n"
                    "- /add_expense to add a new expense.\n"
                    "- /split_bills to calculate and split the final bills among group members."
                )
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
                del context.user_data['current_state']
            except:
                message_text = (
                    f"Sorry, we couldn't create the group '{groupname}'. 😢\n\n"
                    "The group name already exists.\n\n"
                    "Try:\n"
                    "- /create_group with a different group name to create a new group.\n"
                    "- /join_group to join another group"
                )
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
                del context.user_data['current_state']



        elif current_state == 'join_group':
            groupname = text
            try:
                group_id = list(get_group_id(groupname)[0])[0]
                add_user_to_group(user_id, group_id)
                update_current_group(user_id, group_id)
                message_text = (
                    f"You are now a member of {groupname}. 🎉\n\n"
                    "What's next? 🚀\n"
                    "- /add_expense to log a new expense for the group.\n"
                    "- /show_summary to see all group expenses.\n"
                    "- /split_bills to calculate and split the final bills among group members.\n"
                    "- /update_group - switch to your other group."
                )
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
                del context.user_data['current_state']

            except:
                message_text = (
                    "Such group did not exist. Check your spelling. 🧐\n\n"
                    "Try: 🚀\n"
                    "- /join_group to try joining a group again."
                    "- /create_group to start a new group.\n"
                    "- /update_group - switch to your other group."
                )
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
                del context.user_data['current_state']


        elif current_state == 'update_group':
            group_id = int(text)
            update_current_group(user_id,group_id)
            group_name = get_current_group_name(user_id)
            message_text = (
                f"You have updated to Group {group_name}. 🌟\n\n"
                "What's next? 🚀\n"
                "- /add_expense to add a new expense.\n"
                "- /show_my_transactions to view your transactions.\n"
                "- /show_summary to see all group expenses.\n"
                "- /split_bills to calculate and split the final bills among group members."
            )
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
            del context.user_data['current_state']


        elif current_state == 'delete_transaction':
            try:
                transaction_id = int(text)
                result = delete_transaction(transaction_id, user_id)
                message_text = (
                    f"{result}\n\n"
                    "What's next? 🚀\n"
                    "- /add_expense to log a new expense.\n"
                    "- /show_my_transactions to view your transactions.\n"
                    "- /show_summary to view the group expense summary."
                )
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
            except ValueError:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid transaction ID. Please enter a numerical ID.")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {e}")
            finally:
                del context.user_data['current_state']



        elif current_state == 'waiting_for_groupmate_name':
            # Assuming the user has just sent the groupmate's name
            groupmate_name = text
            context.user_data['groupmate_name'] = groupmate_name  # Store the name
            context.user_data['current_state'] = 'waiting_for_expense_amount'  # Update state

            # Prompt user for the next piece of information
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Got it! You paid for {groupmate_name}. Now enter the amount you paid (numerical value only):",
                reply_markup= ReplyKeyboardRemove()
            )


        elif current_state == 'waiting_for_expense_amount':
            # The user is now sending the expense amount
            try:
                expense_amount = float(text)  # Convert the text to a float
                context.user_data['expense_amount'] = expense_amount
                context.user_data['current_state'] = 'waiting_for_expense_description'  # Update state

                # Prompt user for the next piece of information
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="And what was the expense for? Please enter the description:"
                )
            except ValueError:
                # User didn't enter a valid number
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="That doesn't look like a number. Please enter the amount you paid as a number:"
                )


        elif current_state == 'waiting_for_expense_description':
            text = update.message.text
            title = text
            amount = context.user_data['expense_amount']
            user_id = update.effective_user.id
            user2 = context.user_data.get('groupmate_name', None)
            if user2 == None:
                user2_id = None
            else:
                user2_id = get_user_id(user2)
            group_id = get_user_current_group_id(user_id)
            group_name = get_current_group_name(user_id)
            transaction_id = add_transaction(title, amount, user_id, user2_id, group_id)
            if user2_id != None:
                message_text = (
                    f"Added expense of *{amount}* to {user2} for {title} in group *{group_name}*. 📝\n\n"
                    "What's next? 🚀\n"
                    "- /add_expense to log another expense.\n"
                    "- /delete_transaction to delete one transaction\n"
                    "- /show_my_transactions to view your transactions.\n"
                    "- /show_summary to view the expense summary for the group.\n"
                    "- /split_bills to calculate and split bills among group members."
                )
            else:
                message_text = (
                    f"Added expense of *{amount}* for {title} to group *{group_name}*. 📝\n\n"
                    "What's next? 🚀\n"
                    "- /add_expense to log another expense.\n"
                    "- /delete_transaction to delete one transaction\n"
                    "- /show_my_transactions to view your transactions.\n"
                    "- /show_summary to view the expense summary for the group.\n"
                    "- /split_bills to calculate and split bills among group members."
                )
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
            del context.user_data['current_state']
            del context.user_data['expense_amount']
            if user2 != None:
                del context.user_data['groupmate_name']

    except ValueError as ve:
        # Handle incorrect number formats
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid number.")
        logger.error(f"ValueError: {ve}")

    except Exception as e:
        # Handle other exceptions
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again.")
        logger.error(f"Exception: {e}")





if __name__ == '__main__':
    token_id = ''
    application = ApplicationBuilder().token(token_id).build()
    connection = create_connection("", "", '', '')




    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler ('help',help)
    create_username_handler = CommandHandler('create_username',command_create_username)
    create_group_handler = CommandHandler('create_group', command_create_group)
    join_group_handler = CommandHandler('join_group', join_group)
    update_group_handler = CommandHandler('update_group', command_update_group)
    add_expense_handler = CommandHandler('add_expense', add_expense)
    show_my_transactions_handler = CommandHandler('show_my_transactions',show_my_transactions)
    delete_transaction_handler = CommandHandler('delete_transaction',command_delete_transaction)
    show_summary_handler = CommandHandler('show_summary', show_summary)
    split_bills_handler = CommandHandler('split_bills', split_bills)
    add_expense_all_handler = CommandHandler('add_expense_all', add_expense_all)
    add_expense_one_handler = CommandHandler('add_expense_one', add_expense_one)



    application.add_handler(start_handler)
    application.add_handler(create_username_handler)
    application.add_handler(create_group_handler)
    application.add_handler(join_group_handler)
    application.add_handler(update_group_handler)
    application.add_handler(add_expense_handler)
    application.add_handler(show_my_transactions_handler)
    application.add_handler(delete_transaction_handler)
    application.add_handler(show_summary_handler)
    application.add_handler(split_bills_handler)
    application.add_handler(add_expense_all_handler)
    application.add_handler(add_expense_one_handler)
    application.add_handler(help_handler)

    text_handler = MessageHandler(filters.TEXT, handle_text)
    application.add_handler(text_handler)

    application.run_polling()
