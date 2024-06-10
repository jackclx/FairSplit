import mysql.connector
from mysql.connector import Error, InterfaceError, OperationalError
import time
connection = None

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    tries = 3  # Number of retries
    for attempt in range(tries):
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            if connection.is_connected():
                print("MySQL Database connection successful")
                break
        except Error as err:
            print(f"Error: '{err}'")
            time.sleep(5)  # Wait for 5 seconds before retrying
        if attempt == tries - 1:  # This was the last attempt
            raise Exception("Database connection failed after several attempts")
    return connection




def reconnect_if_needed():
    global connection
    try:
        if connection is None or not connection.is_connected():
            print("Reconnecting to the database...")
            connection = create_connection("","","","")
    except Error as err:
        print(f"Error while reconnecting: {err}")
        raise

def execute_query(query, params=None, fetch_result=False):
    global connection
    reconnect_if_needed()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        if fetch_result:
            result = cursor.fetchall()
            connection.commit()
            return result  # Return all rows for select queries
        else:
            rowcount =  cursor.rowcount
            connection.commit()
            return rowcount

    except Error as err:
        print(f"Error: '{err}' occurred while executing the query")
        raise
    finally:
        if cursor:
            cursor.close()




def create_username(user_id, username, current_group_id=None):
    query = "INSERT INTO users (user_id, username, current_group_id) VALUES (%s, %s, %s)"
    execute_query(query, (user_id, username, current_group_id))
    print(f"Username '{username}' created.")


def update_current_group(user_id, new_group_id):
    query = "UPDATE users SET current_group_id = %s WHERE user_id = %s"
    execute_query(query, (new_group_id, user_id))
    print(f"User {user_id}'s current group updated to {new_group_id}.")


def get_username(user_id):
    query = "SELECT username FROM users WHERE user_id = %s"
    result = execute_query(query, (user_id,), fetch_result=True)
    if result:
        return result[0][0]  # Return the username
    return None

def delete_user(user_id):
    query = "DELETE FROM users WHERE id = %s"
    execute_query(query, (user_id,), fetch_result = True)
    print(f"User with id {user_id} deleted.")

def create_group_name(groupname):
    query = "INSERT INTO split_groups (groupname) VALUES (%s)"
    execute_query(query, (groupname,))
    last_id_query = "SELECT LAST_INSERT_ID();"
    result = execute_query(last_id_query, fetch_result=True)
    print(result)
    print(f"Group '{groupname}' created.")
    return result[0][0]


def add_user_to_group(user_id, group_id):
    query = "SELECT COUNT(*) FROM user_groups WHERE user_id = %s AND group_id = %s"
    result = execute_query(query, (user_id, group_id), fetch_result= True)
    print(result)
    if result[0][0] == 0 :
        query = "INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)"
        execute_query(query, (user_id, group_id))
        print(f"User {user_id} added to group {group_id}.")
    else:
        print(f"User {user_id} is already a member of group {group_id}.")




def delete_group(group_id):
    query = "DELETE FROM split_groups WHERE id = %s"
    execute_query(query, (group_id,))
    print(f"Group with id {group_id} deleted.")


def add_transaction(title, amount, created_by, created_to, group_id):
    query = """
    INSERT INTO transactions (title, amount, created_by, created_to, group_id, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    """
    transaction_id = execute_query(query, (title, amount, created_by, created_to, group_id))
    print(f"Transaction '{title}' added.")
    return transaction_id


def delete_transaction(transaction_id, user_id):
    query = "DELETE FROM transactions WHERE id = %s AND created_by = %s"
    affected_rows = execute_query(query, (transaction_id, user_id),fetch_result=False)
    if affected_rows > 0:
        result = f"Transaction with id {transaction_id} deleted."
    else:
        result = f"No transaction with id {transaction_id} found for deletion or you are trying to delete what you owe."
    return result


def get_all_transactions_for_user(user_id, group_id):
    query = """
    SELECT t.id, t.title, t.amount, u1.username AS created_by_username, u2.username AS created_to_username
    FROM transactions t
    JOIN users u1 ON t.created_by = u1.user_id
    LEFT JOIN users u2 ON t.created_to = u2.user_id
    WHERE (t.created_by = %s OR t.created_to = %s) AND t.group_id = %s
    ORDER BY t.created_at ASC
    """
    result = execute_query(query, (user_id, user_id, group_id), fetch_result=True)
    for transaction in result:
        print(transaction)
    return result


def get_all_transactions_in_group(group_id):
    query = """
    SELECT t.*, u1.username AS created_by_username, u2.username AS created_to_username
    FROM transactions t
    JOIN users u1 ON t.created_by = u1.user_id
    LEFT JOIN users u2 ON t.created_to = u2.user_id
    WHERE t.group_id = %s
    """
    result = execute_query(query, (group_id,), fetch_result=True)
    for transaction in result:
        print(transaction)
    return result





def get_group_id(group_name):
    query = "SELECT * FROM split_groups WHERE groupname = %s"
    result = execute_query(query, (group_name,), fetch_result=True)
    return result


def get_current_group_name(user_id):
    query = """
    SELECT sg.groupname
    FROM users u
    JOIN split_groups sg ON u.current_group_id = sg.id
    WHERE u.user_id = %s
    """
    result = execute_query(query, (user_id,), fetch_result=True)
    if result:
        return result[0][0]
    return None



def get_user_current_group_id(user_id):
    query = "SELECT users.current_group_id FROM users WHERE user_id= %s"
    result = execute_query(query, (user_id,), fetch_result=True)
    if result:
        return result[0][0]
    return None


def get_users_groups(user_id):
    query = """
    SELECT split_groups.* FROM split_groups
    JOIN user_groups ON user_groups.group_id = split_groups.id
    WHERE user_groups.user_id = %s
    """
    result = execute_query(query, (user_id,), fetch_result=True)
    for group in result:
        print(group)
    return result

def get_users_in_group(group_id):
    query = """
    SELECT users.* FROM users
    JOIN user_groups ON user_groups.user_id = users.id
    WHERE user_groups.group_id = %s
    """
    result = execute_query(query, (group_id,), fetch_result=True)
    for user in result:
        print(user)
    return result


def get_groupmates(user_id):
    query = """
    SELECT u.username FROM users u
    JOIN user_groups ug ON u.user_id = ug.user_id
    WHERE ug.group_id = (
        SELECT current_group_id FROM users WHERE user_id = %s
    ) AND u.user_id != %s;
    """
    result = execute_query(query, (user_id, user_id), fetch_result=True)
    groupmates = [username[0] for username in result]
    return groupmates

#include user himself
def get_all_groupmates(user_id):
    query = """
    SELECT u.username FROM users u
    JOIN user_groups ug ON u.user_id = ug.user_id
    WHERE ug.group_id = (
        SELECT current_group_id FROM users WHERE user_id = %s
    )
    ;
    """
    result = execute_query(query, (user_id,), fetch_result=True)
    groupmates = [username[0] for username in result]
    return groupmates



def get_user_id(username):
    query = "SELECT users.user_id FROM users WHERE users.username = %s"
    result = execute_query(query, (username,), fetch_result=True)
    if result:
        return result[0][0]
    return None
