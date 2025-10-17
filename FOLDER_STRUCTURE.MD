# Astrology Platform - Folder Structure

## Final Repository Structure

```
astrology-platform/                 # Root directory (your parent folder)
│
├── docker-compose.yml              # Main orchestration file (NEW)
├── .env                           # Main environment variables (NEW - create from .env.example)
├── .env.example                   # Environment template (NEW)
├── .gitignore                     # Git ignore file (NEW)
├── init-db.sql                    # PostgreSQL initialization (NEW)
├── README.md                      # Main documentation (NEW)
├── QUICKSTART.md                  # Quick start guide (NEW)
├── Makefile                       # Make commands for easy management (NEW)
├── setup.sh                       # Setup script (NEW)
│
├── bot/                           # Telegram bot service
│   ├── Dockerfile                 # Existing (can be modified if needed)
│   ├── docker-compose.yml         # Can be removed (replaced by root docker-compose.yml)
│   ├── .env                       # Can be removed (using root .env now)
│   ├── config.py                  # MUST UPDATE - use new version provided
│   ├── main.py                    # Existing - no changes needed
│   ├── requirements.txt           # Existing - no changes needed
│   ├── alembic/                   # Existing - no changes needed
│   ├── logs/                      # Existing - no changes needed
│   └── ...                        # Other bot files
│
├── memory/                        # Memory service
│   ├── Dockerfile                 # Existing - no changes needed
│   ├── .env                       # Can be removed (using root .env now)
│   ├── config.py                  # MUST UPDATE - use new version provided
│   ├── main.py                    # Existing - no changes needed
│   ├── requirements.txt           # Existing - no changes needed
│   └── ...                        # Other memory files
│
└── astrology/                     # Astrology API service
    ├── Dockerfile                 # Existing - no changes needed
    ├── Dockerfile.mcp             # Existing - no changes needed
    ├── docker-compose.yml         # Can be removed (replaced by root docker-compose.yml)
    ├── app.py                     # Existing - no changes needed
    ├── mcp_server.py              # Existing - no changes needed
    ├── requirements.txt           # Existing - no changes needed
    ├── requirements.mcp.txt       # Existing - no changes needed
    ├── ephe/                      # Existing - no changes needed
    └── ...                        # Other astrology files
```

## What Files to Update/Create

### Files to CREATE (in root directory):
1. `docker-compose.yml` - Main orchestration
2. `.env` - Copy from `.env.example` and configure
3. `.env.example` - Environment template
4. `init-db.sql` - Database initialization
5. `README.md` - Main documentation
6. `QUICKSTART.md` - Quick start guide
7. `.gitignore` - Git ignore patterns
8. `Makefile` - Make commands (optional but helpful)
9. `setup.sh` - Setup script (optional but helpful)

### Files to UPDATE:
1. `bot/config.py` - Update with new version that reads from parent .env
2. `memory/config.py` - Update with new version that reads from parent .env

### Files to REMOVE (optional cleanup):
1. `bot/.env` - No longer needed
2. `bot/docker-compose.yml` - No longer needed
3. `memory/.env` - No longer needed
4. `astrology/docker-compose.yml` - No longer needed

### Files to KEEP (no changes):
- All Dockerfiles
- All Python application code
- All requirements.txt files
- All other service-specific files

## Network Configuration

All services communicate via the `astrology-network` Docker network:

### Internal Service URLs (used by containers):
- `postgres:5432` - PostgreSQL
- `redis:6379` - Redis
- `rabbitmq:5672` - RabbitMQ
- `qdrant:6333` - Qdrant
- `astrology-api:8087` - Astrology API
- `astrology-mcp:8585` - Astrology MCP Server
- `memory-service:8085` - Memory Service

### External Access (from host):
- `localhost:5433` - PostgreSQL
- `localhost:6380` - Redis
- `localhost:5673` - RabbitMQ
- `localhost:15673` - RabbitMQ Management UI
- `localhost:6334` - Qdrant HTTP
- `localhost:8087` - Astrology API
- `localhost:8585` - Astrology MCP Server
- `localhost:8085` - Memory Service
- `localhost:8282` - Bot API

## Port Mapping Summary

| Service | Internal Port | External Port | Environment Variable |
|---------|--------------|---------------|---------------------|
| PostgreSQL | 5432 | 5433 | POSTGRES_PORT |
| Redis | 6379 | 6380 | REDIS_PORT |
| RabbitMQ | 5672 | 5673 | RABBITMQ_PORT |
| RabbitMQ Mgmt | 15672 | 15673 | RABBITMQ_MANAGEMENT_PORT |
| Qdrant HTTP | 6333 | 6334 | QDRANT_HTTP_PORT |
| Qdrant gRPC | 6334 | 6335 | QDRANT_GRPC_PORT |
| Bot | 8282 | 8282 | BOT_PORT |
| Memory | 8085 | 8085 | MEMORY_SERVICE_PORT |
| Astrology API | 8087 | 8087 | ASTROLOGY_API_PORT |
| Astrology MCP | 8585 | 8585 | ASTROLOGY_MCP_PORT |

**Note**: External ports are configured to avoid conflicts with commonly used ports. You can change these in `.env` if needed.

## Volume Mounts

Persistent data is stored in Docker volumes:

- `postgres_data` - PostgreSQL database
- `redis_data` - Redis data
- `rabbitmq_data` - RabbitMQ data
- `qdrant_data` - Qdrant vector database
- `./bot/logs` - Bot application logs (mounted from host)

## Migration Path

1. Keep existing project folders intact
2. Create new files in root directory
3. Update `bot/config.py` and `memory/config.py`
4. Create `.env` from `.env.example`
5. Test: `docker-compose up -d`
6. Once verified, optionally remove old `.env` and `docker-compose.yml` files from subfolders