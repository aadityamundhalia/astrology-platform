# Quick Start Guide

Get the Astrology Platform up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Docker
docker --version

# Check Docker Compose
docker-compose --version
```

If not installed, visit: https://docs.docker.com/get-docker/

## Step 1: Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Or use setup script
chmod +x setup.sh
./setup.sh
```

## Step 2: Configure Required Variables

Edit `.env` and set:

```bash
# 1. Get Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 2. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output to:
CHAT_ENCRYPTION_KEY=generated_key_here

# 3. (Optional) Change passwords
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
```

## Step 3: Start Services

```bash
# Start everything
docker-compose up -d

# Watch logs
docker-compose logs -f
```

## Step 4: Verify

```bash
# Check all services are running
docker-compose ps

# Should see all services as "healthy" or "running"
```

## Step 5: Test

1. Open Telegram and find your bot
2. Send `/start` to your bot
3. Try asking an astrology question!

## Access Points

- **Bot**: Your Telegram bot
- **Memory API Docs**: http://localhost:8085/docs
- **Astrology API Docs**: http://localhost:8087/docs
- **RabbitMQ Management**: http://localhost:15673 (guest/guest)

## Using Make Commands (Optional)

If you have `make` installed:

```bash
# Setup
make setup

# Start
make up

# View logs
make logs

# Check health
make health

# Stop
make down

# See all commands
make help
```

## Common Issues

### Port Already in Use

If you see port conflicts, edit `.env` and change the port numbers:

```bash
POSTGRES_PORT=5433  # Change to 5434 if needed
REDIS_PORT=6380     # Change to 6381 if needed
```

### Bot Not Responding

1. Check bot token is correct in `.env`
2. View bot logs: `docker-compose logs bot`
3. Ensure all dependencies are running: `docker-compose ps`

### Services Not Starting

```bash
# View detailed logs
docker-compose logs

# Rebuild
docker-compose up -d --build
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Configure advanced settings in `.env`
- Set up monitoring and backups

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove all data (⚠️ destructive)
docker-compose down -v
```

## Getting Help

- Check logs: `docker-compose logs -f`
- Verify config: `docker-compose config`
- View running services: `docker-compose ps`