# Astrology Platform

A comprehensive microservices-based astrology platform featuring a Telegram bot, memory service, and astrology calculation API.

## Demo
Telegram: rudie_astro_bot

## 🏗️ Architecture

This platform consists of three main services:

- **Bot**: Telegram bot interface for user interactions
- **Memory**: Memory management service using Mem0 and Qdrant
- **Astrology**: Vedic astrology calculation API and MCP server

### Infrastructure Components

- **PostgreSQL**: Primary database for bot data
- **Redis**: Caching and session management
- **RabbitMQ**: Message queue for async processing
- **Qdrant**: Vector database for memory storage
- **Ollama**: External LLM service (not containerized)

## 📋 Prerequisites

- Docker and Docker Compose installed
- Ollama running at `192.168.0.200` (or update in `.env`)
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/aadityamundhalia/astrology-platform.git
cd astrology-platform

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and update the following required values:

```properties
# Required: Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Required: Generate encryption key
# Run: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
CHAT_ENCRYPTION_KEY=your_encryption_key_here

# Update if needed
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f bot
docker-compose logs -f memory-service
docker-compose logs -f astrology-mcp
```

### 4. Verify Installation

Check that all services are healthy:

```bash
docker-compose ps
```

Expected output should show all services as "healthy" or "running".

### 5. Access Services

- **Bot**: Running and connected to Telegram
- **Memory API**: http://localhost:8085/docs
- **Astrology API**: http://localhost:8087/docs
- **Astrology MCP**: http://localhost:8585/health

#### Management UIs & Database Access

- **RabbitMQ Management**: http://localhost:15673 or http://192.168.0.200:15673
  - Username: `guest`
  - Password: `guest`
  
- **Qdrant Dashboard**: http://localhost:6334/dashboard or http://192.168.0.200:6334/dashboard
  - Access vector database UI
  - View collections and points
  
- **Redis Commander** (Optional GUI for Redis):
  ```bash
  # Start Redis GUI with tools profile
  docker-compose --profile tools up -d
  
  # Access at:
  # http://localhost:8081 or http://192.168.0.200:8081
  ```
  
- **PostgreSQL Database**:
  - Host: `localhost` or `192.168.0.200`
  - Port: `5433`
  - Database: `astrology`
  - Username: `default`
  - Password: `secret` (or your configured password)
  - Use any PostgreSQL client (pgAdmin, DBeaver, DataGrip, etc.)
  
- **Redis Direct Connection**:
  - Host: `localhost` or `192.168.0.200`
  - Port: `6380`
  - Password: `secret_redis` (or your configured password)
  - Use Redis CLI, RedisInsight, or any Redis client

## 🔧 Configuration

### Port Configuration

The default ports are configured to avoid conflicts with commonly used services:

| Service | Internal Port | External Port | Configurable |
|---------|--------------|---------------|--------------|
| PostgreSQL | 5432 | 5433 | POSTGRES_PORT |
| Redis | 6379 | 6380 | REDIS_PORT |
| RabbitMQ | 5672 | 5673 | RABBITMQ_PORT |
| RabbitMQ Mgmt | 15672 | 15673 | RABBITMQ_MANAGEMENT_PORT |
| Qdrant HTTP | 6333 | 6334 | QDRANT_HTTP_PORT |
| Qdrant gRPC | 6334 | 6335 | QDRANT_GRPC_PORT |
| Redis Commander | 8081 | 8081 | REDIS_COMMANDER_PORT |
| Bot API | 8282 | 8282 | BOT_PORT |
| Memory Service | 8085 | 8085 | MEMORY_SERVICE_PORT |
| Astrology API | 8087 | 8087 | ASTROLOGY_API_PORT |
| Astrology MCP | 8585 | 8585 | ASTROLOGY_MCP_PORT |

### Service Communication

All services communicate internally using Docker network names:

- `postgres:5432` - PostgreSQL database
- `redis:6379` - Redis cache
- `rabbitmq:5672` - RabbitMQ message broker
- `qdrant:6333` - Qdrant vector database
- `astrology-api:8087` - Astrology calculation API
- `astrology-mcp:8585` - Astrology MCP server
- `memory-service:8085` - Memory management service

## 📦 Project Structure

```
astrology-platform/
├── docker-compose.yml          # Main orchestration file
├── .env                        # Environment variables (create from .env.example)
├── .env.example               # Environment template
├── init-db.sql                # Database initialization
├── README.md                  # This file
├── bot/                       # Telegram bot service
│   ├── Dockerfile
│   ├── config.py             # Updated to read from parent .env
│   ├── main.py
│   └── ...
├── memory/                    # Memory service
│   ├── Dockerfile
│   ├── config.py             # Updated to read from parent .env
│   ├── main.py
│   └── ...
└── astrology/                 # Astrology API service
    ├── Dockerfile
    ├── Dockerfile.mcp
    ├── app.py
    ├── mcp_server.py
    └── ...
```

