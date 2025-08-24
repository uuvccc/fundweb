# FundWeb - Fund Monitoring System

This is a Flask-based fund monitoring system for monitoring fund net asset value and share changes.

## Features

- Automatically fetch fund data
- Display fund net asset value changes
- Display fund share changes
- Provide API interface
- Scheduled task execution
- Web interface display

## Environment Variables

Before using this system, you need to configure the following environment variables:

- `SECRET_KEY` - Secret key for Flask application
- `FUND_API_URL` - Fund data API URL
- `DEFAULT_CUSTNOS` - Default customer number list, comma-separated, e.g.: `custno1,custno2`

## Installation and Running

### Using Docker (Recommended)

```bash
docker-compose up --build
```

### Local Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   # Copy sample configuration file
   cp .env.sample .env
   
   # Edit .env file and fill in actual values
   # On Windows, you can use an editor to open it, on Linux/Mac you can use:
   # nano .env or vim .env
   ```

3. Run the application:
   ```bash
   python run.py
   ```

## API Interfaces

- `GET /api/funds/today-changes?custno=<custno>` - Get today's fund changes
- `GET /api/funds/nav-changes?custno=<custno>` - Get fund net asset value changes
- `GET /api/funds/volume-changes?custno=<custno>` - Get fund share changes
- `GET /api/funds/by-date?date=<date>` - Get fund data for a specific date
- `GET /api/funds/compare?datef=<date_from>&datet=<date_to>` - Get fund data comparison for a date range
- `POST /api/funds/refresh` - Manually trigger data fetching

## Scheduled Tasks

The system uses APScheduler to execute scheduled tasks, with the default configuration to execute the data fetching task daily at 18:25.

## Security Notes

For security reasons, all sensitive information (such as API URL, customer numbers, etc.) should be configured through environment variables, and should not be hard-coded in the code.

## License

MIT