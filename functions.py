import re

def extract_amount(text):
    match = re.match(r'(\d+):', text)
    if match:
        return int(match.group(1))
    return None

def extract_title(text):
    # Extract title, assuming it's always before the last colon
    match = re.search(r':\s*(.*?)(?::\s*[\w\s]+)?$', text)
    if match:
        return match.group(1).strip()
    return None

def extract_name(text):
    # Check if there's a second colon, if yes, extract the name
    if text.count(':') > 1:
        match = re.search(r':\s*[\w\s]*:\s*(\w+)$', text)
        if match:
            return match.group(1).strip()
    return None

def my_transactions(transactions, username):
    paid_for = []
    owes_to = []
    total_spent = 0
    total_owed = 0

    for transaction in transactions:
        id, item, amount, payer, payee = transaction
        if payer.lower() == username.lower():
            if payee:
                paid_for.append(f"ID {id}: ${amount} for '{item}' (to {payee})")
            else:
                paid_for.append(f"ID {id}: ${amount} for '{item}'")
            total_spent += amount
        elif payee and payee.lower() == username.lower():
            owes_to.append(f"ID {id}:  ${amount}  for '{item}' to {payer}")
            total_owed += amount

    formatted_list = f"Transactions for {username}:\n"
    if paid_for:
        formatted_list += "\nPaid For:\n" + "\n".join(paid_for)
    if owes_to:
        formatted_list += "\n\nOwes:\n" + "\n".join(owes_to)
    formatted_list += f"\n\nSummary:\nTotal Spent: {total_spent} \nTotal Owed: {total_owed} "

    return formatted_list



def summary(transactions):
    total_expense = 0
    user_summary = {}

    for transaction in transactions:
        amount = transaction[2]  # Transaction amount
        item = transaction[1]    # Item description
        username1 = transaction[-2]  # created_by user
        username2 = transaction[-1]  # created_to user if exists, otherwise this might be missing or None

        if username1 not in user_summary:
            user_summary[username1] = {'paid_for': [], 'owes': []}

        if username2:  # If created_to user exists
            if username2 not in user_summary:
                user_summary[username2] = {'paid_for': [], 'owes': []}
            user_summary[username1]['paid_for'].append((amount, item, username2))
            user_summary[username2]['owes'].append((amount, item, username1))
        else:
            # Ensure a third element is added, even if it's None
            user_summary[username1]['paid_for'].append((amount, item, None))


    output_lines = []
    for username, details in user_summary.items():
        paid_lines = [f"Paid {amount} for {item}" + (f" for {username2}" if username2 else "") for amount, item, username2 in details['paid_for']]
        owes_lines = [f"Owes {amount} for {item} to {username1}" for amount, item, username1 in details['owes']]
        total_paid = sum(amount for amount, _, _ in details['paid_for'])
        total_owed = sum(amount for amount, _, _ in details['owes'])
        total_expense += total_paid - total_owed
        total_spent = total_paid - total_owed

        user_lines = [f"{username}'s transactions:"] + paid_lines + owes_lines + [f"Total spent: {total_spent}"]
        output_lines.extend(user_lines + [""])  # Add an empty string for spacing

    output_lines.append(f"Total expense incurred: {total_expense}")
    formatted_output = "\n".join(output_lines)
    return formatted_output



def transaction_dic(transactions, group_members):
    expense_dict = {member: 0 for member in group_members}  # Initialize all members with zero expense

    for _, _, amount, _, _, _, _, created_by_username, created_to_username in transactions:
        # Handling the user who created the transaction
        if created_by_username in expense_dict:
            expense_dict[created_by_username] += amount
        else:
            expense_dict[created_by_username] = amount

        # If there is a user to whom the transaction was created
        if created_to_username:
            # Reduce the receiver's total by the amount
            if created_to_username in expense_dict:
                expense_dict[created_to_username] -= amount
            else:
                # In case the receiver is not yet in the dictionary, we initialize with a negative value
                expense_dict[created_to_username] = -amount

    return expense_dict
    