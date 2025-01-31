import os
import mysql.connector
import uuid
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

# Load environment variables
load_dotenv()
mysql_password = os.getenv('MYSQL_PASSWORD')
gemini_api_key = os.getenv('GEMINI_API_KEY')

if not mysql_password or not gemini_api_key:
    raise ValueError("API keys are not properly loaded!")

# Database connection
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password=mysql_password,
    database='langchain_demo'
)
db_cursor = db_connection.cursor()

# Initialize LLM
llm = ChatGoogleGenerativeAI(api_key=gemini_api_key, model="gemini-1.5-flash")

def signup(name, mobile, email):
    user_id = str(uuid.uuid4())
    db_cursor.execute(
        "INSERT INTO users (id, name, mobile, email) VALUES (%s, %s, %s, %s)",
        (user_id, name, mobile, email)
    )
    db_connection.commit()
    return user_id

def login(email):
    db_cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = db_cursor.fetchone()
    return user[0] if user else None

def get_chat_history(user_id):
    db_cursor.execute(
        "SELECT message_type, content, timestamp FROM chat_history WHERE client = %s ORDER BY timestamp",
        (user_id,)
    )
    return db_cursor.fetchall()

def save_chat(session_id, user_id, user_input, response):
    db_cursor.execute(
        "INSERT INTO chat_history (session_id, client, message_type, content, timestamp) VALUES (%s, %s, %s, %s, NOW())",
        (session_id, user_id, 'human', user_input)
    )
    db_cursor.execute(
        "INSERT INTO chat_history (session_id, client, message_type, content, timestamp) VALUES (%s, %s, %s, %s, NOW())",
        (session_id, user_id, 'ai', response)
    )
    db_connection.commit()

def chat_session(user_id):
    session_id = str(uuid.uuid4())  # Generate a unique session ID
    chat_history = [SystemMessage(content="You are a helpful assistant.")]
    
    # Load previous chat history
    previous_messages = get_chat_history(user_id)
    
    for message_type, content, timestamp in previous_messages:
        if message_type == 'human':
            chat_history.append(HumanMessage(content=content))
        else:
            chat_history.append(AIMessage(content=content))
    
    return session_id, chat_history

def process_user_input(user_id, user_input, chat_history, session_id):  # Accept session_id as a parameter
    if user_input:
        chat_history.append(HumanMessage(content=user_input))
        result = llm.invoke(chat_history)
        response = result.content
        chat_history.append(AIMessage(content=response))
        
        if user_id:
            save_chat(session_id, user_id, user_input, response)  # Pass session_id here
        
        return response
    
    return None

def display_chat_history(user_id):
    previous_messages = get_chat_history(user_id)
    chat_history = ""
    
    for message_type, content, timestamp in previous_messages:
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        if message_type == 'human':
            chat_history += f"You: {content} (at {formatted_time})\n"
        else:
            chat_history += f"AI: {content} (at {formatted_time})\n"
    
    return chat_history
