
from backend.database import Base, engine
from backend.models.election import Election
from backend.models.candidate import Candidate
from backend.models.vote import Vote

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
