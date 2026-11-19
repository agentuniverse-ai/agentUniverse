# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 14:20
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: session_service.py
import uuid
from datetime import datetime
from typing import List

from agentuniverse_product.dal.message_library import MessageLibrary
from agentuniverse_product.dal.model.message_do import MessageDO
from agentuniverse_product.dal.model.session_do import SessionDO
from agentuniverse_product.dal.session_library import SessionLibrary
from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.session_dto import SessionDTO


class SessionService:
    """Session Service for aU-product."""

    @staticmethod
    def create_session(agent_id: str) -> str:
        """Create a new session for a given agent id."""
        if agent_id is None:
            raise ValueError("agent_id is required parameter.")
        session_id = str(uuid.uuid4())
        session_do = SessionDO(
            session_id=session_id,
            agent_id=agent_id,
            ext_info=dict(),
        )
        return SessionLibrary().add_session(session_do)

    @staticmethod
    def update_session(session_id: str, agent_id: str, update_time: datetime) -> str:
        """Update a session."""
        return SessionLibrary().update_session(
            SessionDO(session_id=session_id, agent_id=agent_id, gmt_modified=update_time))

    @staticmethod
    def delete_session(session_id: str) -> str:
        """Delete the session with the specified session id."""
        if session_id is None:
            raise ValueError("session_id is required parameter.")
        session_id = SessionLibrary().delete_session(session_id)
        if session_id:
            MessageLibrary().delete_messages(session_id)
        return session_id or ''

    @staticmethod
    def get_session_list(agent_id: str) -> List[SessionDTO]:
        """Get a list of sessions for a given agent id."""
        if agent_id is None:
            raise ValueError("agent_id is required parameter.")
        session_do_list: List[SessionDO] = SessionLibrary().get_session_list(agent_id)
        if len(session_do_list) == 0:
            return []
        # newest 10 sessions
        session_do_list = session_do_list[:10]
        session_messages_map = {}
        for session_do in session_do_list:
            message_do_list: List[MessageDO] = MessageLibrary().get_messages(session_do.session_id)
            session_messages_map[session_do.session_id] = message_do_list
        return SessionService().convert_to_session_dto(session_do_list, session_messages_map)

    @staticmethod
    def get_session_detail(id: str, top_k: int = None) -> SessionDTO | None:
        """Get the session detail for a given session id."""
        if id is None:
            raise ValueError("Session id is required parameter.")
        session_do: SessionDO = SessionLibrary().get_session_detail(id)
        if session_do is None:
            return session_do
        # newest top k messages
        message_do_list: List[MessageDO] = MessageLibrary().get_messages(session_do.session_id, top_k=top_k)
        return SessionService().convert_to_session_dto([session_do], {session_do.session_id: message_do_list})[0]

    @staticmethod
    def convert_to_session_dto(session_do_list: List[SessionDO], session_messages_map: dict[str, List[MessageDO]]) -> \
            List[SessionDTO]:
        """Convert the given session do list to session dto list."""
        res = []
        if len(session_do_list) == 0:
            return res
        for session_do in session_do_list:
            session_dto = SessionDTO(id=session_do.session_id, agent_id=session_do.agent_id,
                                     gmt_created=session_do.gmt_created.strftime('%Y-%m-%d %H:%M:%S'),
                                     gmt_modified=session_do.gmt_modified.strftime('%Y-%m-%d %H:%M:%S'))
            message_dto_list = []
            message_do_list = session_messages_map[session_do.session_id]
            for message_do in message_do_list:
                message_dto = MessageDTO(id=message_do.id, session_id=session_do.session_id,
                                         gmt_created=message_do.gmt_created.strftime('%Y-%m-%d %H:%M:%S'),
                                         gmt_modified=message_do.gmt_modified.strftime('%Y-%m-%d %H:%M:%S'),
                                         content=message_do.content)
                message_dto_list.append(message_dto)
            session_dto.messages = message_dto_list
            res.append(session_dto)
        return res
