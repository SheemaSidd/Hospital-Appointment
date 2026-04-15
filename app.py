import sqlite3
import json
import gradio as gr
from groq import Groq

# ==============================
# CONFIG
# ==============================
GROQ_API_KEY = "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"
MODEL_NAME = "llama-3.1-8b-instant"

client = Groq(api_key=GROQ_API_KEY)

# ==============================
# DATABASE INIT
# ==============================
def init_db():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            department TEXT,
            date TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================
# TOOL FUNCTIONS
# ==============================
def book_appointment(patient_name, department, date, time):
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (patient_name, department, date, time) VALUES (?, ?, ?, ?)",
        (patient_name, department, date, time)
    )
    conn.commit()
    conn.close()
    return f"✅ Appointment booked for {patient_name} in {department} on {date} at {time}."

def view_appointments():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT patient_name, department, date, time FROM appointments")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No appointments found."

    text = "📋 Appointments:\n"
    for r in rows:
        text += f"{r[0]} | {r[1]} | {r[2]} | {r[3]}\n"
    return text

# ==============================
# MCP TOOL DEFINITIONS
# ==============================
tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book a hospital appointment when user provides name, department, date and time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "department": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"}
                },
                "required": ["patient_name", "department", "date", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_appointments",
            "description": "Show all hospital appointments.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# ==============================
# CHAT FUNCTION (STABLE)
# ==============================
def hospital_chat(user_message, history):

    base_messages = [
        {"role": "system", "content": 
         "You are a hospital booking assistant. "
         "If user wants to book appointment and provides name, department, date and time, "
         "you MUST call book_appointment tool. "
         "If user asks to see appointments, call view_appointments tool."},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=base_messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # ---------------- TOOL CALL ----------------
    if message.tool_calls:

        tool_call = message.tool_calls[0]
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if func_name == "book_appointment":
            result = book_appointment(
                args["patient_name"],
                args["department"],
                args["date"],
                args["time"]
            )
        elif func_name == "view_appointments":
            result = view_appointments()
        else:
            result = "Unknown function."

        # SECOND CALL WITH TOOL RESULT
        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                base_messages[0],
                base_messages[1],
                {
                    "role": "assistant",
                    "tool_calls": message.tool_calls
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
            ]
        )

        return final_response.choices[0].message.content

    # If no tool call
    return message.content


# ==============================
# GRADIO UI
# ==============================
demo = gr.ChatInterface(
    fn=hospital_chat,
    title="🏥 AI Hospital Booking System",
    description="Book or view appointments using natural language."
)

demo.launch()
