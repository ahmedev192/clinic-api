"""
Startup script for the Clinic Appointments & Scheduling system.

This script handles initial setup and starts the Django development server.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main startup function."""
    print("🏥 Starting Clinic Appointments & Scheduling System")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Linux/Mac
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements"):
        print("⚠️  Warning: Failed to install some requirements. Continuing anyway...")
    
    # Run migrations
    if not run_command(f"{python_cmd} manage.py makemigrations", "Creating migrations"):
        print("⚠️  Warning: Migration creation failed. Continuing anyway...")
    
    if not run_command(f"{python_cmd} manage.py migrate", "Running migrations"):
        print("❌ Error: Database migration failed. Please check your database configuration.")
        sys.exit(1)
    
    # Create superuser if it doesn't exist
    print("👤 Checking for superuser...")
    try:
        result = subprocess.run(
            f"{python_cmd} manage.py shell -c \"from django.contrib.auth.models import User; print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')\"",
            shell=True, capture_output=True, text=True
        )
        if "No superuser" in result.stdout:
            print("👤 No superuser found. You can create one with:")
            print(f"   {python_cmd} manage.py createsuperuser")
    except:
        pass
    
    # Set up sample data
    print("📊 Setting up sample data...")
    if Path("setup_sample_data.py").exists():
        if run_command(f"{python_cmd} setup_sample_data.py", "Setting up sample data"):
            print("✅ Sample data created successfully")
        else:
            print("⚠️  Warning: Failed to create sample data. You can run it manually later.")
    
    # Start the development server
    print("\n🚀 Starting Django development server...")
    print("=" * 60)
    print("🌐 Server will be available at:")
    print("   • API Documentation: http://localhost:8000/api/docs/")
    print("   • Admin Interface: http://localhost:8000/admin/")
    print("   • Health Check: http://localhost:8000/api/health/")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server
        subprocess.run(f"{python_cmd} manage.py runserver", shell=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
