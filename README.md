# DAMS - Disaster Aid Management System

## Overview
DAMS is a web application designed to coordinate disaster relief efforts by connecting donors with recipients, managing aid requests/pledges, tracking shipments, and facilitating resource allocation during crisis events.

## Features
- **User Role Management**: Admin, Donor, and Recipient roles with different permissions
- **Disaster Event Creation**: Create and manage disaster events
- **Inventory Management**: Track donations and aid items
- **Request System**: Recipients can request specific items needed
- **Matching Algorithms**: Both manual and automated matching between pledges and requests
- **Shipping Tracking**: Monitor the status of aid shipments

## Technology Stack
- **Backend**: Flask (Python), MySQL
- **Frontend**: Vue.js
- **Authentication**: JWT

## Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Node.js and npm

### Backend Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure your database in `config.py`
6. Run the server: `python runserver.py`

### Frontend Setup
1. Navigate to the frontend directory
2. Install dependencies: `npm install`
3. Run development server: `npm run dev`

## License
This project is currently unlicensed.
