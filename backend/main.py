# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
import numpy as np
import cv2
from pydantic import BaseModel, Field
from database import get_db_connection, delete_face_data, get_face_data, save_face_data, get_office_settings, update_office_settings, migrate_add_gender_column, migrate_add_mobile_no_column, migrate_add_address_column, migrate_add_joining_date_column
from recognize_module import recognize_and_log_image
from register_module import router as register_router  # Import router
from typing import Optional, List
import os
import base64
from hashlib import sha256
from collections import defaultdict
import calendar
from datetime import datetime, date, time, timedelta
import sqlite3
import io
import csv


class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUpdate(BaseModel):
    current_username: str
    current_password: str
    new_username: Optional[str] = None
    new_password: Optional[str] = None

class Employee(BaseModel):
    id: str
    name: str
    email: str
    mobile_no: str
    address: str
    gender: str
    department: str
    position: str
    salary: Optional[float] = None
    working_hours_per_day: Optional[float] = None
    employee_type: Optional[str] = None
    joining_date: date

class PunchOutRequest(BaseModel):
    name: str

class Holiday(BaseModel):
    date: date
    name: str
    description: Optional[str] = None
    type: str
    is_recurring: bool = False

    class Config:
        from_attributes = True

class HolidayInDB(Holiday):
    id: int

class Leave(BaseModel):
    employee_id: str
    leave_date: date
    leave_type: str
    reason: Optional[str] = None
    status: str = "approved"

    class Config:
        from_attributes = True

class LeaveInDB(Leave):
    id: int
    created_at: datetime

class WorkingDay(BaseModel):
    date: date
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],  # Add your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register endpoint from register_module.py
app.include_router(register_router)

# Ensure gender, mobile_no, and address columns exist
migrate_add_gender_column()
migrate_add_mobile_no_column()
migrate_add_address_column()
migrate_add_joining_date_column()

# Database is initialized separately - not on every server startup
from database import init_database
init_database()

# Attendance marking endpoint
@app.post("/mark_attendance")
async def mark_attendance(file: UploadFile = File(...)):
    contents = await file.read()
    np_img = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    if frame is None:
        return {"status": "error", "message": "Invalid image"}

    result = recognize_and_log_image(frame)
    return result

