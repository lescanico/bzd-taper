from flask import Flask, request, jsonify
from datetime import date
from taper_gen import convert_to_diazepam, generate_schedule, patient_instructions, ehr_summary, pharmacy_orders, pill_totals

app = Flask(__name__)

@app.route("/taper", methods=["POST"])
def taper():
    data = request.get_json(force=True) or {}
    med = data.get("med")
    dose = data.get("dose")
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
def index():
    return "Benzodiazepine Taper Generator API"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000) 