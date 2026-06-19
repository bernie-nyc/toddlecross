# Toddlecross

Toddlecross is a Python-based platform featuring a web frontend gated by Google SSO. It includes an administrative account tied to the instance for account administration, and is designed for work, data generation, integration, and processing utilizing Python as the core runtime.

## Project Structure

- `config/`: Django project configuration
- `toddlecross/`: Main Django application for UI, integrations, and core logic
- `requirements.txt`: Python pip package dependencies
- `.env.example`: Template for environment variables (copy to `.env` locally)

## Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/bernie-nyc/toddlecross.git
   cd toddlecross
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in the values:
   ```bash
   copy .env.example .env
   ```

5. **Run Migrations and Create Admin**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
