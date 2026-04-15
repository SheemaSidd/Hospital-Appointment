import streamlit as st
import sqlite3
import json
import pandas as pd
import datetime as dt
import time
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
            name TEXT,
            date TEXT,
            time TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================
# ADD SAMPLE DATA
# ==============================
def add_sample_appointments():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # Check if sample data already exists
    cursor.execute("SELECT COUNT(*) FROM appointments")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_data = [
            ("John Doe", "2024-02-15", "10:00:00", "9876543210"),
            ("Jane Smith", "2024-02-16", "14:30:00", "9876543211"),
            ("Mike Brown", "2024-02-17", "09:00:00", "9876543212"),
            ("Sarah Wilson", "2024-02-18", "11:00:00", "9876543213"),
            ("Robert Taylor", "2024-02-19", "15:00:00", "9876543214"),
            ("Emily Martinez", "2024-02-20", "13:00:00", "9876543215"),
        ]
        
        for name, date, time, phone in sample_data:
            cursor.execute(
                "INSERT INTO appointments (name, date, time, phone) VALUES (?, ?, ?, ?)",
                (name, date, time, phone)
            )
        
        conn.commit()
    
    conn.close()

add_sample_appointments()

# ==============================
# TOOL FUNCTIONS
# ==============================
def book_appointment(name, date, time, phone):
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (name, date, time, phone) VALUES (?, ?, ?, ?)",
        (name, date, time, phone)
    )
    conn.commit()
    conn.close()
    return f"Appointment booked for {name} on {date} at {time}. Phone: {phone}"

def view_appointments():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, date, time, phone FROM appointments ORDER BY date, time")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No appointments found."

    text = "Appointments:\n"
    for r in rows:
        text += f"ID: {r[0]} | Name: {r[1]} | Date: {r[2]} | Time: {r[3]} | Phone: {r[4]}\n"
    return text

def check_availability(date, time):
    """Check if a time slot is available"""
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE date = ? AND time = ?", (date, time))
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        return f"Available - Slot is free on {date} at {time}"
    else:
        return f"Not Available - Slot is already booked on {date} at {time}"