@app.post("/employees/")
def create_employee(emp: Employee):
    print("[DEBUG] Received employee data:", emp)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if employee with this ID already exists
        cur.execute("SELECT id, name FROM employees WHERE id = ?", (emp.id,))
        existing = cur.fetchone()
        if existing:
            return {"status": "error", "message": f"Employee with ID '{emp.id}' already exists (Name: {existing[1]})"}
        cur.execute("""
            INSERT INTO employees (id, name, email, mobile_no, address, gender, department, position, salary, working_hours_per_day, employee_type, joining_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (emp.id, emp.name, emp.email, emp.mobile_no, emp.address, emp.gender, emp.department, emp.position, emp.salary, emp.working_hours_per_day, emp.employee_type, emp.joining_date))
        emp_id = emp.id # ID is provided in input
        conn.commit()
        print(f"[DEBUG] Employee inserted with id: {emp_id}")
        return {"status": "success", "employee_id": emp_id}
    except Exception as e:
        print("[ERROR] Failed to insert employee:", e)
        conn.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            return {"status": "error", "message": f"Employee with ID '{emp.id}' already exists"}
        return {"status": "error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

@app.get("/employees/")
def get_employees():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, mobile_no, address, gender, department, position, salary, working_hours_per_day, (photo_data IS NOT NULL) as has_photo, employee_type, joining_date FROM employees;")
    rows = cur.fetchall()
    rows = rows or []
    cur.close()
    conn.close()
    employees = [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "mobile_no": row[3],
            "address": row[4],
            "gender": row[5],
            "department": row[6],
            "position": row[7],
            "salary": row[8],
            "working_hours_per_day": row[9],
            "has_photo": row[10],
            "employee_type": row[11],
            "joining_date": row[12]
        }
        for row in rows
    ]
    return {"employees": employees}

@app.put("/employees/{emp_id}")
def update_employee(emp_id: str, emp: Employee):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE employees SET name=?, email=?, mobile_no=?, address=?, gender=?, department=?, position=?, salary=?, working_hours_per_day=?, employee_type=?, joining_date=?, updated_at=CURRENT_TIMESTAMP 
            WHERE id=?
        """, (emp.name, emp.email, emp.mobile_no, emp.address, emp.gender, emp.department, emp.position, emp.salary, emp.working_hours_per_day, emp.employee_type, emp.joining_date, emp_id))
        conn.commit()
        return {"status": "success", "employee_id": emp_id}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # The ON DELETE CASCADE on the attendance table will handle deleting associated attendance records.
        cur.execute("DELETE FROM employees WHERE id=?", (emp_id,))
        conn.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {"status": "success", "employee_id": emp_id}
    except Exception as e:
        conn.rollback()
        if isinstance(e, HTTPException):
            raise e
        return {"status": "error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

@app.get("/employees/{emp_id}/photo")
def get_employee_photo(emp_id: str):
    """Get employee photo from database"""
    embedding_data, photo_data = get_face_data(emp_id)
    
    if photo_data is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Convert memoryview to bytes if necessary
    if hasattr(photo_data, 'tobytes'):
        photo_data = photo_data.tobytes()
    elif hasattr(photo_data, 'encode'):
        # If it's already bytes, no conversion needed
        pass
    else:
        # Convert to bytes
        photo_data = bytes(photo_data)
    
    return Response(content=photo_data, media_type="image/jpeg")

@app.put("/employees/{emp_id}/photo")
async def update_employee_photo(emp_id: str, file: UploadFile = File(...)):
    """Update employee photo and face embedding"""
    contents = await file.read()
    
    # Check if employee exists
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM employees WHERE id = ?", (emp_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Employee not found")
    finally:
        cur.close()
        conn.close()
    
    # Process image and extract embedding
    try:
        np_img = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Import here to avoid circular imports
        from insightface.app import FaceAnalysis
        import mediapipe as mp
        from sklearn.metrics.pairwise import cosine_similarity
        import pickle
        
        # Face detection
        mp_face_detection = mp.solutions.face_detection
        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.6) as face_detection:
            results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if not results.detections:
                raise HTTPException(status_code=400, detail="No face detected")
        
        # Get embedding
        embedder = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        embedder.prepare(ctx_id=0, det_size=(640, 640))
        faces = embedder.get(frame)
        
        if not faces:
            raise HTTPException(status_code=400, detail="Could not extract embedding")
        
        embedding = faces[0].normed_embedding
        embedding_bytes = pickle.dumps(embedding)
        
        # Save to database
        success = save_face_data(emp_id, embedding_bytes, contents)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save face data")
        
        return {"status": "success", "message": "Photo updated successfully"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/login")
def login(admin_login: AdminLogin):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT username, password_hash FROM admin WHERE username = ?", (admin_login.username,))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        username, password_hash = result
        password_to_check_hash = sha256(admin_login.password.encode()).hexdigest()

        if password_hash != password_to_check_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # In a real app, you would return a JWT token here
        return {"status": "success", "message": "Login successful", "user": {"name": username, "role": "admin"}}
    finally:
        cur.close()
        conn.close()

@app.put("/admin/credentials")
def update_admin_credentials(admin_update: AdminUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # First, find the single admin record. We assume there is only one.
        cur.execute("SELECT id, password_hash FROM admin ORDER BY id LIMIT 1")
        result = cur.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="No admin user found in the system.")

        admin_id, current_password_hash_from_db = result
        
        # Verify the current password provided by the user
        password_to_check_hash = sha256(admin_update.current_password.encode()).hexdigest()
        if current_password_hash_from_db != password_to_check_hash:
            raise HTTPException(status_code=401, detail="Invalid current password.")

        # Prepare the new credentials
        new_username = admin_update.new_username
        new_password_hash = None
        if admin_update.new_password:
            new_password_hash = sha256(admin_update.new_password.encode()).hexdigest()

        # Build the update query dynamically based on what needs to be changed
        update_fields = []
        update_values = []

        if new_username:
            update_fields.append("username = ?")
            update_values.append(new_username)
        
        if new_password_hash:
            update_fields.append("password_hash = ?")
            update_values.append(new_password_hash)

        if not update_fields:
            # Nothing to update
            return {"status": "success", "message": "No changes were made."}

        update_query = f"UPDATE admin SET {', '.join(update_fields)} WHERE id = ?"
        update_values.append(admin_id)

        cur.execute(update_query, tuple(update_values))

        conn.commit()
        return {"status": "success", "message": "Credentials updated successfully."}
        
    except HTTPException as e:
        conn.rollback()
        raise e
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.post("/holidays/", response_model=HolidayInDB)
def create_holiday(holiday: Holiday):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO holidays (date, name, description, type, is_recurring)
            VALUES (?, ?, ?, ?, ?)
            """,
            (holiday.date, holiday.name, holiday.description, holiday.type, holiday.is_recurring)
        )
        new_id = cur.lastrowid
        conn.commit()
        return HolidayInDB(id=new_id, **holiday.dict())
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="A holiday on this date already exists.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/holidays/")
def get_holidays_for_year(year: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, date, name, description, type, is_recurring
            FROM holidays
            WHERE strftime('%Y', date) = ? AND type != 'WORKING_DAY'
            ORDER BY date
        """, (str(year),))
        rows = cur.fetchall()
        rows = rows or []
        cur.close()
        conn.close()
        holidays = [
            {
                "id": row[0],
                "date": row[1],
                "name": row[2],
                "description": row[3],
                "type": row[4],
                "is_recurring": row[5],
            }
            for row in rows
        ]
        return holidays
    except Exception as e:
        print(f"[ERROR] failed to fetch holidays: {e}")
        return []

