# SentinelEdge Threat Model (STRIDE)

| Threat Vector | Attack Scenario | Implemented Mitigation | Residual Risk |
| :--- | :--- | :--- | :--- |
| **Credential Theft** | Brute force or sniffing of operator passwords | Argon2 password hashing, HTTP-only secure cookies, JWT expiration | Compromised operator workstation |
| **Event Spoofing** | Rogue edge nodes posting fabricated incident events | HMAC/token validation on `/api/v1/incidents/ingest`, IP whitelisting | Insider threat with API secret |
| **Duplicate Injection** | Network replays generating duplicate alerts | SHA-256 idempotency key deduplication in PostgreSQL and Redis | Storage overhead for idempotency window |
| **Raw Video Leak** | Unauthorized access to internal video feeds | Zero-upload edge architecture; raw streams never transit WAN | Physical tampering with edge hardware |
| **Denial of Service** | Flooding backend ingestion endpoint | SlowAPI rate limiting, reverse proxy limits, bounded Redis Streams | High edge bandwidth consumption |
