# Attendance System Frontend

Modern face recognition-based attendance tracking system built with React + Vite.

## Features

### 🎯 Welcome Page
- **Live Camera Feed**: Real-time face detection and recognition
- **Automatic Attendance Marking**: Face recognition integration with backend API
- **Welcome Messages**: Personalized greetings for recognized employees
- **Live Stats Dashboard**: Today's attendance overview
- **Punch Out**: Option for employees to mark their departure

### 🔐 Admin Panel
- **Dashboard**: Overview of today's attendance with quick action cards
- **Employee Management**: Complete CRUD operations for employee records including photo capture
- **Attendance Tracking**: Monthly calendar view with color-coded attendance status
- **Holiday Management**: Add/remove holidays and convert weekends to working days
- **Leave Management**: Track and manage employee leaves
- **Payroll**: Automated salary calculations based on attendance
- **Settings**: Configure office hours, on-time limits, and admin credentials

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **Axios** - HTTP client for API calls
- **Vanilla CSS** - Modern styling with CSS custom properties

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

The app will run on `http://localhost:5173`

## Default Credentials

Admin login credentials (set in backend):
- Username: admin
- Password: admin

## API Endpoints Used

- `POST /mark_attendance` - Face recognition and attendance marking
- `GET /api/landing-stats` - Dashboard statistics
- `POST /login` - Admin authentication
- `GET /employees/` - List employees
- `POST /employees/` - Create employee
- `PUT /employees/{id}` - Update employee
- `DELETE /employees/{id}` - Delete employee
- `PUT /employees/{id}/photo` - Upload employee photo
- `GET /attendance/{year}/{month}` - Monthly attendance
- `POST /api/export-attendance-csv` - Export attendance to CSV
- `GET /holidays/?year={year}` - Get holidays
- `POST /holidays/` - Create holiday
- `DELETE /holidays/{id}` - Delete holiday
- `GET /leaves/?year={year}&month={month}` - Get leaves
- `POST /leaves/` - Create leave
- `DELETE /leaves/{id}` - Delete leave
- `GET /office-settings` - Get office configuration
- `PUT /office-settings` - Update office settings
- `PUT /admin/credentials` - Update admin credentials
- `POST /punch_out` - Employee punch out

## Project Structure

```
frontend/
├── public/               # Static assets
├── src/
│   ├── assets/          # Images and media
│   ├── components/      # Reusable components
│   │   ├── Toast.jsx
│   │   ├── ConfirmationModal.jsx
│   │   ├── PunchOutModal.jsx
│   │   └── CaptureModal.jsx
│   ├── context/         # React contexts
│   │   ├── ThemeContext.jsx
│   │   └── ToastContext.jsx
│   ├── pages/           # Page components
│   │   ├── WelcomePage.jsx          # Main landing with camera
│   │   ├── LoginPage.jsx            # Admin login
│   │   ├── DashboardPage.jsx        # Admin dashboard
│   │   ├── AddRemoveEmployeePage.jsx
│   │   ├── AttendanceDashboardPage.jsx
│   │   ├── HolidayManagement.jsx
│   │   ├── LeaveManagement.jsx
│   │   ├── PayrollPage.jsx
│   │   └── SettingsPage.jsx
│   ├── App.jsx          # Main app component with routing
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── package.json
└── vite.config.js
```

## Design Features

### Modern Dark Theme
- Professional color palette with accent colors
- Glassmorphism effects for modern look
- Smooth animations and transitions
- Responsive design for all screen sizes

### User Experience
- Real-time updates and notifications
- Loading states for async operations
- Toast notifications for user feedback
- Confirmation modals for destructive actions
- Sticky table headers for better navigation

## Camera Permissions

The welcome page requires camera access for face recognition. Make sure to:
1. Allow camera permissions when prompted
2. Use HTTPS or localhost (required for camera access)
3. Ensure proper lighting for better face detection

## Development Notes

- API calls are made to `http://localhost:8000` by default
- Authentication state is stored in localStorage
- Theme preference is persisted across sessions
- All dates are handled in YYYY-MM-DD format
- Protected routes redirect to login if not authenticated

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT
