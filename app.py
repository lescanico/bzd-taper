from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import date
import os
from taper_gen import convert_to_diazepam, generate_schedule, patient_instructions, ehr_summary, pharmacy_orders, pill_totals

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

@app.route("/taper", methods=["POST"])
def taper():
    data = request.get_json(force=True) or {}
    med = data.get("med")
    dose = data.get("dose")
    dosing_schedule = data.get("dosing_schedule", {})
    available_strengths = data.get("available_strengths", [10.0, 5.0, 2.0])
    
    if med is None or dose is None:
        return jsonify({"error": "'med' and 'dose' are required fields."}), 400
    try:
        dose = float(dose)
    except Exception:
        return jsonify({"error": "'dose' must be a number."}), 400
    speed = data.get("speed", "standard")
    start = data.get("start", str(date.today()))
    final_hold = data.get("final_hold")  # Should be [days, every_n] or None

    if isinstance(med, str) and med.lower() != "diazepam":
        diaz = convert_to_diazepam(dose, med)
    else:
        diaz = dose

    # Update available strengths if provided
    if available_strengths:
        from taper_gen import AVAILABLE_STRENGTHS
        AVAILABLE_STRENGTHS["diazepam"] = available_strengths

    steps, total_days, warn = generate_schedule(
        diazepam_start_mg=diaz,
        speed=speed,
        start=date.fromisoformat(start),
        final_hold=tuple(final_hold) if final_hold else None,
    )

    return jsonify({
        "warn": warn,
        "patient_instructions": patient_instructions(steps),
        "ehr_summary": ehr_summary(steps, total_days),
        "pharmacy_orders": pharmacy_orders(steps),
        "pill_totals": pill_totals(steps),
    })

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000) 