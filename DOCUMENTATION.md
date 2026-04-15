# Hospital Appointment Booking System
## IEEE Standard Documentation for B.Tech Students

---

## 1. ABSTRACT

This document presents a comprehensive technical specification for a Hospital Appointment Booking System developed using Python, Streamlit, SQLite3, and the Groq AI API. The system provides a user-friendly interface for managing hospital appointments through both conversational AI chat and traditional form-based interfaces. The application implements appointment booking, modification, cancellation, and availability checking features with natural language processing capabilities.

**Keywords:** Appointment Management, AI Chat Integration, SQLite Database, Streamlit Web Framework, Natural Language Processing

---

## 2. INTRODUCTION

### 2.1 Purpose
The Hospital Appointment Booking System aims to streamline the appointment scheduling process by providing:
- Real-time availability checking
- Natural language processing for conversational booking
- Intuitive user interface with multiple interaction modes
- Data persistence using SQLite3 database

### 2.2 Scope
This document covers:
- System architecture and design
- Database schema and operations
- API integration details
- User interface specifications
- Algorithm implementations
- Testing requirements

### 2.3 Definitions and Acronyms
- **AI**: Artificial Intelligence
- **API**: Application Programming Interface
- **CRUD**: Create, Read, Update, Delete
- **GUI**: Graphical User Interface
- **NLP**: Natural Language Processing
- **UI**: User Interface

---

## 3. SYSTEM OVERVIEW

### 3.1 System Description
The Hospital Appointment Booking System is a web-based application that allows users to:
1. Book new appointments
2. View existing appointments
3. Modify appointment dates and times
4. Cancel appointments
5. Check slot availability
6. Interact via conversational AI

### 3.2 System Architecture
```
???????????????????????????????????????????????????
?          Streamlit Web Interface                ?
???????????????????????????????????????????????????
?  ?? Chat Interface (Tab 1)                      ?
?  ?? View Appointments (Tab 2)                   ?
?  ?? Book Appointment (Tab 3)                    ?
?  ?? Modify Appointment (Tab 4)                  ?
?  ?? Cancel Appointment (Tab 5)                  ?
???????????????????????????????????????????????????
?       Application Logic Layer (Python)          ?
???????????????????????????????????????????????????
?  Groq AI API ? Tool Functions? Parse Functions   ?
???????????????????????????????????????????????????
? chat_completion? CRUD Ops   ? NLP Conversion   ?
???????????????????????????????????????????????????
           ?
           ?
???????????????????????????????????????????????????
?      SQLite3 Database Layer                     ?
???????????????????????????????????????????????????
?  appointments table                             ?
?  ?? id (INTEGER, PRIMARY KEY)                   ?
?  ?? name (TEXT)                                 ?
?  ?? date (TEXT, YYYY-MM-DD)                     ?
?  ?? time (TEXT, HH:MM:SS)                       ?
?  ?? phone (TEXT)                                ?
???????????????????????????????????????????????????
```

---

## 4. FUNCTIONAL REQUIREMENTS

### 4.1 User Requirements
| Req ID | Description | Priority | Status |
|--------|-------------|----------|--------|
| UR-001 | User can book appointments via chat | High | Complete |
| UR-002 | User can view all appointments | High | Complete |
| UR-003 | User can modify appointment times | High | Complete |
| UR-004 | User can cancel appointments | High | Complete |
| UR-005 | User can check slot availability | Medium | Complete |
| UR-006 | System suggests available slots | Medium | Complete |
| UR-007 | Chat supports natural language | High | Complete |

### 4.2 System Requirements
| Req ID | Description | Priority | Status |
|--------|-------------|----------|--------|
| SR-001 | Check availability before booking | High | Complete |
| SR-002 | Parse natural language dates/times | High | Complete |
| SR-003 | Prevent double-booking | High | Complete |
| SR-004 | Maintain data persistence | High | Complete |
| SR-005 | Real-time appointment updates | Medium | Complete |
| SR-006 | Error handling and validation | High | Complete |

---

## 5. DETAILED DESIGN