## 🛠️ Management Commands

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (caution: deletes data)
docker-compose down -v

# Restart specific service
docker-compose restart bot
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f bot
docker-compose logs -f memory-service

# Last 100 lines
docker-compose logs --tail=100 bot
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U default -d astrology

# Run migrations (bot service)
docker-compose run --rm bot-init

# Backup database
docker-compose exec postgres pg_dump -U default astrology > backup.sql

# Restore database
docker-compose exec -T postgres psql -U default astrology < backup.sql
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli -a secret_redis

# Monitor Redis
docker-compose exec redis redis-cli -a secret_redis MONITOR

# Check keys
docker-compose exec redis redis-cli -a secret_redis KEYS '*'

# Or connect from host machine
redis-cli -h 192.168.0.200 -p 6380 -a secret_redis
```

### Qdrant Operations

```bash
# Check Qdrant health
curl http://localhost:6334/healthz
curl http://192.168.0.200:6334/healthz

# Access Qdrant Dashboard
# Open in browser: http://localhost:6334/dashboard
# Or: http://192.168.0.200:6334/dashboard

# List collections via API
curl http://localhost:6334/collections
```

### Optional Tools

```bash
# Start Redis Commander (Web GUI for Redis)
docker-compose --profile tools up -d

# Access Redis Commander
# http://localhost:8081 or http://192.168.0.200:8081

# Stop optional tools
docker-compose --profile tools down
```

### Health Checks

```bash
# Check service health
docker-compose ps

# Individual service health
curl http://localhost:8282/health  # Bot
curl http://localhost:8085/docs    # Memory Service
curl http://localhost:8087/docs    # Astrology API
```

## 🔍 Troubleshooting

### Services won't start

1. Check if ports are already in use:
```bash
lsof -i :5433  # PostgreSQL
lsof -i :6380  # Redis
lsof -i :6334  # Qdrant
```

2. View detailed logs:
```bash
docker-compose logs bot
```

3. Verify environment variables:
```bash
docker-compose config
```

### Database connection issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U default -d astrology -c "SELECT 1;"
```

### Bot not responding

1. Verify Telegram token is correct
2. Check bot logs: `docker-compose logs -f bot`
3. Ensure all dependencies are healthy:
```bash
docker-compose ps
```

### Memory service issues

1. Verify Qdrant is running: `curl http://localhost:6334/healthz`
2. Check Ollama connectivity: `curl http://192.168.0.200:11434/api/tags`
3. Review logs: `docker-compose logs -f memory-service`

## 🔐 Security Notes

- Change default passwords in `.env` before deploying to production
- Never commit `.env` file to version control
- Use strong passwords for PostgreSQL, Redis, and RabbitMQ
- Rotate encryption keys periodically
- Keep the Telegram bot token secure

## 📊 Monitoring

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Service Metrics

- **RabbitMQ Management UI**: http://localhost:15673 or http://192.168.0.200:15673
  - Username: `guest`, Password: `guest`
  - Check queue depths, message rates, and consumer activity
  
- **Qdrant Dashboard**: http://localhost:6334/dashboard or http://192.168.0.200:6334/dashboard
  - Monitor vector collections and storage
  
- **Redis Commander**: http://localhost:8081 or http://192.168.0.200:8081 (if started with `--profile tools`)
  - View keys, memory usage, and statistics

## 🧪 Development

### Rebuild specific service

```bash
# Rebuild and restart
docker-compose up -d --build bot

# Rebuild without cache
docker-compose build --no-cache memory-service
```

### Access container shell

```bash
docker-compose exec bot /bin/bash
docker-compose exec memory-service /bin/sh
docker-compose exec postgres /bin/sh
docker-compose exec redis /bin/sh
```

### Connect to databases from external tools

**PostgreSQL** (use pgAdmin, DBeaver, DataGrip, etc.):
```
Host: 192.168.0.200
Port: 5433
Database: astrology
Username: default
Password: secret
```

**Redis** (use RedisInsight, Another Redis Desktop Manager, etc.):
```
Host: 192.168.0.200
Port: 6380
Password: secret_redis
```

**Qdrant** (use Python client or REST API):
```python
from qdrant_client import QdrantClient

client = QdrantClient(
    url="http://192.168.0.200:6334",
    api_key=None  # No auth by default
)
```

## 🤝 Contributing

1. Make changes to your service code
2. Test locally: `docker-compose up -d --build <service-name>`
3. Verify logs: `docker-compose logs -f <service-name>`
4. Commit changes

## 📝 License

MIT

## 🆘 Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review configuration: `docker-compose config`
- Verify environment: `cat .env`
