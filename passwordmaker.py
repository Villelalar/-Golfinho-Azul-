from werkzeug.security import generate_password_hash
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python passwordmaker.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    print("\nGenerating password hash...")
    print("Password:", password)
    print("Hash:", generate_password_hash(password))

if __name__ == '__main__':
    main()
