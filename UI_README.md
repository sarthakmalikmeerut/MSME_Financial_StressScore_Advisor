# MSME Financial Stress Score Advisor - Flask UI

A modern, responsive web interface for monitoring and analyzing MSME (Micro, Small & Medium Enterprises) financial stress in real-time.

## Features

🎯 **Dashboard**
- Real-time statistics and KPIs
- Visual stress score distribution
- Recent alerts and notifications
- Quick access to key data

📊 **Score Management**
- View all MSME stress scores in tabular format
- Sort and filter by risk level
- Progress indicators for easy visualization
- Direct access to detailed MSME information

⚠️ **Alerts System**
- Monitor MSMEs exceeding stress threshold
- Color-coded risk levels (Low, Moderate, High, Critical)
- Quick action buttons
- Risk level definitions

💰 **Transaction Management**
- Add new transactions in real-time
- Support for multiple transaction types (Inflow, Outflow, EMI)
- Category-based organization
- Automatic stress score recalculation

🔍 **MSME Details**
- Comprehensive financial metrics
- Cash flow analysis
- EMI tracking
- Historical performance

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `flask>=2.3.0` - Web framework
- `requests>=2.31.0` - HTTP client for API calls
- `pathway` - Data streaming backend

### 2. Setup Environment Variables (Optional)

```bash
# Set the backend API URL (default: http://localhost:8000)
export API_BASE_URL=http://localhost:8000

# Set the stress threshold (default: 0.4)
export STRESS_THRESHOLD=0.4

# Set Flask debug mode (default: True)
export FLASK_DEBUG=True

# Set Flask port (default: 5000)
export FLASK_PORT=5000
```

Windows (PowerShell):
```powershell
$env:API_BASE_URL="http://localhost:8000"
$env:STRESS_THRESHOLD="0.4"
$env:FLASK_DEBUG="True"
$env:FLASK_PORT="5000"
```

## Running the UI

### Option 1: Direct Execution

```bash
python ui/app.py
```

The UI will be available at: **http://localhost:5000**

### Option 2: Using Flask CLI

```bash
flask --app ui.app run
```

### Option 3: Production Mode

```bash
python -m gunicorn -w 4 -b 0.0.0.0:5000 ui.app:app
```

## Project Structure

```
ui/
├── app.py                 # Main Flask application
├── static/
│   ├── css/
│   │   └── style.css      # Custom styling
│   └── js/
│       └── main.js        # Client-side JavaScript
└── templates/
    ├── base.htm           # Base template with navigation
    ├── dashboard.htm      # Main dashboard
    ├── scores.htm         # All scores view
    ├── alerts.htm         # Alerts view
    ├── msme_detail.htm    # Individual MSME details
    ├── add_transaction.htm # Transaction form
    └── error.htm          # Error pages
```

## API Routes

### Pages (HTML)

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Dashboard home page |
| `/scores` | GET | All MSME scores table |
| `/msme/<msme_id>` | GET | Individual MSME details |
| `/alerts` | GET | Financial stress alerts |
| `/add-transaction` | GET/POST | Add new transaction |
| `/health` | GET | API health check |

### API Endpoints (JSON)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/scores` | GET | All stress scores (JSON) |
| `/api/alerts` | GET | High-risk MSMEs (JSON) |
| `/add-transaction` | POST | Submit transaction data |

## Usage Examples

### Access Dashboard
Open in browser: `http://localhost:5000/`

### View All Scores
Navigate to: `http://localhost:5000/scores`

### View Specific MSME
Navigate to: `http://localhost:5000/msme/A1`

### Check Alerts
Navigate to: `http://localhost:5000/alerts`

### Add Transaction (JSON)
```bash
curl -X POST http://localhost:5000/add-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "msme_id": "A1",
    "amount": 50000,
    "type": "inflow",
    "category": "sales"
  }'
```

## Configuration

### API Backend Integration

The UI communicates with the backend API (usually FastAPI on port 8000) to:
- Fetch stress scores
- Retrieve MSME details
- Get active alerts
- Submit new transactions

Ensure the backend API is running before starting the UI:
```bash
# In another terminal
python -m uvicorn src.api:app --reload --port 8000
```

### Stress Threshold

The threshold determines which MSMEs are flagged as "at risk":
- **Default**: 0.4 (40%)
- **Critical**: ≥ 0.7 (Red)
- **High**: 0.5 - 0.69 (Orange)
- **Moderate**: 0.3 - 0.49 (Blue)
- **Low**: < 0.3 (Green)

## Troubleshooting

### Error: API Unreachable
- Ensure backend API is running on `http://localhost:8000`
- Check `API_BASE_URL` environment variable
- Verify network connectivity

### Port Already in Use
- Change port: `export FLASK_PORT=5001`
- Or kill existing process: `lsof -ti:5000 | xargs kill -9`

### Missing Dependencies
- Reinstall: `pip install -r requirements.txt --upgrade`
- Check Python version: `python --version` (Python 3.8+)

### Static Files Not Loading
- Clear browser cache (Ctrl+Shift+Delete)
- Check Flask `static` folder structure
- Verify file permissions

## Technology Stack

- **Backend**: Flask 2.3+
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript ES6+
- **HTTP Client**: Python Requests
- **Icons**: Font Awesome 6
- **Data**: Real-time from Pathway streaming

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## Performance Tips

- Enable caching headers in production
- Use CDN for static assets
- Implement database caching for frequent queries
- Monitor API response times

## Development

### Enable Debug Mode
```bash
export FLASK_DEBUG=True
python ui/app.py
```

### Auto-reload on Changes
Flask auto-reloads when debug mode is enabled.

### Access Debug Toolbar
Add Flask Debug Toolbar:
```bash
pip install flask-debugtoolbar
```

## Contributing

To extend the UI:
1. Add new routes to `ui/app.py`
2. Create corresponding HTML templates in `ui/templates/`
3. Add custom CSS to `ui/static/css/style.css`
4. Add JavaScript functionality to `ui/static/js/main.js`

## License

This project is part of the MSME Financial Stress Score Advisor system.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask documentation: https://flask.palletsprojects.com/
3. Check Bootstrap documentation: https://getbootstrap.com/

---

**Happy monitoring! 📊✨**
