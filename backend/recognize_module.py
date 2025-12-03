# recognize_module.py

import cv2
import pickle
import numpy as np
from datetime import datetime
from insightface.app import FaceAnalysis
import os
from database import get_db_connection, get_all_face_embeddings, get_office_settings, get_employee_email
import smtplib
from email.mime.text import MIMEText

# Lower threshold for better recognition with variations
THRESHOLD = 0.6  # Reduced from 0.8 to handle masks, rotation, etc.

# InsightFace setup
app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    # Normalize vectors for proper cosine similarity
    norm_a = a / np.linalg.norm(a)
    norm_b = b / np.linalg.norm(b)
    return np.dot(norm_a, norm_b)

def preprocess_image_for_recognition(image_np):
    processed_images = [image_np]
    # Only a few essential variations for speed
    for angle in [-10, 10]:
        height, width = image_np.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image_np, rotation_matrix, (width, height))
        processed_images.append(rotated)
    for scale in [0.95, 1.05]:
        height, width = image_np.shape[:2]
        new_height, new_width = int(height * scale), int(width * scale)
        resized = cv2.resize(image_np, (new_width, new_height))
        start_y = max(0, (new_height - height) // 2)
        start_x = max(0, (new_width - width) // 2)
        cropped = resized[start_y:start_y + height, start_x:start_x + width]
        processed_images.append(cropped)
    return processed_images

def recognize_face_with_variations(embedding):
    """Enhanced face recognition that tries multiple variations"""
    # Get embeddings from database
    db = get_all_face_embeddings()
    if not db:
        print("[DEBUG] No face embeddings found in database")
        return None, 0
    
    embeddings_list = list(db.values())
    names_list = list(db.keys())
    
    print(f"[DEBUG] Comparing against {len(names_list)} registered faces: {names_list}")
    
    # Calculate cosine similarities
    similarities = []
    for stored_embedding in embeddings_list:
        similarity = cosine_similarity(embedding, stored_embedding)
        similarities.append(similarity)
    
    similarities = np.array(similarities)
    best_match_index = np.argmax(similarities)
    best_score = similarities[best_match_index]
    best_name = names_list[best_match_index]
    
    print(f"[DEBUG] Best match: {best_name} with score: {best_score:.4f} (threshold: {THRESHOLD})")
    
    if best_score > THRESHOLD:
        print(f"[DEBUG] Face recognized as: {best_name}")
        return best_name, best_score
    else:
        print(f"[DEBUG] Face not recognized - best score {best_score:.4f} below threshold {THRESHOLD}")
        return None, 0

def recognize_face(embedding):
    """Legacy function for backward compatibility"""
    return recognize_face_with_variations(embedding)

def get_attendance_status(employee_name: str, date: str):
    """Check if attendance exists and if punch-out has occurred."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT check_in, check_out FROM attendance 
            WHERE employee_id = (SELECT id FROM employees WHERE name = ?) 
            AND date = ?
        """, (employee_name, date))
        result = cur.fetchone()
        print(f"[DEBUG] Database query result for {employee_name} on {date}: {result}")
        if result:
            status = {"checked_in": True, "checked_out": result[1] is not None}
            print(f"[DEBUG] Attendance status for {employee_name}: {status}")
            return status
        print(f"[DEBUG] No attendance record found for {employee_name} on {date}")
        return {"checked_in": False, "checked_out": False}
    except Exception as e:
        print(f"Error checking attendance status: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def log_attendance(employee_name: str, status: str):
    """Log attendance in the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO attendance (employee_id, check_in, status, date)
            VALUES ((SELECT id FROM employees WHERE name = ?), CURRENT_TIMESTAMP, ?, CURRENT_DATE)
        """, (employee_name, status))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging attendance: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def recognize_and_log_image(image_np: np.ndarray):
    """Enhanced recognition with multiple attempts and variations"""
    print("[DEBUG] Starting enhanced face recognition...")
    
    # Try original image first
    faces = app.get(image_np)
    if faces:
        face = faces[0]
        emb = face.embedding
        name, score = recognize_face_with_variations(emb)
        
        if name:
            return process_attendance(name, score)
        else:
            # Face detected, but not recognized
            return {"name": None, "message": "Unknown Face - Please register first", "status": "Unknown"}
    
    # If original failed, try preprocessed variations
    print("[DEBUG] Original image failed, trying variations...")
    processed_images = preprocess_image_for_recognition(image_np)
    face_found = False
    for i, processed_img in enumerate(processed_images):
        try:
            faces = app.get(processed_img)
            if faces:
                face_found = True
                face = faces[0]
                emb = face.embedding
                name, score = recognize_face_with_variations(emb)
                if name:
                    return process_attendance(name, score)
                else:
                    # Face detected, but not recognized
                    return {"name": None, "message": "Unknown Face - Please register first", "status": "Unknown"}
        except Exception as e:
            print(f"[DEBUG] Variation {i} failed: {e}")
            continue
    if not face_found:
        print("[DEBUG] No face detected in any variation.")
        return {"name": None, "message": "No face detected. Please try again.", "status": "No Face"}

def process_attendance(name: str, score: float):
    """Process attendance for recognized employee"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    print(f"[DEBUG] Employee {name} detected on {today} with confidence: {score:.4f}")
    attendance_status = get_attendance_status(name, today)
    print(f"[DEBUG] Attendance status: {attendance_status}")

    # Fetch on_time_limit from office_settings
    settings = get_office_settings()
    if settings and settings.get('on_time_limit'):
        on_time_limit = datetime.strptime(settings['on_time_limit'], "%H:%M:%S").time()
    else:
        on_time_limit = datetime.strptime("09:30:00", "%H:%M:%S").time()  # fallback

    if attendance_status and attendance_status["checked_in"]:
        print(f"[DEBUG] {name} is checked in.")
        if attendance_status["checked_out"]:
            print(f"[DEBUG] {name} is already checked out.")
            message = f"{name}: Already punched out for the day."
            status = "Already Punched Out"
            print(f"[DEBUG] Employee already punched out")
            # Send punch-out email
            email = get_employee_email(name)
            if email:
                send_email(
                    email,
                    f"Punch Out Confirmation - {today}",
                    f"Hello {name},\n\nYou have successfully punched out at {now.strftime('%H:%M:%S')} on {today}.\n\nStatus: Punched Out\n\nThank you."
                )
        else:
            print(f"[DEBUG] {name} is checked in but not checked out. Should show punch out modal.")
            message = f"Welcome, {name}! Punch out?"
            status = "Already Marked"
            print(f"[DEBUG] Employee checked in but not out - showing punch-out modal")
    else:
        print(f"[DEBUG] {name} is not checked in today. Logging new check-in.")
        current_time = now.time()
        check_in_status = "Late" if current_time > on_time_limit else "On Time"
        print(f"[DEBUG] New check-in for {name} - status: {check_in_status}")
        if log_attendance(name, check_in_status):
            message = f"{name}: Attendance marked ({check_in_status})"
            status = "Success"
            print(f"[DEBUG] Check-in logged successfully")
            # Send punch-in email
            email = get_employee_email(name)
            if email:
                send_email(
                    email,
                    f"Punch In Confirmation - {today}",
                    f"Hello {name},\n\nYou have successfully punched in at {now.strftime('%H:%M:%S')} on {today}.\n\nStatus: {check_in_status}\n\nThank you."
                )
        else:
            message = f"{name}: Error logging attendance"
            status = "Error"
            print(f"[DEBUG] Error logging check-in")

    print(f"[DEBUG] Returning: name={name}, message={message}, status={status}")
    return {"name": name, "message": message, "status": status}

def send_email(to_email, subject, body):
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER', 'your@email.com')
    smtp_password = os.environ.get('SMTP_PASSWORD', 'yourpassword')
    from_email = smtp_user
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [to_email], msg.as_string())
        print(f"[EMAIL] Sent to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
