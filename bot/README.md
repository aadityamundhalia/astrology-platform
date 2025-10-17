# Rudie - Vedic Astrology Telegram Bot 🌿✨

A friendly, AI-powered Telegram bot that provides personalized Vedic astrology predictions with a warm, conversational personality.

## Features

### 🔮 Astrology Predictions
- 🌙 Daily, weekly, monthly, quarterly, and yearly predictions
- 💕 Love, career, wealth, and health forecasts
- 🎯 Event-specific predictions (job offers, proposals, etc.)
- 📊 Comprehensive horoscope readings

### 🤖 AI-Powered Interface
- **Rudie**: A 22-year-old Australian astrologer personality
- Natural, conversational responses
- Direct YES/NO/WAIT answers for decisions
- Thinking mode for deeper reasoning (configurable)
- Multi-tool function calling for accurate predictions

### 🎨 User Experience
- 📝 Step-by-step wizard for birth details
- 🔄 Easy detail updates via `/change` command
- ⚡ Priority queue system for VIP users
- 🚦 User activation/deactivation system
- 💬 Chat history with Redis caching
- 🧠 Mem0-powered memory for context retention

### 🔐 Security & Privacy
- **End-to-End Chat Encryption**: Users can choose to encrypt their conversations
- **Fernet Symmetric Encryption**: Fast, secure, compact encryption
- **Selective Encryption**: Users control their privacy settings
- **Encrypted Storage**: Messages encrypted at rest in database
- **Privacy-First Logging**: Encrypted chats not logged
- **Flexible Settings**: Enable/disable encryption anytime

### ⚙️ System Features
- 🐰 RabbitMQ message queue (prevents GPU overload)
- 👷 Configurable worker count for scalability
- 🎯 Priority-based request processing
- 🔐 User status management (active/inactive)
- 📈 Ready for monetization with priority tiers

### 🛡️ Moderation & Safety
- ⚠️ Automatic profanity detection
- 📊 Strike system (configurable max strikes)
- 🚫 Auto-deactivation after max strikes
- 🔄 Admin strike reset capability
- 📝 Polite warnings before deactivation

## Tech Stack

- **Framework**: FastAPI (with lifespan management)
- **AI/LLM**: Semantic Kernel + Ollama (`gpt-oss:latest`)
- **Database**: PostgreSQL (with Alembic migrations)
- **Cache**: Redis (chat history, temporary data)
- **Queue**: RabbitMQ (request queuing with priorities)
- **Bot**: python-telegram-bot (async)
- **Memory**: Mem0 (conversation memory service)
- **Embeddings**: Qdrant (vector database for Mem0)
- **Encryption**: Fernet (symmetric encryption for chat privacy)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (database)
- Redis (caching)
- RabbitMQ (message queue)
- Qdrant (vector database for Mem0)
- Ollama with models:
  - `gpt-oss:latest` (main reasoning model)
  - `nomic-embed-text` (embeddings for Mem0)
- Telegram Bot Token (from @BotFather)
- Mem0 Service (running separately)
- Astrology API Service (running separately)

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd astrology-bot
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Generate encryption key:**
```bash
python scripts/generate_encryption_key.py
```

This will output a key like:
```
CHAT_ENCRYPTION_KEY=your_generated_key_here
```

5. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Key environment variables:
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Database
POSTGRES_HOST=192.168.0.200
POSTGRES_PORT=5432
POSTGRES_DB=astrology
POSTGRES_USER=default
POSTGRES_PASSWORD=your_password

# Redis
REDIS_HOST=192.168.0.200
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=192.168.0.200
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=astrology_requests
RABBITMQ_WORKERS=1  # Number of concurrent workers

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:latest
ENABLE_THINKING=true
THINKING_MAX_TOKENS=500
THINKING_TEMPERATURE=0.75

# External Services
MEM0_SERVICE_URL=http://192.168.0.200:8085
ASTROLOGY_API_URL=http://192.168.0.200:8087

# Chat Encryption
CHAT_ENCRYPTION_KEY=your_generated_key_from_step_4

# User Management
MAX_STRIKES=3
ENABLE_PROFANITY_FILTER=true
```

6. **Setup database:**
```bash
# Create database
psql -h your_host -U your_user -c "CREATE DATABASE astrology;"

# Run migrations
alembic upgrade head
```

7. **Pull Ollama models:**
```bash
ollama pull gpt-oss:latest
ollama pull nomic-embed-text
```

8. **Run tests:**
```bash
# Test all connections
python tests/test_connections.py

# Test RabbitMQ specifically
python tests/test_rabbitmq.py

# Test encryption
python tests/test_encryption.py

