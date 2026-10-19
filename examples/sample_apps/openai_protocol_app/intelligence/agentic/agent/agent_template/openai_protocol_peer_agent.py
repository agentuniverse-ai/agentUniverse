from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.agent.template.peer_agent_template import PeerAgentTemplate


class PeerAgent(PeerAgentTemplate,OpenAIProtocolTemplate):
    """Peer agent that combines peer-agent collaboration with OpenAI protocol handling.

    Inherits the peer-agent collaboration behavior and the OpenAI protocol request format.
    """