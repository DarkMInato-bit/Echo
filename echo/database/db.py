import os
import bcrypt
import datetime
from cryptography.fernet import Fernet
import mysql.connector
from mysql.connector import errorcode

KEY_FILE = "secret.key"

def generate_key():
    """Generates a key and saves it into a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

def load_key():
    """Loads the key from the current directory named secret.key."""
    if not os.path.exists(KEY_FILE):
        generate_key()
    return open(KEY_FILE, "rb").read()

KEY = load_key()
FERNET = Fernet(KEY)

def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="deadsec123",
            database="voice_insight"
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Invalid credentials")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

def initialize_database():
    conn = get_mysql_connection()
    if not conn:
        print("Database not connected. Falling back to local text storage.")
        return True
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                contact_encrypted BLOB
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speech_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                text_encrypted BLOB NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Local Text File Helper Operations
def _read_local_users():
    if not os.path.exists("local_users.txt"):
        return {}
    users = {}
    try:
        with open("local_users.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3:
                    username, pw_hash, contact = parts
                    users[username] = {"pw_hash": pw_hash, "contact": contact}
    except Exception as e:
        print(f"Error reading local users: {e}")
    return users

def _write_local_users(users):
    try:
        with open("local_users.txt", "w") as f:
            for username, data in users.items():
                f.write(f"{username}|{data['pw_hash']}|{data['contact']}\n")
    except Exception as e:
        print(f"Error writing local users: {e}")

def register_user(username, password, contact):
    conn = get_mysql_connection()
    if not conn:
        try:
            users = _read_local_users()
            if username in users:
                return False, "Username already exists."
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            contact_encrypted = FERNET.encrypt(contact.encode('utf-8'))
            users[username] = {
                "pw_hash": password_hash.decode('utf-8'), 
                "contact": contact_encrypted.hex()
            }
            _write_local_users(users)
            return True, "User registered successfully in local storage!"
        except Exception as e:
            return False, f"Registration failed locally: {e}"

    cursor = conn.cursor()
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        contact_encrypted = FERNET.encrypt(contact.encode('utf-8'))
        cursor.execute(
            "INSERT INTO users (username, password_hash, contact_encrypted) VALUES (%s, %s, %s)", 
            (username, password_hash.decode('utf-8'), contact_encrypted)
        )
        conn.commit()
        return True, "User registered successfully!"
    except mysql.connector.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, f"Registration failed: {e}"
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    conn = get_mysql_connection()
    if not conn:
        try:
            users = _read_local_users()
            if username in users:
                user_data = users[username]
                if bcrypt.checkpw(password.encode('utf-8'), user_data["pw_hash"].encode('utf-8')):
                    return True, username  # Return username as ID for local fallback
            return False, "Invalid username or password."
        except Exception as e:
            return False, f"Login failed locally: {e}"

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            return True, user[0]
        else:
            return False, "Invalid username or password."
    except Exception as e:
        return False, f"Login failed: {e}"
    finally:
        cursor.close()
        conn.close()

def save_spoken_text_to_db(user_id, text):
    conn = get_mysql_connection()
    if not conn:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text_encrypted = FERNET.encrypt(text.encode('utf-8'))
            with open("local_history.txt", "a") as f:
                f.write(f"{user_id}|{timestamp}|{text_encrypted.hex()}\n")
        except Exception as e:
            print(f"Error saving spoken text locally: {e}")
        return

    cursor = conn.cursor()
    try:
        text_encrypted = FERNET.encrypt(text.encode('utf-8'))
        cursor.execute(
            "INSERT INTO speech_history (user_id, text_encrypted) VALUES (%s, %s)", 
            (user_id, text_encrypted)
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving spoken text: {e}")
    finally:
        cursor.close()
        conn.close()

def load_user_history_from_db(user_id):
    conn = get_mysql_connection()
    if not conn:
        if not os.path.exists("local_history.txt"):
            return []
        history = []
        try:
            with open("local_history.txt", "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        u_id, timestamp, text_encrypted_hex = parts
                        if str(u_id) == str(user_id):
                            try:
                                text_enc = bytes.fromhex(text_encrypted_hex)
                                text = FERNET.decrypt(text_enc).decode('utf-8')
                                history.append((text, timestamp))
                            except Exception:
                                pass
            history.sort(key=lambda x: x[1], reverse=True)
            return history
        except Exception as e:
            print(f"Error loading user history locally: {e}")
            return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT text_encrypted, timestamp FROM speech_history WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
        history = cursor.fetchall()
        decrypted_history = [(FERNET.decrypt(text).decode('utf-8'), timestamp) for text, timestamp in history]
        return decrypted_history
    except Exception as e:
        print(f"Error loading user history: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def save_report_to_db(user_id, filename, file_path):
    conn = get_mysql_connection()
    if not conn:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("local_reports.txt", "a") as f:
                f.write(f"{user_id}|{timestamp}|{filename}|{file_path}\n")
        except Exception as e:
            print(f"Error saving report locally: {e}")
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO report_history (user_id, filename, file_path) VALUES (%s, %s, %s)",
            (user_id, filename, file_path)
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving report to the database: {e}")
    finally:
        cursor.close()
        conn.close()

def get_latest_report_path(user_id):
    conn = get_mysql_connection()
    if not conn:
        if not os.path.exists("local_reports.txt"):
            return None
        latest_report = None
        latest_time = ""
        try:
            with open("local_reports.txt", "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 4:
                        u_id, timestamp, filename, file_path = parts
                        if str(u_id) == str(user_id):
                            if timestamp > latest_time:
                                latest_time = timestamp
                                latest_report = file_path
            return latest_report
        except Exception as e:
            print(f"Error reading local reports: {e}")
            return None

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT file_path FROM report_history WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1",
            (user_id,)
        )
        result = cursor.fetchone()
        return result["file_path"] if result else None
    except Exception as e:
        print(f"Error fetching latest report: {e}")
        return None
    finally:
        cursor.close()
        conn.close()