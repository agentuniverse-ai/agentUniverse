from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='test_app/config.toml', core_mode=True)

if __name__ == '__main__':
    print("Agent Universe started successfully.")
