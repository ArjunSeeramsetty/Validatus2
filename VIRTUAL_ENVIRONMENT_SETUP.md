# Virtual Environment Setup Guide

## Overview
This guide provides instructions for setting up a Python virtual environment for the Validatus platform to avoid dependency conflicts.

## Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Create Virtual Environment
```bash
# Navigate to the project directory
cd Validatus2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies (if needed)
cd ../frontend
npm install
```

### 3. Environment Configuration
Create a `.env` file in the backend directory with the following variables:
```env
ENVIRONMENT=development
LOCAL_DEVELOPMENT_MODE=true
GCP_PROJECT_ID=validatus-platform
GCP_REGION=us-central1
```

### 4. Verify Installation
```bash
# Test backend startup
cd backend
python -m app.main

# Test frontend (if applicable)
cd frontend
npm run dev
```

## Deactivation
To deactivate the virtual environment:
```bash
deactivate
```

## Troubleshooting
- If you encounter permission errors, try running as administrator
- For dependency conflicts, consider using `pip install --force-reinstall`
- Ensure Python version compatibility with all packages