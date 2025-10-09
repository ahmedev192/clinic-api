"""
Setup script for Clinic Management System - Staff Module
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🏥 Clinic Management System - Staff Module Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command("python -m venv venv", "Virtual environment creation"):
            sys.exit(1)
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
        python_command = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
        python_command = "venv/bin/python"
    
    # Install requirements
    print("Installing requirements...")
    if not run_command(f"{pip_command} install -r requirements.txt", "Requirements installation"):
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        with open(".env", "w") as f:
            f.write("SECRET_KEY=django-insecure-change-this-in-production\n")
            f.write("DEBUG=True\n")
            f.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
        print("✓ .env file created")
    
    # Run migrations
    print("Running database migrations...")
    if not run_command(f"{python_command} manage.py makemigrations", "Make migrations"):
        sys.exit(1)
    
    if not run_command(f"{python_command} manage.py migrate", "Apply migrations"):
        sys.exit(1)
    
    # Create superuser (optional)
    print("\n" + "=" * 50)
    print("Setup completed successfully! 🎉")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Create a superuser:")
    print(f"   {python_command} manage.py createsuperuser")
    
    print("\n3. Seed initial data (optional):")
    print(f"   {python_command} manage.py seed_data")
    
    print("\n4. Run development server:")
    print(f"   {python_command} manage.py runserver")
    
    print("\n5. Access the application:")
    print("   - API Documentation: http://localhost:8000/api/docs/")
    print("   - Admin Panel: http://localhost:8000/admin/")
    
    print("\n" + "=" * 50)
    print("For more information, see README.md")


if __name__ == "__main__":
    main()
