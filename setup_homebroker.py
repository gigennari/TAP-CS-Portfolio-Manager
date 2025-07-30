#!/usr/bin/env python3
"""
Setup script for the Homebroker functionality
This script installs the required dependencies and sets up the environment
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    
    requirements = [
        "flask==2.3.2",
        "flask-cors==4.0.0", 
        "mysql-connector-python==8.3.0",
        "yfinance==0.2.37",
        "requests==2.31.0"
    ]
    
    for requirement in requirements:
        try:
            print(f"Installing {requirement}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"✓ {requirement} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {requirement}: {e}")
            return False
    
    return True

def create_env_file():
    """Create environment file for API keys"""
    env_file = os.path.join(os.path.dirname(__file__), 'server', '.env')
    
    if not os.path.exists(env_file):
        print("Creating .env file for API configuration...")
        with open(env_file, 'w') as f:
            f.write("# Alpha Vantage API Key\n")
            f.write("# Get your free API key from: https://www.alphavantage.co/support/#api-key\n")
            f.write("ALPHA_VANTAGE_API_KEY=YOUR_API_KEY_HERE\n")
            f.write("\n")
            f.write("# Flask Configuration\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=True\n")
        
        print(f"✓ Created {env_file}")
        print("⚠️  Please update the ALPHA_VANTAGE_API_KEY in the .env file")
    else:
        print(f"✓ .env file already exists at {env_file}")

def main():
    """Main setup function"""
    print("🚀 Setting up Homebroker functionality...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install some requirements. Please check the errors above.")
        return False
    
    # Create environment file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Get a free Alpha Vantage API key from: https://www.alphavantage.co/support/#api-key")
    print("2. Update the ALPHA_VANTAGE_API_KEY in server/.env file")
    print("3. Start the Flask server: python server/app.py")
    print("4. Open homebroker.html in your browser")
    print("\n🎯 Features available:")
    print("• Stock search with auto-completion")
    print("• Real-time stock data and charts")
    print("• Buy/Sell functionality")
    print("• Portfolio integration")
    
    return True

if __name__ == "__main__":
    main()