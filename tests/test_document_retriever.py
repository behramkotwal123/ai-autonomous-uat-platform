from app.document_retriever import (
    retrieve_relevant_documentation
)


def test_retrieves_search_documentation():

    documentation = (
        retrieve_relevant_documentation(
            "/search GET NO_FLIGHTS"
        )
    )

    assert "/search" in documentation
    assert "NO_FLIGHTS" in documentation


def test_retrieves_booking_documentation():

    documentation = (
        retrieve_relevant_documentation(
            "/booking POST INVALID_FARE"
        )
    )

    assert "/booking" in documentation
    assert "INVALID_FARE" in documentation

