# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher
- Git

## Backend Setup

1. Create and activate a virtual environment:
```bash
# Using conda
conda create -n trading_env python=3.8
conda activate trading_env

# Or using venv
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

2. Install core dependencies:
```bash
pip install -r requirements.txt
```

3. Install the project in development mode:
```bash
pip install -e .
```

4. (Optional) Install additional ML components:
```bash
pip install -e ".[ml]"  # Machine Learning components
pip install -e ".[analysis]"  # Technical Analysis components
pip install -e ".[dev]"  # Development tools
```

## Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

## Database Setup

1. Start InfluxDB using Docker:
```bash
docker run -d \
  --name influxdb \
  -p 8086:8086 \
  influxdb:latest
```

2. Update the database configuration in `config.yaml`:
```yaml
database:
  type: influxdb
  url: http://localhost
  port: 8086
  username: your_username
  password: your_password
  database: trading_data
  org: your_org
  bucket: market_data
```

## Running the Application

1. Start both backend and frontend servers:
```bash
./start_dev.sh
```

Or start them separately:

2. Start the backend server:
```bash
uvicorn src.infrastructure.api.main:app --reload --port 8000
```

3. Start the frontend development server:
```bash
cd frontend
npm start
```

## Accessing the Application

- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Troubleshooting

1. If you encounter dependency conflicts:
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

2. If the frontend build fails:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

3. If you get InfluxDB connection errors:
- Verify InfluxDB is running: `docker ps`
- Check logs: `docker logs influxdb`
- Ensure config.yaml has correct credentials

## Development Setup

1. Install development tools:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest tests/
```

3. Format code:
```bash
black src/
```

4. Lint code:
```bash
flake8 src/
```

## Common Issues

1. **Port Conflicts**: If ports 3000 or 8000 are in use:
- Backend: Use `uvicorn src.infrastructure.api.main:app --reload --port 8001`
- Frontend: Update `package.json` with `"start": "PORT=3001 react-scripts start"`

2. **Python Version Conflicts**: 
- Use `conda create` with specific Python version
- Or use `pyenv` to manage Python versions

3. **Node Version Issues**:
- Use `nvm` to manage Node.js versions
- Recommended: Node.js 14.x or higher

## Next Steps

After installation:
1. Review the API documentation at http://localhost:8000/docs
2. Check the frontend dashboard at http://localhost:3000
3. Configure your preferred symbols in config.yaml
4. Start developing new features!