### 5.1 Database Design

#### 5.1.1 Appointments Table
```sql
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL (YYYY-MM-DD),
    time TEXT NOT NULL (HH:MM:SS),
    phone TEXT NOT NULL
)
```

#### 5.1.2 Data Constraints
- **Primary Key:** id (Auto-increment)
- **Unique Constraint:** (date, time) combination prevents double-booking
- **NOT NULL:** All fields must be provided
- **Date Format:** YYYY-MM-DD (ISO 8601)
- **Time Format:** HH:MM:SS (24-hour)
- **Phone Format:** Numeric string

### 5.2 Function Specifications

#### 5.2.1 book_appointment(name, date, time, phone)
**Purpose:** Create new appointment record
**Input Parameters:**
- name (string): Patient name
- date (string): Appointment date (YYYY-MM-DD)
- time (string): Appointment time (HH:MM:SS)
- phone (string): Contact number

**Process Flow:**
1. Connect to database
2. Execute INSERT query with parameters
3. Commit transaction
4. Return confirmation message

**Error Handling:**
- Database connection failures
- Invalid data format
- SQL injection prevention via parameterized queries

**Returns:** Confirmation string with appointment details

#### 5.2.2 check_availability(date, time)
**Purpose:** Verify if a time slot is available
**Algorithm:**
```
1. Connect to database
2. Query: SELECT COUNT(*) FROM appointments 
   WHERE date = ? AND time = ?
3. IF count == 0 THEN
     RETURN "Available"
   ELSE
     RETURN "Not Available"
4. Close connection
```

**Returns:** Availability status string

#### 5.2.3 modify_appointment(appointment_id, new_date, new_time)
**Purpose:** Update existing appointment
**Validation Steps:**
1. Validate appointment_id is numeric
2. Check if appointment exists
3. Verify new slot is available
4. Prevent conflict with other appointments

**Process:**
```
1. Convert ID to integer
2. SELECT appointment WHERE id = ?
3. IF NOT EXISTS RETURN Error
4. Check availability of new slot
5. IF NOT AVAILABLE RETURN Error
6. UPDATE appointment SET date, time
7. COMMIT and RETURN Success
```

**Returns:** Confirmation or error message

#### 5.2.4 cancel_appointment(appointment_id)
**Purpose:** Remove appointment record
**Process:**
1. Validate and convert ID
2. Check existence
3. Delete record
4. Commit transaction

**Returns:** Cancellation confirmation

#### 5.2.5 get_available_slots(date)
**Purpose:** Generate list of available time slots
**Algorithm:**
```
1. Query booked times: SELECT time FROM appointments WHERE date = ?
2. Generate all slots: 09:00 to 17:00, every 30 minutes
3. Filter out booked slots
4. Return formatted string with available slots
5. IF no slots available RETURN "No available slots"
```

**Slot Range:** 09:00:00 - 17:00:00 (30-minute intervals)
**Returns:** Formatted string with available slots

#### 5.2.6 parse_natural_date(date_str)
**Purpose:** Convert natural language dates to YYYY-MM-DD
**Supported Formats:**
- "today" ? Current date
- "tomorrow" ? Next day
- "next day" ? Day after tomorrow
- "YYYY-MM-DD" ? Direct parsing

**Algorithm:**
```
1. Normalize input to lowercase
2. Check keyword matches
3. IF keyword found: Calculate date
4. ELSE: Parse ISO format
5. RETURN formatted date string
```

#### 5.2.7 parse_natural_time(time_str)
**Purpose:** Convert natural language times to HH:MM:SS
**Supported Formats:**
- "3 PM" ? "15:00:00"
- "3:30 PM" ? "15:30:00"
- "15:30" ? "15:30:00"
- "3:30:00 PM" ? "15:30:00"

**Parsing Strategy:**
1. Replace case-insensitive am/pm markers
2. Try each format sequentially
3. Return first successful parse
4. Return input if no format matches

### 5.3 Chat Function Design

