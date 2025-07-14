from flask import Flask, render_template, request, jsonify, session
from datetime import date, timedelta
from collections import defaultdict
import json

# Import existing taper logic
from taper_gen import (
    TAPER_SPEEDS, EQUIVALENTS_TO_DIAZEPAM_MG, AVAILABLE_STRENGTHS,
    convert_to_diazepam, create_bzd_taper_plan,
    format_patient_instructions, format_ehr_summary, 
    format_pharmacy_orders, summarize_total_pills
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change in production

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_taper():
    try:
        data = request.get_json()
        
        # Extract form data
        starting_medication = data.get('medication', '').lower()
        starting_dose = float(data.get('dose', 0))
        taper_speed = data.get('speed', 'standard')
        start_date_str = data.get('start_date', date.today().isoformat())
        dosing_frequency = data.get('frequency', 'auto')
        
        # Parse start date
        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f"Invalid date format: {start_date_str}. Use YYYY-MM-DD format."
            }), 400
        
        # Generate taper plan
        plan, total_days = create_bzd_taper_plan(
            starting_medication=starting_medication,
            starting_dose_mg=starting_dose,
            taper_speed=taper_speed,
            start_date=start_date,
            dosing_frequency=dosing_frequency,
            verbose=False
        )
        
        # Format outputs
        patient_instructions = format_patient_instructions(plan)
        ehr_summary = format_ehr_summary(plan, total_days)
        pharmacy_orders = format_pharmacy_orders(plan)
        pill_summary = summarize_total_pills(plan)
        
        return jsonify({
            'success': True,
            'plan': plan,
            'total_days': total_days,
            'patient_instructions': patient_instructions,
            'ehr_summary': ehr_summary,
            'pharmacy_orders': pharmacy_orders,
            'pill_summary': pill_summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/medications')
def get_medications():
    return jsonify(list(EQUIVALENTS_TO_DIAZEPAM_MG.keys()))

@app.route('/api/taper_speeds')
def get_taper_speeds():
    return jsonify(TAPER_SPEEDS)

@app.route('/api/strengths/<medication>')
def get_strengths(medication):
    medication = medication.lower()
    if medication in AVAILABLE_STRENGTHS:
        return jsonify(AVAILABLE_STRENGTHS[medication])
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000) 