def modify_appointment(appointment_id, new_date, new_time):
    """Modify an existing appointment"""
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # Convert to int if it's a string
    try:
        appointment_id = int(appointment_id)
    except (ValueError, TypeError):
        conn.close()
        return f"Error: Invalid appointment ID. Please provide a numeric ID."
    
    # Check if appointment exists
    cursor.execute("SELECT name, phone FROM appointments WHERE id = ?", (appointment_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return f"Error: Appointment ID {appointment_id} not found. Please check the ID and try again."
    
    name, phone = result
    
    # Check if new slot is available
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE date = ? AND time = ? AND id != ?", 
                   (new_date, new_time, appointment_id))
    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        return f"Error: Slot on {new_date} at {new_time} is already booked. Please choose a different time."
    
    # Update the appointment
    cursor.execute("UPDATE appointments SET date = ?, time = ? WHERE id = ?", 
                   (new_date, new_time, appointment_id))
    conn.commit()
    conn.close()
    
    return f"Appointment {appointment_id} for {name} has been successfully modified to {new_date} at {new_time}."

def cancel_appointment(appointment_id):
    """Cancel an existing appointment"""
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # Convert to int if it's a string
    try:
        appointment_id = int(appointment_id)
    except (ValueError, TypeError):
        conn.close()
        return f"Error: Invalid appointment ID. Please provide a numeric ID."
    
    # Check if appointment exists
    cursor.execute("SELECT name, date, time FROM appointments WHERE id = ?", (appointment_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return f"Error: Appointment ID {appointment_id} not found. Please check the ID and try again."
    
    name, date, time = result
    
    # Delete the appointment
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    
    return f"Successfully cancelled! Appointment {appointment_id} for {name} on {date} at {time} has been removed from the system."

def get_appointments_data():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, date, time, phone FROM appointments ORDER BY date, time")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_available_slots(date):
    """Get all available time slots for a specific date"""
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT time FROM appointments WHERE date = ?", (date,))
    booked_times = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Generate time slots (every 30 minutes from 09:00 to 17:00)
    available_slots = []
    start_hour = 9
    end_hour = 17
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}:00"
            if time_str not in booked_times:
                available_slots.append(time_str)
    
    # Return as formatted string
    if available_slots:
        slots_text = "Available slots on " + str(date) + ":\n"
        for slot in available_slots:
            slots_text += f"{slot}\n"
        return slots_text
    else:
        return f"No available slots on {date}. Please choose a different date."

def parse_natural_date(date_str):
    """Convert natural language dates to YYYY-MM-DD format"""
    date_str = date_str.lower().strip()
    today = dt.date.today()
    
    if date_str in ["today"]:
        return today.strftime("%Y-%m-%d")
    elif date_str in ["tomorrow"]:
        tomorrow = today + dt.timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    elif date_str in ["next day"]:
        next_day = today + dt.timedelta(days=2)
        return next_day.strftime("%Y-%m-%d")
    else:
        # Try to parse as standard date format
        try:
            parsed = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
            return parsed.strftime("%Y-%m-%d")
        except:
            return date_str

def parse_natural_time(time_str):
    """Convert natural language times to HH:MM:SS format"""
    time_str = time_str.lower().strip()
    
    # Handle common time formats
    replacements = {
        "am": "AM",
        "pm": "PM",
        "a.m.": "AM",
        "p.m.": "PM",
    }
    
    for key, value in replacements.items():
        time_str = time_str.replace(key, value)
    
    # Try various time formats
    time_formats = [
        "%I:%M:%S %p",  # 03:30:00 PM
        "%I:%M %p",     # 03:30 PM
        "%I %p",        # 3 PM
        "%H:%M:%S",     # 15:30:00
        "%H:%M",        # 15:30
    ]
    
    for fmt in time_formats:
        try:
            parsed = dt.datetime.strptime(time_str, fmt).time()
            return parsed.strftime("%H:%M:%S")
        except:
            continue
    
    # If nothing matches, return as is
    return time_str

# ==============================
# MCP TOOL DEFINITIONS
# ==============================
tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment when user provides name, date, time and phone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "phone": {"type": "string"}
                },
                "required": ["name", "date", "time", "phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_appointments",
            "description": "Show all appointments.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check if a time slot is available on a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "time": {"type": "string"}
                },
                "required": ["date", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_appointment",
            "description": "Modify an existing appointment with new date and time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"},
                    "new_date": {"type": "string"},
                    "new_time": {"type": "string"}
                },
                "required": ["appointment_id", "new_date", "new_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"}
                },
                "required": ["appointment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Get all available time slots for a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"}
                },
                "required": ["date"]
            }
        }
    }
]