#### 5.3.1 hospital_chat(user_message)
**Purpose:** Process user input and execute appropriate tool
**Architecture:**
```
Input ? System Prompt + Message
  ?
Groq API (LLM Processing)
  ?
Tool Detection & Validation
  ?
Execute Tool Function
  ?
Tool Response
  ?
Final LLM Response
  ?
Output to User
```

**Tool Calling Strategy:**
- One tool call per request (tool_choice="auto")
- Validation before execution
- Error messages if data incomplete

**Supported Tools:**
1. book_appointment
2. view_appointments
3. check_availability
4. modify_appointment
5. cancel_appointment
6. get_available_slots

---

## 6. IMPLEMENTATION DETAILS

### 6.1 Technology Stack
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Streamlit | Latest |
| Backend | Python | 3.8+ |
| Database | SQLite3 | Embedded |
| AI API | Groq | gsk_* |
| Data Processing | Pandas | Latest |
| Date/Time | datetime | Built-in |

### 6.2 Key Libraries
```python
import streamlit as st          # Web framework
import sqlite3                  # Database
import json                     # JSON parsing
import pandas as pd             # Data manipulation
import datetime as dt           # Date/time handling
import time                     # Sleep function
from groq import Groq           # AI API client
```

### 6.3 Session State Management
```python
st.session_state.messages          # Chat history list
st.session_state.processing        # Processing flag
```

### 6.4 Error Handling Strategy

**Database Errors:**
```python
try:
    # Database operation
except (sqlite3.Error, ValueError, TypeError) as e:
    return f"Error: {str(e)}"
finally:
    conn.close()  # Always close connection
```

**API Errors:**
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    return f"Error: {str(e)}"
```

**Validation Errors:**
```python
if not name or not date or not time_str or not phone:
    missing = [field for field in [name, date, time_str, phone] if not field]
    return f"Missing: {', '.join(missing)}"
```

---

## 7. USER INTERFACE DESIGN

### 7.1 Tab Structure
| Tab # | Name | Function | Features |
|-------|------|----------|----------|
| 1 | Chat | Conversational AI booking | Message history, Real-time processing |
| 2 | View Appointments | List all appointments | Refresh button, Dataframe display |
| 3 | Book Appointment | Form-based booking | Date/time picker, Availability check |
| 4 | Modify Appointment | Update appointments | ID input, Date/time picker, Availability check |
| 5 | Cancel Appointment | Delete appointments | ID input, Confirmation |

### 7.2 Chat Interface Design
```
????????????????????????????????????
?    Chat Container                ?
?  ??????????????????????????????  ?
?  ? User: Hello                ?  ?
?  ? Assistant: Hi! How can...  ?  ?
?  ? User: Book tomorrow        ?  ?
?  ? Assistant: Sure! I need... ?  ?
?  ? User: John, 3pm, 9876...   ?  ?
?  ? Assistant: Booked!         ?  ?
?  ??????????????????????????????  ?
?                                  ?
?  [Type your message...]          ?
????????????????????????????????????
```

### 7.3 Sidebar Features
- Quick Actions button (Clear Chat History)
- Feature information display
- Navigation links

---

## 8. ALGORITHMS

### 8.1 Availability Checking Algorithm
```
Algorithm: CHECK_AVAILABILITY(date, time)
Input: date (YYYY-MM-DD), time (HH:MM:SS)
Output: Boolean (available)

BEGIN
    connection ? OPEN_DATABASE()
    query ? "SELECT COUNT(*) FROM appointments 
             WHERE date = ? AND time = ?"
    result ? EXECUTE(query, [date, time])
    count ? result[0]
    
    IF count == 0 THEN
        CLOSE(connection)
        RETURN TRUE
    ELSE
        CLOSE(connection)
        RETURN FALSE
    END IF
END
```

### 8.2 Natural Language Parsing Algorithm
```
Algorithm: PARSE_NATURAL_TIME(time_str)
Input: time_str (string)
Output: formatted_time (HH:MM:SS)

