from database import SessionLocal, User, Base, engine

def create_users():
    db = SessionLocal()
    
    # Define your test users and their plain-text passwords here
    test_users = {
        "priya": "pass123",
        "raghav": "pass456",
        "anjali": "pass789",
        "arjun": "pass101",
        "meena": "pass112"
    }

    print("Adding test users...")
    for username, password in test_users.items():
        # Check if user already exists
        if not db.query(User).filter(User.username == username).first():
            # Create a new user with the plain-text password
            new_user = User(username=username, password=password)
            db.add(new_user)
            print(f"- Created user: {username}")
        else:
            print(f"- User '{username}' already exists, skipping.")

    db.commit()
    db.close()
    print("\nTest users are ready.")

if __name__ == "__main__":
    # This function creates the database file and all tables defined in database.py
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")
    
    # Now, add the users to the newly created tables
    create_users()