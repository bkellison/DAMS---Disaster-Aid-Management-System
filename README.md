# DAMS - Disaster Aid Management System

## Overview
DAMS is a web application designed to coordinate disaster relief efforts by connecting donors with recipients, managing aid requests and pledges, and facilitating efficient resource allocation during crisis events.

**Live Application**: [https://dams-disaster-aid-management-system.netlify.app](https://dams-disaster-aid-management-system.netlify.app)

## Core Features

### User Management
- Multi-role authentication system (Admin, Admin Observer, Donor, Recipient)
- JWT-based security with role-based access control
- User registration and approval workflow

### Event & Inventory Management
- Disaster event creation with geographic tracking
- Comprehensive item catalog organized by categories
- Real-time inventory tracking combining admin stock and donor pledges

### Request & Pledge System
- Request creation by recipients with specific needs
- Pledge management by donors with shipping timelines
- Progress tracking and status management

### Matching System
- Manual matching interface for precise control
- Automated matching algorithms:
  - Geographic proximity-based matching
  - Shipping time optimization
  - Quantity optimization for resource efficiency
- Combined inventory allocation (admin stock + donor pledges)

### Shipping & Logistics
- Comprehensive tracking system with status updates
- Multi-status workflow: Pending → Shipped → Delivered
- Role-based shipping permissions

## Technology Stack

**Backend**: Flask (Python), MySQL, JWT Authentication  
**Frontend**: Vue.js 3, Pinia State Management, Vue Router  
**External APIs**: ZipCodeBase for distance calculations  
**Deployment**: Railway (Backend), Netlify (Frontend)

## Database Architecture
- **dr_admin**: User management, authentication, responses
- **dr_events**: Events, items, requests, pledges, matches

## User Roles & Permissions

| Role | Create Events | Manage Pledges | Create Requests | Matching | Shipping |
|------|---------------|----------------|-----------------|----------|----------|
| Admin | Yes | Yes | Yes | Yes | Full Access |
| Admin Observer | No | View Only | View Only | View Only | View Only |
| Donor | No | Yes | Yes | No | Can Ship |
| Recipient | No | No | Yes | No | Can Confirm Delivery |

## License
This project is currently unlicensed.
