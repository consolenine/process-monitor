# Machine Snapshot Monitoring Backend

This project provides a Django-based backend system for collecting, storing, and broadcasting machine snapshot data in real-time. Agents (clients) can send snapshot data including system configuration and process information. Snapshots are stored in the database and broadcasted over WebSockets to subscribed frontend clients.

## Features

- Receive snapshot data via POST requests.
- Store snapshots of system metrics and running processes.
- WebSocket-based real-time updates per machine.
- RESTful API endpoints for querying snapshot history.
- Filtering by machine, time range (last hour, 3 hours, day), etc.
- Dynamic inclusion/exclusion of process data.
- Patchable configuration (polling interval, enabled flag).

---

## Tech Stack

- **Backend:** Django, Django REST Framework, Django Channels
- **WebSocket Layer:** Channels (in-memory layer)
- **Database:** SQLite (or configure your preferred DB)
- **Frontend Integration:** Compatible with any frontend using AJAX/WebSockets (e.g., jQuery, React, Vue)

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- pipenv or virtualenv (recommended)

### Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create .env using .env.example
Copy the `.env.example` file to `.env` and update the values as needed.

```bash
cp .env.example .env
```

### Database Migrations

```bash
cd backend && python manage.py migrate
```

### Run the Server

```bash
cd backend && python manage.py runserver
```

## Frontend Setup

### NPM Dependencies

```bash
cd ui && npm install
```

### Run Development Server
```bash
cd ui && npm run dev
```

## Agent Build Instructions

```bash
cd agent && pyinstaller --onefile run.py --name ProcessMonitorAgent
```

## Further scopes

Some features, I wanted to implement but couldn't due to time constraints:

- **Authentication:** Implement user authentication for secure access to the API.
- **Authorization:** Role-based access control for different user roles (admin, user).
- **Data Visualization:** Charting can be done using historical data from API.
- **Testing:** Unit tests for API endpoints and WebSocket connections (using pyTest).
- Rewrite frontend with React for better performance.