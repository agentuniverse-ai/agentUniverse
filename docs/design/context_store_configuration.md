# Context store configuration loading

`initialize_by_component_configer` now applies the supplied YAML options before
initializing a storage backend. Previously these stores inherited an empty
configuration hook, so constructor defaults were used despite different YAML
settings (including the Redis endpoint and Chroma collection).

Shared options: `name`, `storage_tier`, `max_segments`, `ttl_hours`, and
`enable_metrics`. Metrics enabled through configuration are initialized before
RAM operations use them. Existing metrics are retained on reinitialization.

Redis additionally reads `redis_host`, `redis_port`, `redis_db`,
`redis_password`, `key_prefix`, and `default_ttl_seconds`. Chroma additionally
reads `collection_name`, `embedding_model_name`, `persist_directory`, and
`similarity_threshold` before constructing its client and embedding function.

Only these explicit options are assigned. Omitted options keep constructor
values; supplied false, zero and null values are not discarded by truthiness
checks. For example, `redis_password: null` clears a constructor-supplied
password. Configuration should use the same value types as the corresponding
constructor fields. This does not add validation of arbitrary assignments.

This fixes configuration application, not context component package discovery
or Chroma persistence/embedding compatibility. The backend's existing support
and limitations for each option remain unchanged. In particular, this does not
add capacity enforcement to backends that do not implement it.
