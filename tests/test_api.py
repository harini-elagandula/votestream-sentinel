
from uuid import uuid4

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# 1. Test the home endpoint
def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["project"] == "VoteStream Sentinel"


# 2. Test the health endpoint
def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# 3. Test duplicate-vote prevention
def test_duplicate_vote_is_rejected():
    payload = {
        "election_id": 2,
        "candidate_id": 5,
        "voter_id": f"pytest-{uuid4()}",
    }

    first_response = client.post(
        "/api/v1/votes",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/votes",
        json=payload,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "This voter has already voted in this election"
    )


# 4. Test rejection of a nonexistent election
def test_vote_rejects_nonexistent_election():
    payload = {
        "election_id": 999999,
        "candidate_id": 5,
        "voter_id": f"pytest-{uuid4()}",
    }

    response = client.post(
        "/api/v1/votes",
        json=payload,
    )

    assert response.status_code == 400


# 5. Test rejection of a nonexistent candidate
def test_vote_rejects_nonexistent_candidate():
    payload = {
        "election_id": 2,
        "candidate_id": 999999,
        "voter_id": f"pytest-{uuid4()}",
    }

    response = client.post(
        "/api/v1/votes",
        json=payload,
    )

    assert response.status_code == 400


# 6. Test election creation
def test_create_election():
    payload = {
        "title": f"Pytest Election {uuid4()}"
    }

    response = client.post(
        "/api/v1/elections",
        json=payload,
    )

    assert response.status_code in (200, 201)
    assert response.json()["title"] == payload["title"]
    assert "id" in response.json()


# 7. Test candidate creation
def test_create_candidate():
    # Create an election first
    election_payload = {
        "title": f"Candidate Test Election {uuid4()}"
    }

    election_response = client.post(
        "/api/v1/elections",
        json=election_payload,
    )

    assert election_response.status_code in (200, 201)

    election_id = election_response.json()["id"]

    # Create a candidate for the new election
    candidate_payload = {
        "name": f"Test Candidate {uuid4()}"
    }

    candidate_response = client.post(
        f"/api/v1/elections/{election_id}/candidates",
        json=candidate_payload,
    )

    assert candidate_response.status_code in (200, 201)
    assert candidate_response.json()["name"] == candidate_payload["name"]
    assert candidate_response.json()["election_id"] == election_id

def test_list_elections():
    response = client.get("/api/v1/elections")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_results_endpoint():
    # Create an election specifically for this test.
    election_response = client.post(
        "/api/v1/elections",
        json={"title": "Results Test Election"},
    )

    assert election_response.status_code == 201
    election_id = election_response.json()["id"]

    # Add a candidate to the new election.
    candidate_response = client.post(
        f"/api/v1/elections/{election_id}/candidates",
        json={"name": "Test Candidate"},
    )

    assert candidate_response.status_code == 201

    # Check the results endpoint.
    results_response = client.get(
        f"/api/v1/results/{election_id}"
    )

    assert results_response.status_code == 200

    data = results_response.json()
    assert data["election_id"] == election_id
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["candidate"] == "Test Candidate"
    assert data["results"][0]["votes"] == 0