# ==============================
# CHAT FUNCTION
# ==============================
def hospital_chat(user_message):
    base_messages = [
        {"role": "system", "content": 
         "You are a helpful booking assistant. "
         "Handle ONE action at a time. "
         "IMPORTANT: Before calling any function, check if you have ALL required information. "
         "For book_appointment: you need NAME, DATE, TIME (HH:MM:SS format), and PHONE. "
         "For modify_appointment: you need APPOINTMENT_ID, NEW_DATE, and NEW_TIME. "
         "For cancel_appointment: you need APPOINTMENT_ID. "
         "If any information is missing, ASK the user for it instead of calling the function. "
         "If user wants to book an appointment and you have all info, call book_appointment tool. "
         "If user wants to check availability, call check_availability tool. "
         "If user wants to modify an appointment, call modify_appointment tool. "
         "If user wants to cancel an appointment, call cancel_appointment tool. "
         "If user asks to see appointments, call view_appointments tool. "
         "If user asks for available slots on a date, call get_available_slots tool. "
         "Always format time as HH:MM:SS (24-hour format). Examples: 09:00:00, 14:00:00 (2pm), 15:30:00 (3:30pm). "
         "Always format date as YYYY-MM-DD. Example: 2024-02-15. "
         "Call only ONE tool per response. Never call multiple tools in one response. "
         "Be conversational and helpful in your responses."},
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=base_messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=500
        )

        message = response.choices[0].message

        # Handle tool calls - only process ONE tool call
        if hasattr(message, 'tool_calls') and message.tool_calls:
            # Take only the first tool call
            tool_call = message.tool_calls[0]
            func_name = tool_call.function.name
            
            try:
                args = json.loads(tool_call.function.arguments)
            except:
                args = {}

            if func_name == "book_appointment":
                # Validate all required fields exist
                name = args.get("name", "").strip()
                date = args.get("date", "").strip()
                time_str = args.get("time", "").strip()
                phone = args.get("phone", "").strip()
                
                # Check if any field is missing
                if not name or not date or not time_str or not phone:
                    missing = []
                    if not name: missing.append("name")
                    if not date: missing.append("date")
                    if not time_str: missing.append("time")
                    if not phone: missing.append("phone")
                    return f"I need the following information to book an appointment: {', '.join(missing)}. Please provide these details."
                
                # Parse natural language date and time
                date = parse_natural_date(date)
                time_str = parse_natural_time(time_str)
                
                result = book_appointment(name, date, time_str, phone)
                
            elif func_name == "view_appointments":
                result = view_appointments()
                
            elif func_name == "check_availability":
                # Convert time format if needed
                time_str = args.get("time", "").strip()
                date = args.get("date", "").strip()
                
                if not date or not time_str:
                    return "Please provide both date and time to check availability."
                
                # Parse natural language date and time
                date = parse_natural_date(date)
                time_str = parse_natural_time(time_str)
                
                result = check_availability(date, time_str)
                
            elif func_name == "modify_appointment":
                # Validate required fields
                appointment_id = args.get("appointment_id", "").strip()
                new_date = args.get("new_date", "").strip()
                time_str = args.get("new_time", "").strip()
                
                if not appointment_id or not new_date or not time_str:
                    missing = []
                    if not appointment_id: missing.append("appointment ID")
                    if not new_date: missing.append("new date")
                    if not time_str: missing.append("new time")
                    return f"I need: {', '.join(missing)}. Please provide these details."
                
                # Parse natural language date and time
                new_date = parse_natural_date(new_date)
                time_str = parse_natural_time(time_str)
                
                result = modify_appointment(appointment_id, new_date, time_str)
                
            elif func_name == "cancel_appointment":
                appointment_id = args.get("appointment_id", "").strip()
                
                if not appointment_id:
                    return "Please provide the appointment ID to cancel."
                
                result = cancel_appointment(appointment_id)
                
            elif func_name == "get_available_slots":
                date = args.get("date", "").strip()
                
                if not date:
                    return "Please provide a date to check available slots."
                
                # Parse natural language date
                date = parse_natural_date(date)
                
                result = get_available_slots(date)
                # Result is already a formatted string, no need to convert
            else:
                result = "Unknown function."

            try:
                # Second call with tool result
                final_response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        base_messages[0],
                        base_messages[1],
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        },
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result)
                        }
                    ],
                    max_tokens=500
                )
                return final_response.choices[0].message.content
            except Exception as e:
                return str(result)

        # If no tool call
        if hasattr(message, 'content'):
            return message.content
        else:
            return "Unable to process request"
    except Exception as e:
        return f"Error: {str(e)}"


# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(page_title="Appointment Booking", layout="wide")

st.title("Appointment Booking System")
st.markdown("Book or view appointments using natural language or the form below.")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Chat", "View Appointments", "Book Appointment", "Modify Appointment", "Cancel Appointment"])

