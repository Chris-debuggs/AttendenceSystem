import os
import cv2
import base64
import pickle
import numpy as np
import mediapipe as mp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from database import get_db_connection, save_face_data, get_all_face_embeddings

# Initialize router
router = APIRouter()

# Initialize InsightFace
embedder = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
embedder.prepare(ctx_id=0, det_size=(640, 640))

# Initialize MediaPipe face detection
mp_face_detection = mp.solutions.face_detection

# Similarity threshold for face comparison
SIMILARITY_THRESHOLD = 0.7  # Slightly reduced for better registration

# Request model
class RegisterRequest(BaseModel):
    id: str
    name: str
    email: str
    mobile_no: str
    address: str
    gender: str
    department: str
    position: str
    salary: float
    working_hours_per_day: float
    employee_type: str
    joining_date: str  # <-- Add this line (as string for date input)
    image_base64: str  # base64 string without the prefix

class ValidateFaceRequest(BaseModel):
    image_base64: str

def create_robust_embedding(frame):
    embeddings = []
    faces = embedder.get(frame)
    if faces:
        embeddings.append(faces[0].normed_embedding)
    for angle in [-10, 10]:
        height, width = frame.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(frame, rotation_matrix, (width, height))
        faces = embedder.get(rotated)
        if faces:
            embeddings.append(faces[0].normed_embedding)
    for scale in [0.95, 1.05]:
        height, width = frame.shape[:2]
        new_height, new_width = int(height * scale), int(width * scale)
        resized = cv2.resize(frame, (new_width, new_height))
        start_y = max(0, (new_height - height) // 2)
        start_x = max(0, (new_width - width) // 2)
        cropped = resized[start_y:start_y + height, start_x:start_x + width]
        faces = embedder.get(cropped)
        if faces:
            embeddings.append(faces[0].normed_embedding)
    if not embeddings:
        raise Exception("Could not extract any embeddings from the image")
    avg_embedding = np.mean(embeddings, axis=0)
    avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
    print(f"[DEBUG] Created robust embedding from {len(embeddings)} variations")
    return avg_embedding

def check_similar_face(embedding):
    """Check if the face embedding is similar to any existing face in the database"""
    try:
        # Get all existing face embeddings
        existing_embeddings = get_all_face_embeddings()
        
        if not existing_embeddings:
            print("[DEBUG] No existing faces in database to compare against")
            return None, 0
        
        print(f"[DEBUG] Checking against {len(existing_embeddings)} existing faces")
        
        # Calculate similarities with existing faces
        similarities = []
        names = []
        
        for name, stored_embedding in existing_embeddings.items():
            # Normalize embeddings for proper cosine similarity
            norm_embedding = embedding / np.linalg.norm(embedding)
            norm_stored = stored_embedding / np.linalg.norm(stored_embedding)
            similarity = np.dot(norm_embedding, norm_stored)
            
            similarities.append(similarity)
            names.append(name)
            
            print(f"[DEBUG] Similarity with {name}: {similarity:.4f}")
        
        # Find the best match
        best_index = np.argmax(similarities)
        best_similarity = similarities[best_index]
        best_name = names[best_index]
        
        print(f"[DEBUG] Best match: {best_name} with similarity: {best_similarity:.4f}")
        
        if best_similarity > SIMILARITY_THRESHOLD:
            return best_name, best_similarity
        else:
            return None, best_similarity
            
    except Exception as e:
        print(f"[ERROR] Error checking similar faces: {e}")
        return None, 0

@router.post("/register_face")
def register_face(request: RegisterRequest):
    emp_id = request.id
    emp_name = request.name.strip().replace(" ", "_")
    print(f"[DEBUG] Attempting to register employee with ID: {emp_id} and Name: {request.name}")

    if not emp_id or not request.name:
        raise HTTPException(status_code=400, detail="Employee ID and Name cannot be empty.")

    try:
        image_data = base64.b64decode(request.image_base64)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decode image.")

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image data.")

    # Face detection
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.6) as face_detection:
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results.detections:
            raise HTTPException(status_code=400, detail="No face detected.")

    # Create robust embedding from multiple variations
    try:
        embedding = create_robust_embedding(frame)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract embedding: {str(e)}")

    # Check for similar faces before registration
    print(f"[DEBUG] Checking for similar faces before registration...")
    similar_name, similarity_score = check_similar_face(embedding)
    
    if similar_name:
        raise HTTPException(
            status_code=400, 
            detail=f"Face is too similar to existing employee '{similar_name}' (similarity: {similarity_score:.4f}). Please use a different photo or contact admin if this is an error."
        )

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Step 1: Check if employee with this ID already exists
        cur.execute("SELECT name FROM employees WHERE id = ?", (emp_id,))
        existing_employee = cur.fetchone()
        if existing_employee:
            raise HTTPException(status_code=400, detail=f"Employee with ID '{emp_id}' already exists (Name: {existing_employee[0]}).")

        # Step 2: Insert the new employee record
        print(f"[DEBUG] Inserting new employee record for ID: {emp_id}")
        cur.execute("""
            INSERT INTO employees (id, name, email, mobile_no, address, gender, department, position, salary, working_hours_per_day, employee_type, joining_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (emp_id, request.name, request.email, request.mobile_no, request.address, request.gender, request.department, request.position, request.salary, request.working_hours_per_day, request.employee_type, request.joining_date))
        
        # Step 3: Save face embedding and image data
        print(f"[DEBUG] Saving face data for ID: {emp_id}")
        embedding_bytes = pickle.dumps(embedding)
        cur.execute("""
            UPDATE employees 
            SET face_embedding = ?, photo_data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (embedding_bytes, image_data, emp_id))

        conn.commit()
        print(f"[SUCCESS] Successfully registered employee '{request.name}' with ID '{emp_id}'.")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Transaction failed for employee ID {emp_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {e}")
    finally:
        cur.close()
        conn.close()

    return {
        "status": "success",
        "message": f"Face of '{request.name}' registered successfully with robust embedding.",
        "employee_id": emp_id
    }

@router.post("/validate_face")
def validate_face_uniqueness(request: ValidateFaceRequest):
    """
    Validates a face image to ensure it's not too similar to any existing face.
    This does NOT save any data. It's a pre-check before registration.
    """
    try:
        image_data = base64.b64decode(request.image_base64)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decode image.")

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image data.")
        
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.6) as face_detection:
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results.detections:
            raise HTTPException(status_code=400, detail="No face detected in the image.")

    try:
        embedding = create_robust_embedding(frame)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract face embedding: {str(e)}")

    similar_name, similarity_score = check_similar_face(embedding)
    
    if similar_name:
        raise HTTPException(
            status_code=400, 
            detail=f"Face is too similar to an existing employee '{similar_name}' (similarity: {similarity_score:.4f})."
        )

    return {"status": "success", "message": "Face is unique and valid for registration."}
