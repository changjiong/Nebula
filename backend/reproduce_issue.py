
import sys
import os

# Add backend directory to path
sys.path.append(os.getcwd())

from sqlmodel import select, Session
from app.core.db import engine
from app.models import Skill, User
from app.core.permissions import filter_skills_by_permission

def reproduction():
    with Session(engine) as session:
        print("Querying all skills...")
        try:
            skills = session.exec(select(Skill)).all()
            print(f"Found {len(skills)} skills.")
        except Exception as e:
            print(f"Error querying skills: {e}")
            import traceback
            traceback.print_exc()
            return

        print("Querying first superuser...")
        user = session.exec(select(User).where(User.is_superuser == True)).first()
        if not user:
            print("No superuser found, trying any user...")
            user = session.exec(select(User)).first()
        
        if not user:
            print("No users found.")
            # Create a dummy user object if needed, or pass None
            user = None

        print(f"Testing permissions with user: {user.email if user else 'None'}")
        
        try:
            filtered = filter_skills_by_permission(user, skills)
            print(f"Filtered skills: {len(filtered)}")
        except Exception as e:
            print(f"Error filtering skills: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    reproduction()
