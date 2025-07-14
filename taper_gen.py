from datetime import timedelta, date
from collections import defaultdict
import datetime

TAPER_SPEEDS = {
    "slow": {"percent": 2.5, "interval_days": 28},
    "standard": {"percent": 5.0, "interval_days": 21},
    "fast": {"percent": 10.0, "interval_days": 14},
}

EQUIVALENTS_TO_DIAZEPAM_MG = {
    "alprazolam": 0.5,
    "clonazepam": 0.5,
    "lorazepam": 1.0,
    "temazepam": 10.0,
    "oxazepam": 15.0,
    "chlordiazepoxide": 25.0,
    "diazepam": 10.0,
}

AVAILABLE_STRENGTHS = {
    "diazepam": [10.0, 5.0, 2.0],
    "clonazepam": [2.0, 1.0, 0.5],
    "alprazolam": [2.0, 1.0, 0.5, 0.25],
}


def convert_to_diazepam(dose_mg, med_name):
    med_name = med_name.lower()
    if med_name not in EQUIVALENTS_TO_DIAZEPAM_MG:
        raise ValueError(f"Unsupported medication: {med_name}. Must be converted to diazepam before tapering.")
    ratio = 10.0 / EQUIVALENTS_TO_DIAZEPAM_MG[med_name]
    return round(dose_mg * ratio, 2)


def even_split(total, parts):
    base = round(total / parts, 2)
    split = [base] * parts
    split[-1] += round(total - sum(split), 2)
    return split


def can_achieve(dose, med_name):
    combo = get_pill_combination(dose, med_name)
    achieved = round(sum(k * v for k, v in combo.items()), 2)
    return achieved == dose


