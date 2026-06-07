from app.schemas import TicketTransferRequest


def test_ticket_transfer_request_schema():
    payload = TicketTransferRequest(
        target_agent_id="AGT-202",
        reason="Technical support ownership needed.",
    )

    assert payload.target_agent_id == "AGT-202"
    assert "Technical" in payload.reason
