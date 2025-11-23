# backend/seed.py
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, Module, Topic, Project, UserProgress, project_topics
import json

def seed_db():
    """Populates the database with initial user, modules, topics, and projects."""
    # Create tables if they don't exist
    from app.database import create_tables
    create_tables()
    
    db = SessionLocal()
    print("🌱 Seeding database...")

    # Check if data already exists
    if db.query(Module).first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    # 1. Create a Module
    net_mod = Module(name="Networking Fundamentals", description="Core concepts of computer networks.")
    db.add(net_mod)
    db.commit()

    # 2. Create a Topic
    osi_topic = Topic(
        module_id=net_mod.id, 
        name="The OSI Model", 
        description="Understanding the 7 layers of the OSI model.",
        content="The Open Systems Interconnection (OSI) model is a conceptual framework..."
    )
    db.add(osi_topic)
    db.commit()

    # 3. Create a Project
    handshake_proj = Project(
        title="Analyze a TCP Handshake with Wireshark",
        objective="To capture and analyze a TCP three-way handshake.",
        setup_instructions="1. Install Wireshark.\n2. Start a capture on your active network interface.",
        guided_steps=json.dumps([
            {"step": "Stop the capture after the page loads."},
            {"step": "Filter for TCP SYN packets."}
        ]),
        validation_script="# Placeholder for a Python script to check the result",
        difficulty_level="beginner"
    )
    db.add(handshake_proj)
    db.commit()

    # 4. Link Project to Topic
    handshake_proj.topics.append(osi_topic)
    db.commit()

    # 5. Create a User
    test_user = User(username="testuser", skill_level="beginner")
    db.add(test_user)
    db.commit()

    # 6. Initialize User Progress for the new topic
    user_progress = UserProgress(
        user_id=test_user.id,
        topic_id=osi_topic.id,
        mastery_probability=0.2 # Initial BKT probability
    )
    db.add(user_progress)
    db.commit()

    db.close()
    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed_db()