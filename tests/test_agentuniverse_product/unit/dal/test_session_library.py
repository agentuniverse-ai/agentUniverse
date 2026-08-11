from agentuniverse_product.dal.model.session_do import SessionDO
from agentuniverse_product.dal.session_library import SessionLibrary


def test_update_session_does_not_mask_session_acquisition_error(monkeypatch):
    library = SessionLibrary.__wrapped__()

    def fail_to_acquire_session():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(library, "get_db_session", fail_to_acquire_session)
    session = SessionDO(session_id="session-1", agent_id="agent-1")

    assert library.update_session(session) is None