# Run all tests
python run_tests.py
```

9. **Start the bot:**
```bash
# Development
python main.py

# Production (Docker)
docker-compose up -d
```

## Chat Encryption

### How It Works

1. **User Choice**: During setup via `/change`, users are asked if they want encryption
2. **Automatic Encryption**: If enabled, all messages are encrypted before database storage
3. **Transparent Decryption**: Encrypted messages are automatically decrypted when retrieved
4. **Privacy-First**: Encrypted chats are never logged in plain text
5. **Flexible Control**: Users can enable/disable encryption anytime

### Encryption Details

- **Algorithm**: Fernet (symmetric encryption)
- **Key Size**: 256-bit (32 bytes)
- **Performance**: Fast encryption/decryption (<1ms per message)
- **Storage**: Encrypted messages are ~133% of original size (base64 encoded)
- **Security**: Industry-standard cryptographic library (cryptography.io)

### User Commands for Encryption
```bash
# Enable encryption during setup
/change
# Follow prompts and select "Yes, encrypt my chats 🔐"

# Enable encryption later
/change
# Select encryption option

# View encryption status
/info
```

### Admin Commands for Encryption
```bash
# View user encryption status
python scripts/manage_user.py get <user_id>

# Enable encryption for a user (encrypts all previous chats)
python scripts/manage_user.py encrypt <user_id>

# Disable encryption for a user (previous chats remain encrypted)
python scripts/manage_user.py unencrypt <user_id>
```

### Important Notes

⚠️ **Key Management**:
- Keep `CHAT_ENCRYPTION_KEY` secret and secure
- If the key is lost, encrypted messages **cannot be recovered**
- Back up your encryption key in a secure location
- Never commit the `.env` file to version control

🔒 **Encryption Behavior**:
- **Enabling encryption**: All previous unencrypted chats are encrypted
- **Disabling encryption**: Previous encrypted chats remain encrypted, only new chats are unencrypted
- **Database migration**: Encrypted and unencrypted chats coexist safely

📊 **What Gets Encrypted**:
- ✅ User messages
- ✅ Bot responses
- ✅ Stored in `chat_history` table
- ❌ User metadata (name, birth details) - these remain unencrypted for functionality

## Usage

### User Commands

Talk to your bot on Telegram:

**Setup** (first time):
- `/start` - Welcome and setup instructions
- `/change` - Interactive wizard for birth details and encryption settings
- Send details all at once:
```
  Date of Birth: 1990-01-15
  Time of Birth: 10:30
  Place of Birth: New Delhi, India
```

**Get Predictions:**
- "How is today for me?"
- "What's my week looking like?"
- "Tell me about my love life this month"
- "Should I take this job offer?"
- "Good time to ask someone out?"
- "Career predictions for this year"

**Other Commands:**
- `/info` - View your birth details and encryption status
- `/help` - Usage instructions
- `/clear` - Clear chat history and memory
- `/cancel` - Cancel current operation

### Admin Commands

Manage users via CLI:
```bash
# List all users
python scripts/manage_user.py list

# Get user details (including encryption status)
python scripts/manage_user.py get 123456789

# Activate/Deactivate users
python scripts/manage_user.py activate 123456789
python scripts/manage_user.py deactivate 123456789

# Set user priority (1=VIP, 10=lowest)
python scripts/manage_user.py priority 123456789 1

# Strike management
python scripts/manage_user.py reset-strikes 123456789

# Encryption management
python scripts/manage_user.py encrypt 123456789    # Enable and encrypt all chats
python scripts/manage_user.py unencrypt 123456789  # Disable (keeps old chats encrypted)

# Purge RabbitMQ queue
python scripts/purge_queue.py
# or
python scripts/purge_queue_http.py