BEGIN
    normalized ? LOWERCASE(TRIM(time_str))
    
    // Replace AM/PM markers
    FOR each (am_variant, pm_variant) IN replacements:
        normalized ? REPLACE(normalized, am_variant, "AM")
        normalized ? REPLACE(normalized, pm_variant, "PM")
    END FOR
    
    // Try each format
    formats ? ["%I:%M:%S %p", "%I:%M %p", "%I %p", "%H:%M:%S", "%H:%M"]
    
    FOR each format IN formats:
        TRY
            parsed_time ? PARSE(normalized, format)
            RETURN FORMAT(parsed_time, "%H:%M:%S")
        EXCEPT
            CONTINUE
        END TRY
    END FOR
    
    RETURN time_str  // Return as-is if no format matches
END
```

### 8.3 Slot Generation Algorithm
```
Algorithm: GET_AVAILABLE_SLOTS(date)
Input: date (YYYY-MM-DD)
Output: available_slots (list of strings)

BEGIN
    booked_times ? QUERY("SELECT time FROM appointments WHERE date = ?")
    booked_set ? CONVERT_TO_SET(booked_times)
    
    available_slots ? EMPTY_LIST
    
    FOR hour FROM 9 TO 16:  // 9 AM to 4:30 PM
        FOR minute IN [0, 30]:
            time_slot ? FORMAT("{hour:02d}:{minute:02d}:00")
            
            IF time_slot NOT IN booked_set THEN
                ADD(available_slots, time_slot)
            END IF
        END FOR
    END FOR
    
    IF LENGTH(available_slots) == 0 THEN
        RETURN "No available slots"
    ELSE
        RETURN FORMAT_AS_STRING(available_slots)
    END IF
END
```

---

## 9. TESTING AND VALIDATION

### 9.1 Unit Test Cases

#### Test Case: TC-001 Book Valid Appointment
- **Input:** name="John Doe", date="2024-02-25", time="10:00:00", phone="9876543210"
- **Expected:** Database entry created, confirmation returned
- **Status:** Pass

#### Test Case: TC-002 Prevent Double Booking
- **Input:** Same date, time as existing appointment
- **Expected:** Error message returned, appointment not created
- **Status:** Pass

#### Test Case: TC-003 Parse Natural Date
- **Input:** "tomorrow"
- **Expected:** Next day in YYYY-MM-DD format
- **Status:** Pass

#### Test Case: TC-004 Parse Natural Time
- **Input:** "3 PM"
- **Expected:** "15:00:00"
- **Status:** Pass

#### Test Case: TC-005 Modify Appointment
- **Input:** ID=1, new_date="2024-02-25", new_time="14:00:00"
- **Expected:** Appointment updated, confirmation returned
- **Status:** Pass

#### Test Case: TC-006 Cancel Appointment
- **Input:** ID=1
- **Expected:** Appointment deleted, confirmation returned
- **Status:** Pass

### 9.2 Integration Tests
| Test | Component | Result |
|------|-----------|--------|
| Chat-Database | User message ? Tool ? DB Update | Pass |
| Form-Database | Form submission ? Validation ? DB Insert | Pass |
| Availability-Booking | Check ? Book flow | Pass |
| Multi-tab Sync | Update in one tab reflects in another | Pass |

### 9.3 Validation Rules
1. **Phone Number:** Non-empty string
2. **Date:** Valid YYYY-MM-DD format
3. **Time:** Valid HH:MM:SS format
4. **Name:** Non-empty string
5. **Appointment ID:** Positive integer

---

## 10. PERFORMANCE ANALYSIS

### 10.1 Time Complexity
| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Book Appointment | O(1) | Direct INSERT |
| Check Availability | O(n) | WHERE clause scan |
| Get Available Slots | O(n + m) | n=booked, m=generated slots |
| Modify Appointment | O(n) | Check existing + UPDATE |
| Cancel Appointment | O(1) | Direct DELETE by ID |

### 10.2 Space Complexity
| Component | Complexity | Description |
|-----------|-----------|-------------|
| Chat History | O(n) | n = number of messages |
| Appointments Table | O(m) | m = number of appointments |
| Available Slots | O(16) | Fixed 16 slots per day |

### 10.3 Optimization Strategies
1. **Indexing:** Create index on (date, time) for faster availability checks
2. **Caching:** Cache available slots for current day
3. **Query Optimization:** Use parameterized queries to prevent SQL injection

---

## 11. SECURITY CONSIDERATIONS

### 11.1 SQL Injection Prevention
```python
# ? SAFE - Parameterized queries
cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))

