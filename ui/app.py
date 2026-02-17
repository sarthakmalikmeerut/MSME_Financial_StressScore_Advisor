"""
Flask UI for MSME Financial Stress Score Advisor
"""

from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_SORT_KEYS'] = False

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
STRESS_THRESHOLD = float(os.getenv('STRESS_THRESHOLD', 0.4))


def get_api_safe(endpoint, default=None):
    """Make a safe GET request to the API."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API Error: {e}")
    return default or {}


def post_api_safe(endpoint, data=None, default=None):
    """Make a safe POST request to the API."""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=5)
        if response.status_code in [200, 201]:
            return response.json()
    except Exception as e:
        print(f"API Error: {e}")
    return default or {}


def stress_level_color(score):
    """Return color class based on stress score."""
    if score >= 0.7:
        return 'danger'
    elif score >= 0.5:
        return 'warning'
    elif score >= 0.3:
        return 'info'
    else:
        return 'success'


def stress_level_text(score):
    """Return human-readable stress level."""
    if score >= 0.7:
        return 'Critical'
    elif score >= 0.5:
        return 'High'
    elif score >= 0.3:
        return 'Moderate'
    else:
        return 'Low'


@app.route('/')
def dashboard():
    """Main dashboard showing all stress scores and alerts."""
    scores_data = get_api_safe('/scores', {})
    scores = scores_data.get('scores', {})
    
    alerts_data = get_api_safe(f'/alerts?threshold={STRESS_THRESHOLD}', {})
    alerts = alerts_data.get('alerts', {})
    
    total_msmes = len(scores)
    critical_count = sum(1 for v in scores.values() if v.get('stress_score', 0) >= 0.7)
    high_count = sum(1 for v in scores.values() if 0.5 <= v.get('stress_score', 0) < 0.7)
    
    sorted_scores = sorted(
        scores.items(),
        key=lambda x: x[1].get('stress_score', 0),
        reverse=True
    )[:10]
    
    context = {
        'total_msmes': total_msmes,
        'critical_count': critical_count,
        'high_count': high_count,
        'alerts_count': len(alerts),
        'scores': sorted_scores,
        'alerts': sorted(alerts.items(), key=lambda x: x[1].get('stress_score', 0), reverse=True),
        'threshold': STRESS_THRESHOLD,
    }
    
    return render_template('dashboard.htm', **context)


@app.route('/scores')
def all_scores():
    """View all MSME stress scores in a table."""
    scores_data = get_api_safe('/scores', {})
    scores = scores_data.get('scores', {})
    
    sorted_scores = sorted(
        scores.items(),
        key=lambda x: x[1].get('stress_score', 0),
        reverse=True
    )
    
    context = {
        'scores': sorted_scores,
        'stress_level_color': stress_level_color,
        'stress_level_text': stress_level_text,
    }
    
    return render_template('scores.htm', **context)


@app.route('/msme/<msme_id>')
def msme_detail(msme_id):
    """View detailed information for a single MSME."""
    score_data = get_api_safe(f'/scores/{msme_id}', {})
    
    if not score_data or 'data' not in score_data:
        return render_template('error.htm', 
                             error_title='MSME Not Found',
                             error_message=f'No data found for MSME: {msme_id}'), 404
    
    msme_data = score_data['data']
    stress_score = msme_data.get('stress_score', 0)
    
    context = {
        'msme_id': msme_id.upper(),
        'data': msme_data,
        'stress_score': stress_score,
        'stress_level_color': stress_level_color(stress_score),
        'stress_level_text': stress_level_text(stress_score),
        'timestamp': score_data.get('timestamp'),
    }
    
    return render_template('msme_detail.htm', **context)


@app.route('/alerts')
def alerts_view():
    """View all MSMEs with high stress scores."""
    alerts_data = get_api_safe(f'/alerts?threshold={STRESS_THRESHOLD}', {})
    alerts = alerts_data.get('alerts', {})
    
    sorted_alerts = sorted(
        alerts.items(),
        key=lambda x: x[1].get('stress_score', 0),
        reverse=True
    )
    
    context = {
        'alerts': sorted_alerts,
        'alert_count': len(alerts),
        'threshold': STRESS_THRESHOLD,
        'stress_level_color': stress_level_color,
        'stress_level_text': stress_level_text,
    }
    
    return render_template('alerts.htm', **context)


@app.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    """Add a new transaction."""
    if request.method == 'POST':
        try:
            data = request.get_json() or request.form
            
            msme_id = data.get('msme_id', '').strip().upper()
            amount = float(data.get('amount', 0))
            trans_type = data.get('type', 'inflow')
            category = data.get('category', 'sales')
            
            if not msme_id or amount <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Please provide valid MSME ID and amount'
                }), 400
            
            result = post_api_safe('/transactions', {
                'msme_id': msme_id,
                'amount': amount,
                'type': trans_type,
                'category': category,
            })
            
            if result and 'status' in result:
                return jsonify({
                    'success': True,
                    'message': 'Transaction added successfully',
                    'data': result.get('transaction'),
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to add transaction'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 400
    
    return render_template('add_transaction.htm')


@app.route('/health')
def health():
    """API health check."""
    health_data = get_api_safe('/health', {})
    
    if health_data.get('status') == 'ok':
        return jsonify({'status': 'ok', 'api': health_data})
    else:
        return jsonify({
            'status': 'error',
            'message': 'API unreachable',
            'api_url': API_BASE_URL
        }), 503


@app.route('/api/scores', methods=['GET'])
def api_scores():
    """API endpoint to get all scores (JSON)."""
    scores_data = get_api_safe('/scores', {})
    return jsonify(scores_data)


@app.route('/api/alerts', methods=['GET'])
def api_alerts():
    """API endpoint to get alerts (JSON)."""
    threshold = request.args.get('threshold', STRESS_THRESHOLD, type=float)
    alerts_data = get_api_safe(f'/alerts?threshold={threshold}', {})
    return jsonify(alerts_data)


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('error.htm',
                         error_title='Page Not Found',
                         error_message='The page you are looking for does not exist.'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.htm',
                         error_title='Server Error',
                         error_message='An unexpected error occurred.'), 500


@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {
        'stress_level_color': stress_level_color,
        'stress_level_text': stress_level_text,
        'api_url': API_BASE_URL,
        'threshold': STRESS_THRESHOLD,
    }


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"🚀 Starting MSME UI on http://localhost:{port}")
    print(f"📊 Backend API: {API_BASE_URL}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
