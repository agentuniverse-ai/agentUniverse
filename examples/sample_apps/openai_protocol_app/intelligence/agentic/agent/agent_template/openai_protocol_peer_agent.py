from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.agent.template.peer_agent_template import PeerAgentTemplate


class PeerAgent(PeerAgentTemplate,OpenAIProtocolTemplate):
    """Demo peer agent exposing the OpenAI protocol interface.

    Combines the peer work pattern from `PeerAgentTemplate` with the
    OpenAI protocol input/output handling of `OpenAIProtocolTemplate`;
    the class body is intentionally empty.
    """
    pass