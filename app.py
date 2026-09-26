from flask import Flask, render_template, jsonify, request
from engine import AMLEngine
import os

app = Flask(__name__)
engine = None

@app.before_request
def load_engine():
    global engine
    if engine is None:
        if os.path.exists("aml_dataset.csv"):
            engine = AMLEngine("aml_dataset.csv")
            engine.run_all_rules()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/risk-scores')
def get_risk_scores():
    if not engine: return jsonify({})
    # Filter only medium/high/critical
    alerts = {k: v for k, v in engine.risk_scores.items() if v['score'] >= 30}
    return jsonify(alerts)

@app.route('/api/graph')
def get_graph():
    if not engine: return jsonify({"nodes": [], "edges": []})
    return jsonify(engine.get_graph_data())

@app.route('/api/timeline/<account_id>')
def get_timeline(account_id):
    if not engine: return jsonify([])
    return jsonify(engine.get_account_timeline(account_id))

if __name__ == '__main__':
    # Run setup
    if not os.path.exists("aml_dataset.csv"):
        print("Generating data...")
        from data_gen import generate_aml_data
        generate_aml_data()
        
    app.run(host='0.0.0.0', port=5050, debug=True)
