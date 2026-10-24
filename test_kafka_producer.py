
from backend.streaming.producer import publish_vote_event

publish_vote_event({
    "event": "vote_recorded",
    "election_id": 2,
    "candidate_id": 4,
    "voter_id": "demo-voter-002",
})

print("Producer test finished.")