# Reset RabbitMQ queue
python scripts/reset_rabbitmq_queue.py
```

### Scaling Workers

Adjust concurrent workers in `.env`:
```bash
RABBITMQ_WORKERS=3  # Process 3 requests simultaneously
```

**Note**: More workers = more GPU memory usage. Start with 1 worker per GPU.

## User Priority System

Users have priority levels (1-10):
- **Priority 1-2**: VIP users (⚡ fastest response)
- **Priority 3-5**: Standard users (default: 5)
- **Priority 6-10**: Low priority users

Messages are processed in priority order. Within the same priority, FIFO (first-in-first-out) applies.

## Strike System

The bot includes an automatic moderation system to maintain respectful interactions:

### How it Works
1. User sends rude/profane message
2. Bot detects inappropriate content
3. Strike is added to user's account
4. User receives warning with remaining strikes
5. After max strikes, account is auto-deactivated

### Configuration
```bash
MAX_STRIKES=3                    # Number of strikes before deactivation
ENABLE_PROFANITY_FILTER=true    # Enable/disable moderation
```

### Strike Management
- View strikes: `python scripts/manage_user.py get <user_id>`
- Reset strikes: `python scripts/manage_user.py reset-strikes <user_id>`
- Strikes are logged in database for audit trail

### What Triggers a Strike
- Profanity and vulgar language
- Insults and aggressive commands
- Disrespectful behavior
- The bot responds politely but firmly

Users are given clear warnings and know exactly how many strikes remain before deactivation.

## Configuration

### Thinking Mode

Enable/disable AI reasoning:
```bash
ENABLE_THINKING=true           # Enable thinking for better responses
THINKING_MAX_TOKENS=500        # Allow more tokens for reasoning
THINKING_TEMPERATURE=0.75      # Control creativity
```

### Worker Configuration

Adjust based on hardware:
```bash
RABBITMQ_WORKERS=1  # Single GPU: 1 worker
RABBITMQ_WORKERS=2  # Dual GPU: 2 workers
RABBITMQ_WORKERS=4  # High-end server: 4+ workers
```

### Chat History

Control Redis cache:
```bash
REDIS_CHAT_HISTORY_LIMIT=5  # Keep last 5 conversation pairs
```

### Encryption Settings
```bash
CHAT_ENCRYPTION_KEY=your_key_here  # Generated via scripts/generate_encryption_key.py
```

## Monitoring

### Logs
```bash
# Docker logs
docker-compose logs -f astrology-bot

# Application logs (if running directly)
# Logs appear in terminal with timestamps
# Note: Encrypted chats show as "encrypted message" in logs
```

### Queue Status
```bash
# Check queue via HTTP
curl http://localhost:8282/queue/status

# Check via RabbitMQ Management
http://192.168.0.200:15672
# Login: guest/guest
```

## Troubleshooting

### Bot not responding
1. Check if bot is running: `docker-compose ps`
2. Check logs: `docker-compose logs -f astrology-bot`
3. Verify RabbitMQ: `python tests/test_rabbitmq.py`
4. Purge old messages: `python scripts/purge_queue.py`

### Ollama errors
1. Verify models: `ollama list`
2. Pull if missing: `ollama pull gpt-oss:latest`
3. Check Ollama: `curl http://localhost:11434/api/tags`

### Database issues
1. Check connection: `python tests/test_connections.py`
2. Run migrations: `alembic upgrade head`
3. Check current version: `alembic current`

### Memory (Mem0) issues
1. Test connection: `python tests/test_mem0_connection.py`
2. Check Mem0 health: `curl http://192.168.0.200:8085/health`

### Encryption issues
1. Test encryption: `python tests/test_encryption.py`
2. Verify key is set in `.env`
3. Check if key is valid (32 URL-safe base64-encoded bytes)
4. If key is lost, encrypted messages **cannot** be recovered

### Regenerate Encryption Key
```bash
# Generate new key
python scripts/generate_encryption_key.py

# Update .env with new key
# WARNING: Old encrypted messages cannot be decrypted with new key!
```

## Performance Tips

1. **Single GPU**: Set `RABBITMQ_WORKERS=1`
2. **Multiple GPUs**: Set `RABBITMQ_WORKERS=<num_gpus>`
3. **Disable thinking for speed**: `ENABLE_THINKING=false`
4. **Reduce token limit**: `THINKING_MAX_TOKENS=300`
5. **Use SSD for PostgreSQL and Redis**
6. **Encryption overhead**: <1ms per message, minimal impact

## Security Best Practices

1. **Encryption Key**:
   - Store encryption key securely
   - Never commit `.env` to version control
   - Back up encryption key separately
   - Rotate keys periodically (requires re-encryption)

2. **Database Security**:
   - Use strong PostgreSQL passwords
   - Enable SSL for database connections in production
   - Regularly backup encrypted and unencrypted data

3. **Access Control**:
   - Limit admin script access
   - Use environment-specific configurations
   - Monitor user activity logs

## Monetization Ready

The bot includes priority system for paid tiers:
- Free users: Priority 5 (default)
- Basic plan: Priority 3-4
- Premium plan: Priority 1-2
- **Privacy tier**: Encryption as premium feature

Implement payment gateway and update user priority upon payment.

## License

MIT License - See LICENSE file for details

## Contributing

Pull requests are welcome! For major changes:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Support

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Docs: [Wiki](https://github.com/your-repo/wiki)

## Acknowledgments

- Semantic Kernel by Microsoft
- Ollama for local LLM inference
- python-telegram-bot community
- Mem0 for memory management
- Fernet encryption from cryptography.io

---

Made with ❤️ and ✨ cosmic energy • Protected with 🔐 encryption