@app.delete("/holidays/{holiday_id}", status_code=204)
def delete_holiday(holiday_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM holidays WHERE id = ?", (holiday_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Holiday not found")
        conn.commit()
    finally:
        cur.close()
        conn.close()

# --- Leave Management Endpoints ---
@app.post("/leaves/", response_model=LeaveInDB)
def create_leave(leave: Leave):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if employee exists
        cur.execute("SELECT id FROM employees WHERE id = ?", (leave.employee_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if leave already exists for this employee on this date
        cur.execute("SELECT id FROM leaves WHERE employee_id = ? AND leave_date = ?", (leave.employee_id, leave.leave_date))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Leave already exists for this employee on this date")
        
        cur.execute(
            """
            INSERT INTO leaves (employee_id, leave_date, leave_type, reason, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (leave.employee_id, leave.leave_date, leave.leave_type, leave.reason, leave.status)
        )
        new_id = cur.lastrowid
        created_at = datetime.now() # Approximate
        conn.commit()
        return LeaveInDB(id=new_id, created_at=created_at, **leave.dict())
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Leave already exists for this employee on this date.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/leaves/", response_model=List[LeaveInDB])
def get_leaves_for_month(year: int, month: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT l.id, l.employee_id, l.leave_date, l.leave_type, l.reason, l.status, l.created_at, e.name as employee_name
            FROM leaves l
            JOIN employees e ON l.employee_id = e.id
            WHERE strftime('%Y', l.leave_date) = ? AND strftime('%m', l.leave_date) = ?
            ORDER BY l.leave_date, e.name
        """, (str(year), f"{month:02d}"))
        rows = cur.fetchall()
        return [LeaveInDB(
            id=r[0], employee_id=r[1], leave_date=r[2], leave_type=r[3], 
            reason=r[4], status=r[5], created_at=r[6]
        ) for r in rows]
    finally:
        cur.close()
        conn.close()

@app.get("/leaves/all/", response_model=List[LeaveInDB])
def get_all_leaves_for_year(year: int):
    """Get all leaves for a specific year (all months)"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT l.id, l.employee_id, l.leave_date, l.leave_type, l.reason, l.status, l.created_at, e.name as employee_name
            FROM leaves l
            JOIN employees e ON l.employee_id = e.id
            WHERE strftime('%Y', l.leave_date) = ?
            ORDER BY l.leave_date, e.name
        """, (str(year),))
        rows = cur.fetchall()
        return [LeaveInDB(
            id=r[0], employee_id=r[1], leave_date=r[2], leave_type=r[3], 
            reason=r[4], status=r[5], created_at=r[6]
        ) for r in rows]
    finally:
        cur.close()
        conn.close()

@app.get("/leaves/employee/{employee_id}/", response_model=List[LeaveInDB])
def get_leaves_for_employee(employee_id: str, year: Optional[int] = None):
    """Get all leaves for a specific employee, optionally filtered by year"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if year:
            cur.execute("""
                SELECT l.id, l.employee_id, l.leave_date, l.leave_type, l.reason, l.status, l.created_at, e.name as employee_name
                FROM leaves l
                JOIN employees e ON l.employee_id = e.id
                WHERE l.employee_id = ? AND strftime('%Y', l.leave_date) = ?
                ORDER BY l.leave_date DESC
            """, (employee_id, str(year)))
        else:
            cur.execute("""
                SELECT l.id, l.employee_id, l.leave_date, l.leave_type, l.reason, l.status, l.created_at, e.name as employee_name
                FROM leaves l
                JOIN employees e ON l.employee_id = e.id
                WHERE l.employee_id = ?
                ORDER BY l.leave_date DESC
            """, (employee_id,))
        rows = cur.fetchall()
        return [LeaveInDB(
            id=r[0], employee_id=r[1], leave_date=r[2], leave_type=r[3], 
            reason=r[4], status=r[5], created_at=r[6]
        ) for r in rows]
    finally:
        cur.close()
        conn.close()

@app.delete("/leaves/{leave_id}", status_code=204)
def delete_leave(leave_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM leaves WHERE id = ?", (leave_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Leave not found")
        conn.commit()
    finally:
        cur.close()
        conn.close()

# --- Attendance Endpoint (Updated Logic) ---
def get_attendance_by_month(year: int, month: int):
    """Fetches combined attendance, holiday, and leave data for a given month and year."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Get all employees
        cur.execute("SELECT id, name, joining_date FROM employees ORDER BY name")
        employees = {row[0]: row[1] for row in cur.fetchall()}
        joining_dates = {row[0]: row[2] for row in cur.fetchall()}

        # 2. Get all holidays in the month
        cur.execute("SELECT date, name FROM holidays WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?", (str(year), f"{month:02d}"))
        holidays = {datetime.strptime(row[0], '%Y-%m-%d').day: row[1] for row in cur.fetchall()}

        # 3. Get all leaves for the month
        cur.execute("""
            SELECT employee_id, leave_date
            FROM leaves 
            WHERE status = 'approved' AND strftime('%Y', leave_date) = ? AND strftime('%m', leave_date) = ?
        """, (str(year), f"{month:02d}"))
        leaves = defaultdict(set)
        for emp_id, leave_date_str in cur.fetchall():
            try:
                leaves[emp_id].add(datetime.strptime(leave_date_str, '%Y-%m-%d').day)
            except ValueError:
                continue

        # 4. Get all attendance records for the month
        cur.execute("""
            SELECT employee_id, date, check_in, check_out, status
            FROM attendance
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (str(year), f"{month:02d}"))
        attendance_records = defaultdict(dict)
        for emp_id, att_date_str, check_in_str, check_out_str, status in cur.fetchall():
            try:
                day = datetime.strptime(att_date_str, '%Y-%m-%d').day
            except ValueError:
                continue
            
            # Use 'P' for Present On Time, 'LT' for Late to avoid conflict with Leave 'L'
            day_status = "P" if status == "On Time" else "LT"
            
            punch_in = check_in_str
            if check_in_str and not isinstance(check_in_str, str):
                 punch_in = check_in_str.strftime('%I:%M %p')
            
            punch_out = check_out_str
            if check_out_str and not isinstance(check_out_str, str):
                 punch_out = check_out_str.strftime('%I:%M %p')

            attendance_records[emp_id][day] = {
                "status": day_status,
                "punch_in": punch_in,
                "punch_out": punch_out,
            }

        return employees, joining_dates, holidays, leaves, attendance_records
    finally:
        cur.close()
        conn.close()

@app.get("/attendance/{year}/{month}")
def get_monthly_attendance(year: int, month: int):
    """
    New function to get monthly attendance data, including holidays and weekend days.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Get all employees
        cur.execute("SELECT id, name, joining_date FROM employees")
        employees = cur.fetchall()
        employee_data = {name: emp_id for emp_id, name, _ in employees}
        joining_dates = {}
        for emp_id, _, joining_date_str in employees:
            if joining_date_str:
                try:
                    joining_dates[emp_id] = datetime.strptime(joining_date_str, '%Y-%m-%d').date()
                except ValueError:
                    joining_dates[emp_id] = None
            else:
                joining_dates[emp_id] = None

        # Get attendance for the month
        cur.execute("""
            SELECT employee_id, date, status, check_in, check_out
            FROM attendance
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (str(year), f"{month:02d}"))
        
        attendance_records = cur.fetchall()

        # Get holidays for the month
        cur.execute("""
            SELECT date, name
            FROM holidays
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ? AND type != 'WORKING_DAY'
        """, (str(year), f"{month:02d}"))
        holidays_records = cur.fetchall()
        holidays_records = cur.fetchall()
        holidays = {}
        for rec in holidays_records:
            try:
                d = datetime.strptime(rec[0], '%Y-%m-%d').day
                holidays[d] = rec[1]
            except ValueError:
                continue
        
        # Get converted working days for the month
        cur.execute("""
            SELECT date
            FROM holidays
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ? AND type = 'WORKING_DAY'
        """, (str(year), f"{month:02d}"))
        working_days_records = cur.fetchall()
        working_days_records = cur.fetchall()
        working_days = []
        for rec in working_days_records:
            try:
                working_days.append(datetime.strptime(rec[0], '%Y-%m-%d').day)
            except ValueError:
                continue

        # Get approved leaves for the month
        cur.execute("""
            SELECT employee_id, leave_date, leave_type, reason
            FROM leaves
            WHERE status = 'approved' AND strftime('%Y', leave_date) = ? AND strftime('%m', leave_date) = ?
        """, (str(year), f"{month:02d}"))
        leaves_records = cur.fetchall()
            
        # Create a mapping of employee leaves by day
        leaves_by_employee = defaultdict(dict)
        for emp_id, leave_date_str, leave_type, reason in leaves_records:
            emp_name = next((name for name, eid in employee_data.items() if eid == emp_id), None)
            if emp_name:
                try:
                    day = datetime.strptime(leave_date_str, '%Y-%m-%d').day
                    leaves_by_employee[emp_name][day] = {
                        "status": "L",
                        "leave_type": leave_type,
                        "reason": reason
                    }
                except ValueError:
                    continue

        # Process attendance data
        attendance_by_employee = defaultdict(dict)
        for emp_id, date_val_str, status, check_in_str, check_out_str in attendance_records:
            emp_name = next((name for name, eid in employee_data.items() if eid == emp_id), None)
            if emp_name:
                try:
                    date_val = datetime.strptime(date_val_str, '%Y-%m-%d').date()
                except ValueError:
                    continue

                # Only consider attendance on or after joining_date
                if joining_dates.get(emp_id) and date_val < joining_dates[emp_id]:
                    continue
                day = date_val.day
                
                # Parse check_in and check_out if they are strings
                punch_in = check_in_str
                if check_in_str and not isinstance(check_in_str, str):
                     punch_in = check_in_str.strftime('%H:%M:%S')
                
                punch_out_time = check_out_str
                if check_out_str and not isinstance(check_out_str, str):
                    punch_out_time = check_out_str.strftime('%H:%M:%S')

                attendance_by_employee[emp_name][day] = {
                    "status": status,
                    "punch_in": punch_in,
                    "punch_out": punch_out_time
                }
        
        # Add leave data to attendance
        for emp_name, leave_days in leaves_by_employee.items():
            emp_id = employee_data.get(emp_name)
            for day, leave_info in leave_days.items():
                d = date(year, month, day)
                if joining_dates.get(emp_id) and d < joining_dates[emp_id]:
                    continue
                if day not in attendance_by_employee[emp_name]:
                    attendance_by_employee[emp_name][day] = leave_info
        
        # Add holiday info to attendance data
        for day, name in holidays.items():
            for emp_name in employee_data.keys():
                emp_id = employee_data[emp_name]
                d = date(year, month, day)
                if joining_dates.get(emp_id) and d < joining_dates[emp_id]:
                    continue
                if day not in attendance_by_employee[emp_name]:
                    attendance_by_employee[emp_name][day] = {"status": "H", "holiday_name": name}

        _, days_in_month = calendar.monthrange(year, month)

        # Determine weekend days for the month
        weekend_days = []
        for day in range(1, days_in_month + 1):
            d = date(year, month, day)
            if d.weekday() >= 5: # Saturday or Sunday
                weekend_days.append(day)

        return {
            "attendance": attendance_by_employee,
            "employee_data": employee_data,
            "daysInMonth": days_in_month,
            "holidays": holidays,
            "weekend_days": weekend_days,
            "working_days": working_days
        }

    except Exception as e:
        print(f"[ERROR] Failed to get monthly attendance: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

@app.post("/punch_out")
def punch_out(req: PunchOutRequest):
    """Handle punch-out requests"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Import the function
    from database import punch_out_employee
    
    success = punch_out_employee(req.name, today)
    
    if success:
        return {"status": "success", "message": f"{req.name} punched out successfully."}
    else:
        # This could be because they already punched out or were never punched in.
        raise HTTPException(status_code=400, detail="Failed to punch out. Employee may not have punched in or has already punched out.")

@app.get("/api/landing-stats")
def get_landing_stats():
    """Get statistics for the landing page without affecting existing logic"""
    conn = get_db_connection()
    cur = conn.cursor()
    today_str = date.today().isoformat()

    try:
        # Total employees
        cur.execute("SELECT COUNT(*) as total FROM employees")
        result = cur.fetchone()
        total_employees = result[0] if result else 0

        # Present today (On Time)
        cur.execute("""
            SELECT COUNT(DISTINCT employee_id) as present
            FROM attendance
            WHERE date = ? AND status = 'On Time'
        """, (today_str,))
        result = cur.fetchone()
        present_today = result[0] if result else 0

        # Late today
        cur.execute("""
            SELECT COUNT(DISTINCT employee_id) as late
            FROM attendance
            WHERE date = ? AND status = 'Late'
        """, (today_str,))
        result = cur.fetchone()
        late_today = result[0] if result else 0

        # On leave today (from leaves table)
        # On leave today (from leaves table)
        cur.execute("""
            SELECT COUNT(DISTINCT employee_id) as on_leave
            FROM leaves
            WHERE leave_date = ? AND status = 'approved'
        """, (today_str,))
        result = cur.fetchone()
        on_leave = result[0] if result else 0

        # Recent entries (last 5)
        cur.execute("""
            SELECT e.name, a.check_in, a.status
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE a.date = ?
            ORDER BY a.check_in DESC
            LIMIT 5
        """, (today_str,))
        recent_entries = [
            {"name": row[0], "time": row[1], "status": row[2]}
            for row in cur.fetchall()
        ]

        return {
            "totalEmployees": total_employees,
            "presentToday": present_today,
            "lateToday": late_today,
            "onLeave": on_leave,
            "recentEntries": recent_entries
        }
    except Exception as e:
        print(f"[ERROR] Failed to get landing stats: {e}")
        return {
            "totalEmployees": 0,
            "presentToday": 0,
            "lateToday": 0,
            "onLeave": 0,
            "recentEntries": []
        }
    finally:
        cur.close()
        conn.close()

@app.get("/test_face_similarities")
def test_face_similarities():
    """Test endpoint to check face similarities between all registered faces"""
    try:
        from test_face_similarity import test_face_similarities
        
        # Capture the output
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        
        test_face_similarities()
        
        output = new_stdout.getvalue()
        sys.stdout = old_stdout
        
        return {"status": "success", "output": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/working-days/", response_model=HolidayInDB)
def create_working_day(working_day: WorkingDay):
    """Convert a weekend day to a working day by creating a negative holiday"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if the date is actually a weekend
        day_of_week = working_day.date.weekday()
        if day_of_week < 5:  # Monday = 0, Friday = 4
            raise HTTPException(status_code=400, detail="Can only convert weekends (Saturday/Sunday) to working days")
        
        # Check if there's already a holiday or working day for this date
        cur.execute("SELECT id, name FROM holidays WHERE date = ?", (working_day.date,))
        existing = cur.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail=f"Date {working_day.date} already has a holiday: {existing[1]}")
        
        # Create a working day entry (negative holiday)
        cur.execute("""
            INSERT INTO holidays (date, name, description, type, is_recurring)
            VALUES (?, ?, ?, ?, ?);
        """, (working_day.date, working_day.name, working_day.description, 'WORKING_DAY', False))
        
        new_id = cur.lastrowid
        conn.commit()
        
        return {
            "id": new_id,
            "date": working_day.date,
            "name": working_day.name,
            "description": working_day.description,
            "type": 'WORKING_DAY',
            "is_recurring": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create working day: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.get("/working-days/")
def get_working_days_for_year(year: int):
    """Get all working days (converted weekends) for a specific year"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, date, name, description, type, is_recurring
            FROM holidays
            WHERE type = 'WORKING_DAY' AND strftime('%Y', date) = ?
            ORDER BY date
        """, (str(year),))
        
        rows = cur.fetchall()
        working_days = [
            {
                "id": row[0],
                "date": row[1],
                "name": row[2],
                "description": row[3],
                "type": row[4],
                "is_recurring": row[5]
            }
            for row in rows
        ]
        
        return working_days
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch working days: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.delete("/working-days/{working_day_id}", status_code=204)
def delete_working_day(working_day_id: int):
    """Delete a working day (revert weekend)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if it's actually a working day
        cur.execute("SELECT id, name, type FROM holidays WHERE id = ?", (working_day_id,))
        holiday = cur.fetchone()
        
        if not holiday:
            raise HTTPException(status_code=404, detail="Working day not found")
        
        if holiday[2] != 'WORKING_DAY':
            raise HTTPException(status_code=400, detail="Can only delete working days (converted weekends)")
        
        cur.execute("DELETE FROM holidays WHERE id = ?", (working_day_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Working day not found")
            
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete working day: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.get('/office-settings')
def get_office_settings_api():
    settings = get_office_settings()
    if not settings:
        raise HTTPException(status_code=404, detail='Office settings not found')
    return settings

@app.put('/office-settings')
def update_office_settings_api(payload: dict):
    start_time = payload.get('start_time')
    end_time = payload.get('end_time')
    on_time_limit = payload.get('on_time_limit')
    if not (start_time and end_time and on_time_limit):
        raise HTTPException(status_code=400, detail='All fields are required')
    success = update_office_settings(start_time, end_time, on_time_limit)
    if not success:
        raise HTTPException(status_code=500, detail='Failed to update office settings')
    return {'message': 'Office settings updated successfully'}

@app.post("/api/export-attendance-csv")
def export_attendance_csv(
    filters: dict = Body(...)
):
    """
    Export attendance as CSV with advanced filters and layout options.
    filters: {
        year: int,
        month: Optional[int],
        date_start: Optional[str],
        date_end: Optional[str],
        department: Optional[str],
        employee_type: Optional[str],
        status: Optional[list],
        layout: str,  # 'employees-as-columns' or 'dates-as-columns'
        fields: dict  # {name: bool, id: bool, department: bool, type: bool, status: bool}
    }
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        year = filters.get('year')
        month = filters.get('month')
        date_start = filters.get('date_start')
        date_end = filters.get('date_end')
        department = filters.get('department')
        employee_type = filters.get('employee_type')
        status_filter = filters.get('status')
        layout = filters.get('layout', 'employees-as-columns')
        fields = filters.get('fields', {"name": True, "id": True, "department": False, "type": False, "status": True})
        gender = filters.get('gender')

        # Get employees with optional department/type/gender filter
        emp_query = "SELECT id, name, department, employee_type, gender, joining_date FROM employees"
        emp_params = []
        where_clauses = []
        if department:
            where_clauses.append("department = ?")
            emp_params.append(department)
        if employee_type:
            where_clauses.append("employee_type = ?")
            emp_params.append(employee_type)
        if gender:
            where_clauses.append("gender = ?")
            emp_params.append(gender)
        if where_clauses:
            emp_query += " WHERE " + " AND ".join(where_clauses)
        emp_query += " ORDER BY name"
        cur.execute(emp_query, tuple(emp_params))
        employees = cur.fetchall()
        employee_map = {row[1]: row for row in employees}  # name: (id, name, department, type, joining_date)
        employee_ids = [row[0] for row in employees]

        # Determine date range
        if date_start and date_end:
            start_date = datetime.strptime(date_start, "%Y-%m-%d").date()
            end_date = datetime.strptime(date_end, "%Y-%m-%d").date()
        elif year and month:
            start_date = date(year, month, 1)
            _, days_in_month = calendar.monthrange(year, month)
            end_date = date(year, month, days_in_month)
        elif year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
        else:
            raise HTTPException(status_code=400, detail="Must provide year or date range")

        # Get attendance records in range
        cur.execute(
            """
            SELECT employee_id, date, status
            FROM attendance
            WHERE date >= ? AND date <= ?
            """,
            (start_date, end_date)
        )
        attendance_records = cur.fetchall()
        # Map: (emp_id, date) -> status
        att_map = {(row[0], row[1]): row[2] for row in attendance_records}

        # Get leaves in range
        cur.execute(
            """
            SELECT employee_id, leave_date
            FROM leaves
            WHERE leave_date >= ? AND leave_date <= ? AND status = 'approved'
            """,
            (start_date, end_date)
        )
        leave_records = cur.fetchall()
        leave_map = {(row[0], row[1]): 'L' for row in leave_records}

        # Get holidays in range
        cur.execute(
            """
            SELECT date, name
            FROM holidays
            WHERE date >= ? AND date <= ? AND type != 'WORKING_DAY'
            """,
            (start_date, end_date)
        )
        holiday_records = cur.fetchall()
        holiday_map = {row[0]: row[1] for row in holiday_records}

        # Build list of all days in range
        all_dates = []
        d = start_date
        while d <= end_date:
            all_dates.append(d)
            d += timedelta(days=1)

        # Parse joining dates to date objects
        joining_dates = {}
        for row in employees:
            emp_id = row[0]
            joining_date_str = row[5]  # joining_date is at index 5
            if joining_date_str:
                try:
                    joining_dates[emp_id] = datetime.strptime(joining_date_str, '%Y-%m-%d').date()
                except ValueError:
                    joining_dates[emp_id] = None
            else:
                joining_dates[emp_id] = None

        # Filter employees by status if needed (status filter is for attendance status, e.g. Present, Absent, etc.)
        filtered_employees = employees
        if status_filter:
            filtered_employees = []
            for row in employees:
                emp_id = row[0]
                for d in all_dates:
                    s = att_map.get((emp_id, d)) or leave_map.get((emp_id, d)) or (holiday_map.get(d) and 'H')
                    if s and s in status_filter:
                        filtered_employees.append(row)
                        break
        # Prepare CSV
        output = io.StringIO()
        writer = csv.writer(output)
        if layout == 'employees-as-columns':
            # Header: Name + all dates
            header = ['Employee Name'] + [d.strftime('%Y-%m-%d') for d in all_dates]
            writer.writerow(header)
            for row in filtered_employees:
                emp_id, name, dept, etype, gender, joining_date_str = row
                joining_date = joining_dates.get(emp_id)
                rowdata = [name]
                for d in all_dates:
                    cell_status = ''
                    if joining_date and d < joining_date:
                        cell_status = ''
                    else:
                        s = att_map.get((emp_id, d)) or leave_map.get((emp_id, d)) or (holiday_map.get(d) and 'H')
                        if s:
                            cell_status = s
                        else:
                            # If no status, mark as Absent or Holiday as per frontend logic
                            if holiday_map.get(d):
                                cell_status = 'H'
                            else:
                                cell_status = 'A'
                        # If this date is the joining_date, append (Joining Day)
                        if joining_date and d == joining_date:
                            cell_status = f"{cell_status} (Joining Day)"
                    rowdata.append(cell_status)
                writer.writerow(rowdata)
        else:  # dates-as-columns
            # Header: Date + all employees
            header = ['Date'] + [row[1] for row in filtered_employees]
            writer.writerow(header)
            for d in all_dates:
                rowdata = [d.strftime('%Y-%m-%d')]
                for row in filtered_employees:
                    emp_id = row[0]
                    joining_date = joining_dates.get(emp_id)
                    cell_status = ''
                    if joining_date and d < joining_date:
                        cell_status = ''
                    else:
                        s = att_map.get((emp_id, d)) or leave_map.get((emp_id, d)) or (holiday_map.get(d) and 'H')
                        if s:
                            cell_status = s
                        else:
                            if holiday_map.get(d):
                                cell_status = 'H'
                            else:
                                cell_status = 'A'
                        if joining_date and d == joining_date:
                            cell_status = f"{cell_status} (Joining Day)"
                    rowdata.append(cell_status)
                writer.writerow(rowdata)
        output.seek(0)
        filename = f"attendance_export_{year or ''}_{month or ''}.csv"
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