def get_pill_combination(dose_mg, med_name="diazepam"):
    strengths = sorted(AVAILABLE_STRENGTHS[med_name], reverse=True)
    remaining = dose_mg
    combo = {}

    for s in strengths:
        count = int(remaining // s)
        if count > 0:
            combo[s] = count
            remaining = round(remaining - count * s, 2)

    if 0 < remaining < min(strengths):
        closest = min(strengths, key=lambda x: abs(x - remaining))
        combo[closest] = combo.get(closest, 0) + 0.5

    return combo


def assign_split_doses(dose_mg, med_name, frequency):
    freq_map = {"once": 1, "bid": 2, "tid": 3}
    parts = freq_map[frequency]
    doses = even_split(dose_mg, parts)
    times = ["AM", "PM", "HS"][:parts]
    schedule = {}
    for time, d in zip(times, doses):
        schedule[time] = get_pill_combination(d, med_name)
    return schedule


def split_dose(dose_mg, med_name="diazepam", frequency="auto"):
    if frequency == "auto":
        once_combo = get_pill_combination(dose_mg, med_name)
        if dose_mg == round(sum(k * v for k, v in once_combo.items()), 2):
            return assign_split_doses(dose_mg, med_name, "once"), "once"

        for option in ["bid", "tid"]:
            doses = even_split(dose_mg, {"bid": 2, "tid": 3}[option])
            if all(can_achieve(d, med_name) for d in doses):
                return assign_split_doses(dose_mg, med_name, option), option

        return assign_split_doses(dose_mg, med_name, "tid"), "tid"
    else:
        return assign_split_doses(dose_mg, med_name, frequency), frequency


def generate_percent_taper_schedule(
    diazepam_dose_mg,
    taper_speed="standard",
    min_dose_mg=0.5,
    round_to=0.5,
    final_hold_days=None,
    final_hold_frequency_days=None,
    start_date=date.today(),
    dosing_frequency="auto",
):
    percent = TAPER_SPEEDS[taper_speed]["percent"]
    interval_days = TAPER_SPEEDS[taper_speed]["interval_days"]

    schedule = []
    current_dose = diazepam_dose_mg
    current_day = 1
    current_date = start_date
    week_number = 1
    step_count = 0
    max_steps = 50  # Prevent runaway schedules
    try:
        while current_dose > min_dose_mg:
            step_count += 1
            if step_count > max_steps:
                raise ValueError(f"Taper schedule would take more than {max_steps} steps. Try a faster taper speed or increase the minimum dose.")
            # Proactive date overflow check
            max_days = (datetime.date.max - current_date).days
            if (interval_days - 1) > max_days:
                raise ValueError("Taper schedule end date exceeds supported range. Please check input parameters (dose, speed, or start date). Try a faster taper, higher minimum dose, or later start date.")
            dose = round(current_dose, 2)
            dosing_schedule, actual_freq = split_dose(dose, frequency=dosing_frequency)
            end_date = current_date + timedelta(days=interval_days - 1)
            step = {
                "dose_mg": dose,
                "duration_days": interval_days,
                "start_day": current_day,
                "end_day": current_day + interval_days - 1,
                "start_date": current_date,
                "end_date": end_date,
                "week_label": f"Weeks {week_number}–{week_number + (interval_days // 7) - 1}",
                "dosing_frequency": actual_freq,
                "dosing_schedule": dosing_schedule,
            }
            schedule.append(step)
            reduction = current_dose * (percent / 100)
            current_dose = max(current_dose - reduction, min_dose_mg)
            current_dose = round(round_to * round(current_dose / round_to), 2)
            current_day += interval_days
            # Proactive date overflow check for next step
            max_days_next = (datetime.date.max - current_date).days
            if interval_days > max_days_next:
                raise ValueError("Taper schedule date increment exceeds supported range. Please check input parameters (dose, speed, or start date). Try a faster taper, higher minimum dose, or later start date.")
            current_date = current_date + timedelta(days=interval_days)
            if current_date.year > 2100:
                raise ValueError("Taper schedule exceeds year 2100. Please check input parameters.")
            week_number += (interval_days // 7)
    except (OverflowError, ValueError):
        raise ValueError("Taper schedule date calculation exceeds supported range. Please check input parameters (dose, speed, or start date). Try a higher starting dose, faster taper, or earlier start date.")

    final_schedule, actual_freq = split_dose(min_dose_mg, frequency=dosing_frequency)
    schedule.append({
        "dose_mg": min_dose_mg,
        "duration_days": interval_days,
        "start_day": current_day,
        "end_day": current_day + interval_days - 1,
        "start_date": current_date,
        "end_date": current_date + timedelta(days=interval_days - 1),
        "note": "final daily dose",
        "week_label": f"Weeks {week_number}–{week_number + (interval_days // 7) - 1}",
        "dosing_frequency": actual_freq,
        "dosing_schedule": final_schedule,
    })

    current_day += interval_days
    current_date += timedelta(days=interval_days)
    week_number += (interval_days // 7)

    if final_hold_days and final_hold_frequency_days:
        schedule.append({
            "dose_mg": min_dose_mg,
            "duration_days": final_hold_days,
            "frequency_days": final_hold_frequency_days,
            "start_day": current_day,
            "end_day": current_day + final_hold_days - 1,
            "start_date": current_date,
            "end_date": current_date + timedelta(days=final_hold_days - 1),
            "note": f"final hold every {final_hold_frequency_days} days",
            "week_label": f"Weeks {week_number}–{week_number + (final_hold_days // 7)}",
            "dosing_frequency": actual_freq,
            "dosing_schedule": final_schedule,
        })

    total_days = schedule[-1]["end_day"]
    return schedule, total_days


def create_bzd_taper_plan(starting_medication, starting_dose_mg, taper_speed,
                          round_to=0.5, final_hold_days=None, final_hold_frequency_days=None,
                          start_date=date.today(), dosing_frequency="auto", verbose=False):
    med_name = starting_medication.lower()
    if med_name != "diazepam":
        if verbose:
            print("\n⚠️ Per guideline, taper must be done using diazepam.")
        converted_dose = convert_to_diazepam(starting_dose_mg, med_name)
        if verbose:
            print(f"{starting_dose_mg} mg {starting_medication.title()} ≈ {converted_dose} mg diazepam")
    else:
        converted_dose = starting_dose_mg

    taper_schedule, total_days = generate_percent_taper_schedule(
        diazepam_dose_mg=converted_dose,
        taper_speed=taper_speed,
        round_to=round_to,
        final_hold_days=final_hold_days,
        final_hold_frequency_days=final_hold_frequency_days,
        start_date=start_date,
        dosing_frequency=dosing_frequency
    )

    return taper_schedule, total_days


def format_patient_instructions(schedule):
    instructions = [
        "⚠️ Do not change this schedule without consulting your prescriber.",
        "📆 Tapering Schedule:", ""
    ]
    for s in schedule:
        line = f"{s['week_label']} ({s['start_date'].strftime('%b %d, %Y')} to {s['end_date'].strftime('%b %d, %Y')}):"
        instructions.append(line)
        for time, combo in s["dosing_schedule"].items():
            dose_str = " + ".join([f"{v} × {k}mg" for k, v in combo.items()])
            instructions.append(f"  • {time}: {dose_str}")
        if "note" in s:
            instructions.append(f"  → Note: {s['note']}")
    instructions.append("\nIf you experience any withdrawal symptoms, contact your provider immediately.")
    return instructions


def format_ehr_summary(schedule, total_days):
    return f"Patient will taper off diazepam over {total_days} days using a {len(schedule)}-step protocol, ending at 0.5 mg daily per the February 28, 2025 Joint Clinical Practice Guideline."


def format_pharmacy_orders(schedule):
    orders = []
    for s in schedule:
        for time, combo in s["dosing_schedule"].items():
            time_phrase = {
                "AM": "in the morning",
                "PM": "in the afternoon",
                "HS": "in the evening"
            }.get(time, f"at {time}")
            total_days = s["duration_days"]

            for strength_mg, count_per_dose in combo.items():
                dose_phrase = f"Take {count_per_dose:.1f} tablet{'s' if count_per_dose != 1 else ''} by mouth {time_phrase}"
                total_dispense = int(round(count_per_dose * total_days))
                orders.append({
                    "date": s["start_date"].strftime("%B %d, %Y"),
                    "product": f"Diazepam {strength_mg} mg tablets",
                    "sig": f"Sig: {dose_phrase}",
                    "dispense": f"Disp: {total_dispense} tablets for {total_days} days"
                })
    return orders


def summarize_total_pills(schedule):
    total_pills = defaultdict(float)
    for step in schedule:
        duration = step["duration_days"]
        for combo in step["dosing_schedule"].values():
            for strength, count_per_dose in combo.items():
                total_pills[strength] += count_per_dose * duration
    return dict(sorted(total_pills.items(), reverse=True))


if __name__ == "__main__":
    plan, duration = create_bzd_taper_plan(
        starting_medication="clonazepam",
        starting_dose_mg=1.0,
        taper_speed="slow",
        final_hold_days=6,
        final_hold_frequency_days=3,
        start_date=date(2025, 7, 15),
        dosing_frequency="auto"
    )

    print("\n🧑‍⚕️ PATIENT INSTRUCTIONS:")
    for line in format_patient_instructions(plan):
        print(line)

    print("\n📄 EHR SUMMARY:")
    print(format_ehr_summary(plan, duration))

    print("\n💊 PHARMACY ORDERS:")
    for item in format_pharmacy_orders(plan):
        print(f"Date: {item['date']}\n  {item['product']}\n  {item['sig']}\n  {item['dispense']}\n")

    print("\n🧮 TOTAL PILLS NEEDED:")
    pill_summary = summarize_total_pills(plan)
    for strength, total in pill_summary.items():
        print(f"Diazepam {strength} mg: {int(round(total))} tablets")
