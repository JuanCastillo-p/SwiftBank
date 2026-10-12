# bank_backend.py
import mysql.connector
from decimal import Decimal

# ------------------------------
# Database Connection
# ------------------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bank"
    )

# ------------------------------
# Bank Logic Class
# ------------------------------
class BankLogic:
    def __init__(self):
        self.db = connect_db()
        self.cursor = self.db.cursor(dictionary=True)
        self.logged_in_user = None
        # Track failed login and PIN attempts (in-memory)
        self.login_attempts = 0
        self.pin_attempts = 0

    def logTransaction(self, bank_id, action, amount, balance_after):
        sql = """
        INSERT INTO transaction_logs (bank_id, action_type, amount, balance_after)
        VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(sql, (bank_id, action, amount, balance_after))
        self.db.commit()

    def openAccount(self, name, address, pin, balance):
        # Validate required fields
        if not name or not name.strip() or not address or not address.strip():
            return False, "Name and address are required."

        if len(pin) != 4 or not pin.isdigit():
            return False, "PIN must be exactly 4 digits."

        try:
            balance = Decimal(balance)
        except:
            return False, "Invalid amount."

        if balance < 100 or balance > 500000 or balance % 50 != 0:
            return False, "Deposit must be between ₱100–₱500,000 and in ₱50 increments."

        self.cursor.execute(
            "INSERT INTO bankaccount (bank_user, bank_address, bank_pin, bank_balance) VALUES (%s, %s, %s, %s)",
            (name, address, pin, balance)
        )
        self.db.commit()

        account_id = self.cursor.lastrowid
        self.logTransaction(account_id, "Account Created", balance, balance)
        # reset attempt counters after account creation just in case
        self.login_attempts = 0
        self.pin_attempts = 0
        return True, f"Account created! Your Account ID: {account_id}"

    def login(self, account_id, name, pin):
        try:
            account_id = int(account_id)
        except:
            self.login_attempts += 1
            if self.login_attempts >= 3:
                # too many failed login attempts -> go back to starting screen
                self.login_attempts = 0
                return False, "Too many failed login attempts. Returning to starting screen."
            return False, f"Invalid Account ID. Attempts left: {3 - self.login_attempts}"

        self.cursor.execute(
            "SELECT * FROM bankaccount WHERE bank_id=%s AND bank_user=%s AND bank_pin=%s",
            (account_id, name, pin)
        )
        user = self.cursor.fetchone()

        if user:
            self.logged_in_user = user
            # reset attempt counters on successful login
            self.login_attempts = 0
            self.pin_attempts = 0
            return True, f"Welcome, {user['bank_user']}!"

        # failed authentication
        self.login_attempts += 1
        if self.login_attempts >= 3:
            self.login_attempts = 0
            return False, "Too many failed login attempts. Returning to starting screen."
        return False, f"Login failed. Check your credentials. Attempts left: {3 - self.login_attempts}"

    def deposit(self, amount, pin):
        user = self.logged_in_user
        try:
            amount = Decimal(amount)
        except:
            return False, "Invalid amount."

        if amount < 100 or amount % 50 != 0:
            return False, "Deposit must be at least ₱100 and in ₱50 increments."
        if user["bank_balance"] + amount > 500000:
            return False, "Balance cannot exceed ₱500,000."
        if pin != user["bank_pin"]:
            # increment PIN attempts and logout after 3 failures
            self.pin_attempts += 1
            if self.pin_attempts >= 3:
                self.pin_attempts = 0
                self.logged_in_user = None
                return False, "Incorrect PIN. Account logged out after 3 failed PIN attempts."
            return False, f"Incorrect PIN. Attempts left: {3 - self.pin_attempts}"

        # correct PIN -> reset pin attempts
        self.pin_attempts = 0

        new_balance = user["bank_balance"] + amount
        self.cursor.execute("UPDATE bankaccount SET bank_balance=%s WHERE bank_id=%s",
                            (new_balance, user["bank_id"]))
        self.db.commit()
        self.logTransaction(user["bank_id"], "Deposit", amount, new_balance)
        user["bank_balance"] = new_balance
        return True, f"Deposited ₱{amount:.2f}. New balance: ₱{new_balance:.2f}"

    def withdraw(self, amount, pin):
        user = self.logged_in_user
        try:
            amount = Decimal(amount)
        except:
            return False, "Invalid amount."

        if amount < 100 or amount % 50 != 0:
            return False, "Withdrawal must be at least ₱100 and in ₱50 increments."
        if amount > user["bank_balance"]:
            return False, "Insufficient balance."
        if pin != user["bank_pin"]:
            # increment PIN attempts and logout after 3 failures
            self.pin_attempts += 1
            if self.pin_attempts >= 3:
                self.pin_attempts = 0
                self.logged_in_user = None
                return False, "Incorrect PIN. Account logged out after 3 failed PIN attempts."
            return False, f"Incorrect PIN. Attempts left: {3 - self.pin_attempts}"

        # correct PIN -> reset pin attempts
        self.pin_attempts = 0

        new_balance = user["bank_balance"] - amount
        self.cursor.execute("UPDATE bankaccount SET bank_balance=%s WHERE bank_id=%s",
                            (new_balance, user["bank_id"]))
        self.db.commit()
        self.logTransaction(user["bank_id"], "Withdrawal", amount, new_balance)
        user["bank_balance"] = new_balance
        return True, f"Withdrawn ₱{amount:.2f}. New balance: ₱{new_balance:.2f}"

    def transfer(self, receiver_id, amount, pin):
        sender = self.logged_in_user
        self.cursor.execute("SELECT * FROM bankaccount WHERE bank_id=%s", (receiver_id,))
        receiver = self.cursor.fetchone()

        if not receiver:
            return False, "Recipient not found."

        try:
            amount = Decimal(amount)
        except:
            return False, "Invalid amount."

        if amount < 100:
            return False, "Transfer must be at least ₱100."
        if amount > sender["bank_balance"]:
            return False, "Insufficient balance."
        if receiver["bank_balance"] + amount > 500000:
            return False, "Recipient balance limit exceeded."
        if pin != sender["bank_pin"]:
            # increment PIN attempts and logout after 3 failures
            self.pin_attempts += 1
            if self.pin_attempts >= 3:
                self.pin_attempts = 0
                self.logged_in_user = None
                return False, "Incorrect PIN. Account logged out after 3 failed PIN attempts."
            return False, f"Incorrect PIN. Attempts left: {3 - self.pin_attempts}"

        # correct PIN -> reset pin attempts
        self.pin_attempts = 0

        new_sender_balance = sender["bank_balance"] - amount
        new_receiver_balance = receiver["bank_balance"] + amount

        self.cursor.execute("UPDATE bankaccount SET bank_balance=%s WHERE bank_id=%s",
                            (new_sender_balance, sender["bank_id"]))
        self.cursor.execute("UPDATE bankaccount SET bank_balance=%s WHERE bank_id=%s",
                            (new_receiver_balance, receiver_id))
        self.db.commit()

        self.logTransaction(sender["bank_id"], "Transfer Sent", amount, new_sender_balance)
        self.logTransaction(receiver_id, "Transfer Received", amount, new_receiver_balance)

        sender["bank_balance"] = new_sender_balance
        return True, f"Transferred ₱{amount:.2f} to {receiver['bank_user']}. New balance: ₱{new_sender_balance:.2f}"

    def getLogs(self):
        user = self.logged_in_user
        self.cursor.execute("SELECT * FROM transaction_logs WHERE bank_id=%s ORDER BY log_time DESC LIMIT 20",
                            (user["bank_id"],))
        return self.cursor.fetchall()

    def refreshUser(self):
        self.cursor.execute("SELECT * FROM bankaccount WHERE bank_id=%s",
                            (self.logged_in_user["bank_id"],))
        self.logged_in_user = self.cursor.fetchone()