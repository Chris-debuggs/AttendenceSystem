# Face Recognition Attendance System - Backend

This backend system now stores face embeddings and images directly in the PostgreSQL database instead of using files. This ensures that when employees are deleted or edited from the frontend, their face data is also properly managed.

## Features

- **Database-based face storage**: Face embeddings and images are stored in PostgreSQL
- **Automatic face data management**: Face data is automatically deleted when employees are removed
- **Face data updates**: Face embeddings are updated when employee photos are changed
- **Attendance tracking**: All attendance records are stored in the database
- **Duplicate face detection**: Prevents registering the same face multiple times

## Database Schema

### Employees Table
```sql
CREATE TABLE employees (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    photo_data BYTEA,           -- Raw image data
    face_embedding BYTEA,       -- Pickled face embedding
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) REFERENCES employees(id),
    check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_out TIMESTAMP,
    date DATE DEFAULT CURRENT_DATE
);
```

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database**:
   - Make sure PostgreSQL is running
   - Create a database named `attendance_db`
   - Update database connection in `database.py` if needed

3. **Initialize database**:
   ```bash
   python init_db.py
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Employee Management
- `POST /register_face` - Register a new employee with face data
- `POST /employees/` - Create employee (without face data)
- `GET /employees/` - Get all employees
- `PUT /employees/{emp_id}` - Update employee information
- `DELETE /employees/{emp_id}` - Delete employee (includes face data)

### Face Data Management
- `GET /employees/{emp_id}/photo` - Get employee photo from database
- `PUT /employees/{emp_id}/photo` - Update employee photo and face embedding

### Attendance
- `POST /mark_attendance` - Mark attendance using face recognition

## Key Changes from File-based System

1. **No more file dependencies**: Face images and embeddings are stored in the database
2. **Automatic cleanup**: When an employee is deleted, their face data is automatically removed
3. **Consistent data**: All employee data (including face data) is managed in one place
4. **Better scalability**: Database storage is more scalable than file-based storage

## Face Recognition Process

1. **Registration**: 
   - Employee photo is captured
   - Face is detected and embedding is extracted
   - Embedding and image are stored in database
   - Duplicate face check is performed against existing embeddings

2. **Recognition**:
   - Face embedding is extracted from captured image
   - Compared against all stored embeddings in database
   - Best match above threshold is returned
   - Attendance is logged in database

## Error Handling

- **Duplicate faces**: System prevents registering the same face multiple times
- **No face detected**: Returns appropriate error message
- **Database errors**: Proper rollback and error messages
- **Invalid images**: Validation for image format and quality

## Security Considerations

- Face embeddings are stored as binary data in the database
- Images are stored as raw bytes
- Database connection uses proper authentication
- Input validation for all API endpoints