# TAB 1: CHAT
with tab1:
    st.subheader("Chat with Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "processing" not in st.session_state:
        st.session_state.processing = False

    # Create a container for chat messages
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input at the bottom (stays fixed)
    user_input = st.chat_input("Type your message...")
    
    if user_input and not st.session_state.processing:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.processing = True
        
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get bot response
        with st.spinner("Processing..."):
            bot_response = hospital_chat(user_input)
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        
        # Show bot response
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        
        st.session_state.processing = False

# TAB 2: VIEW APPOINTMENTS
with tab2:
    st.subheader("All Appointments")
    
    if st.button("Refresh Appointments"):
        st.cache_data.clear()
        st.rerun()
    
    appointments_data = get_appointments_data()
    
    if appointments_data:
        df = pd.DataFrame(
            appointments_data,
            columns=["ID", "Name", "Date", "Time", "Phone"]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info(f"Total Appointments: {len(appointments_data)}")
    else:
        st.info("No appointments found.")

# TAB 3: BOOK APPOINTMENT
with tab3:
    st.subheader("Book New Appointment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name")
        phone = st.text_input("Phone Number")
    
    with col2:
        date = st.date_input("Date")
        time = st.time_input("Time")
    
    if st.button("Book Appointment"):
        if name and phone:
            # Check availability first
            availability = check_availability(str(date), str(time))
            if "Not Available" in availability:
                st.error(availability)
                
                # Show available slots
                st.warning("This slot is not available. Here are available slots on this date:")
                available_slots = get_available_slots(str(date))
                
                if available_slots:
                    st.info(f"Available time slots on {date}:")
                    for slot in available_slots:
                        st.write(f"- {slot}")
                else:
                    st.warning("No available slots on this date. Please choose a different date.")
            else:
                result = book_appointment(name, str(date), str(time), phone)
                st.success(result)
                st.balloons()
                time.sleep(1.5)
                st.cache_data.clear()
                st.rerun()
        else:
            st.error("Please enter name and phone number")

# TAB 4: MODIFY APPOINTMENT
with tab4:
    st.subheader("Modify Appointment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        appointment_id = st.number_input("Appointment ID", min_value=1, step=1)
        new_date = st.date_input("New Date", key="modify_date")
    
    with col2:
        st.write("")
        st.write("")
        new_time = st.time_input("New Time", key="modify_time")
    
    # Check availability button
    if st.button("Check Availability"):
        availability = check_availability(str(new_date), str(new_time))
        if "free" in availability.lower():
            st.success(availability)
        else:
            st.warning(availability)
            # Show available slots
            st.info("Available time slots on this date:")
            available_slots = get_available_slots(str(new_date))
            if available_slots:
                for slot in available_slots:
                    st.write(f"- {slot}")
            else:
                st.warning("No available slots on this date.")
    
    # Modify button
    if st.button("Modify Appointment"):
        availability = check_availability(str(new_date), str(new_time))
        if "Not Available" in availability:
            st.error(availability)
            # Show available slots
            st.warning("Available time slots on this date:")
            available_slots = get_available_slots(str(new_date))
            if available_slots:
                for slot in available_slots:
                    st.write(f"- {slot}")
            else:
                st.warning("No available slots on this date.")
        else:
            result = modify_appointment(str(appointment_id), str(new_date), str(new_time))
            if "Error" in result:
                st.error(result)
            else:
                st.success(result)
                st.balloons()
                time.sleep(1.5)
                st.cache_data.clear()
                st.rerun()

# TAB 5: CANCEL APPOINTMENT
with tab5:
    st.subheader("Cancel Appointment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cancel_id = st.number_input("Appointment ID to Cancel", min_value=1, step=1, key="cancel_id")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Cancel Appointment"):
            result = cancel_appointment(str(cancel_id))
            if "Error" in result:
                st.error(result)
            else:
                st.success(result)
                st.balloons()
                # Wait a moment before refreshing
                time.sleep(1.5)
                st.cache_data.clear()
                st.rerun()

# Sidebar
st.sidebar.title("Quick Actions")
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    "Features:\n"
    "- Chat to book or view\n"
    "- View all appointments\n"
    "- Book with form\n"
    "- Modify existing appointments\n"
    "- Cancel appointments\n"
    "- Check availability before booking"
)