# ? UNSAFE - String concatenation
cursor.execute(f"SELECT * FROM appointments WHERE id = {appointment_id}")
```

### 11.2 Input Validation
- All user inputs are stripped and validated
- Type checking before database operations
- Format validation for dates and times

### 11.3 API Security
- Groq API key should be stored in environment variables
- Never expose API keys in code
- Use secure credential management

### 11.4 Data Privacy
- No sensitive data stored beyond appointment details
- Phone numbers stored as required by business logic
- Consider GDPR compliance for production

---

## 12. DEPLOYMENT GUIDELINES

### 12.1 System Requirements
- Python 3.8 or higher
- Internet connection (for Groq API)
- 100 MB disk space minimum
- Modern web browser

### 12.2 Installation Steps
```bash
# 1. Clone repository
git clone <repository-url>

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export GROQ_API_KEY="your-api-key"

# 5. Run application
streamlit run streamlit_app.py
```

### 12.3 Production Deployment
- Use environment-based configuration
- Enable HTTPS for data transmission
- Implement backup strategies for database
- Monitor application logs
- Set up error tracking

---

## 13. MAINTENANCE AND SUPPORT

### 13.1 Regular Maintenance
- Database optimization: VACUUM SQLite periodically
- Log rotation: Archive old logs
- Security updates: Keep libraries updated
- Performance monitoring: Track API response times

### 13.2 Known Limitations
1. Single-threaded SQLite (not suitable for high concurrency)
2. No user authentication in current version
3. Time slots fixed to 30-minute intervals
4. Operating hours: 9 AM to 5 PM only

### 13.3 Future Enhancements
1. User authentication and multi-user support
2. Doctor/specialist scheduling
3. Patient history tracking
4. Email/SMS notifications
5. Payment integration
6. Reporting and analytics

---

## 14. CONCLUSION

The Hospital Appointment Booking System successfully demonstrates the integration of modern web technologies with AI-powered conversational interfaces. The system provides a robust, user-friendly solution for appointment management with comprehensive error handling, data validation, and security measures.

**Key Achievements:**
- ? Functional appointment management system
- ? Natural language processing integration
- ? Intuitive user interface with multiple interaction modes
- ? Data persistence and integrity
- ? Comprehensive error handling

---

## 15. REFERENCES

1. Groq API Documentation: https://console.groq.com/docs
2. Streamlit Documentation: https://docs.streamlit.io
3. SQLite3 Python Documentation: https://docs.python.org/3/library/sqlite3.html
4. IEEE Standard 830-1998: Software Requirements Specification
5. Date and Time Standard (ISO 8601): https://www.iso.org/iso-8601-date-and-time-format.html

---

## APPENDICES

### Appendix A: Sample Data
```
ID | Name | Date | Time | Phone
1  | John Doe | 2024-02-15 | 10:00:00 | 9876543210
2  | Jane Smith | 2024-02-16 | 14:30:00 | 9876543211
3  | Mike Brown | 2024-02-17 | 09:00:00 | 9876543212
```

### Appendix B: API Response Example
```json
{
  "status": "success",
  "message": "Appointment booked for John Doe on 2024-02-25 at 14:00:00",
  "appointment_id": 7
}
```

### Appendix C: Configuration Parameters
```python
GROQ_API_KEY = "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"
MODEL_NAME = "llama-3.1-8b-instant"
DATABASE_NAME = "hospital.db"
OPERATING_HOURS_START = 9  # 9 AM
OPERATING_HOURS_END = 17   # 5 PM
SLOT_INTERVAL = 30         # minutes
```

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Author:** Development Team  
**Status:** Complete and Verified
