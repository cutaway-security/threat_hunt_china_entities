"""threat_hunt_china_entities verification pipeline.

Tiered, source-grounded verification: each source fetch emits typed CLAIMS (credited only for what
it proves, DR-02a); indicators are assembled from claims by rules that forbid promoting attribution
into host-presence. No hashes or version-pinned values reach an indicator (DR-09/DR-10).
"""
