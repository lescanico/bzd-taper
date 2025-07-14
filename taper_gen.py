#!/usr/bin/env python3
"""
taper_gen.py
============

Generate diazepam-based taper schedules that comply with the 2025
ASAM guideline.  Produces patient instructions, pharmacy orders,
EHR summary and pill counts.

Run as a module::

    python taper_gen.py --med clonazepam --dose 1 --speed slow \
                        --start 2025-07-15 --final-hold 6 3
"""
from __future__ import annotations

import argparse
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Tuple, TypedDict

# ───────────────────────────────────────────────────────────── constants ──
ASAM_GUIDELINE_URL = (
    "https://downloads.asam.org/sitefinity-production-blobs/docs/default-source/"
    "guidelines/benzodiazepine-tapering-2025/bzd-tapering-document---final-approved-"
    "version-for-distribution-02-28-25.pdf?sfvrsn=5bdf9c81_4"
)

EQUIVALENTS_TO_DIAZEPAM_MG: Dict[str, float] = {
    "alprazolam": 0.5,
    "clonazepam": 0.5,
    "lorazepam": 1.0,
    "temazepam": 10.0,
    "oxazepam": 15.0,
    "chlordiazepoxide": 25.0,
    "diazepam": 10.0,
}

AVAILABLE_STRENGTHS: Dict[str, List[float]] = {
    "diazepam": [10.0, 5.0, 2.0],
    "clonazepam": [2.0, 1.0, 0.5],
    "alprazolam": [2.0, 1.0, 0.5, 0.25],
}

class SpeedConfig(TypedDict):
    label: str
    percent: float
    interval: int

SPEED_TABLE: List[SpeedConfig] = [
    {"label": "slow",        "percent": 2.5,  "interval": 28},
    {"label": "standard",    "percent": 5.0,  "interval": 21},
    {"label": "fast",        "percent": 10.0, "interval": 14},
    {"label": "very fast",   "percent": 15.0, "interval": 14},
    {"label": "ultra fast",  "percent": 20.0, "interval": 7},
]

# ───────────────────────────────────────────────────────────── helpers ────
def _format_tablet_count(n: float) -> str:
    """Pretty-print 0.5 as the half-tablet glyph."""
    return "½" if math.isclose(n, 0.5, abs_tol=1e-3) else str(int(n))


def _even_split(total: float, parts: int) -> List[float]:
    base = round(total / parts, 2)
    chunks = [base] * parts
    chunks[-1] += round(total - sum(chunks), 2)
    return chunks


def convert_to_diazepam(dose_mg: float, med: str) -> float:
    med = med.lower()
    if med not in EQUIVALENTS_TO_DIAZEPAM_MG:
        raise ValueError(f"Medication '{med}' not in equivalency table.")
    ratio = 10.0 / EQUIVALENTS_TO_DIAZEPAM_MG[med]
    return round(dose_mg * ratio, 2)


def _pill_combo(dose: float, med: str = "diazepam") -> Dict[float, float]:
    strengths = sorted(AVAILABLE_STRENGTHS[med], reverse=True)
    remaining, combo = dose, {}
    for s in strengths:
        qty = int(remaining // s)
        if qty:
            combo[s] = qty
            remaining = round(remaining - qty * s, 2)
    if 0 < remaining < min(strengths):
        closest = min(strengths, key=lambda x: abs(x - remaining))
        combo[closest] = combo.get(closest, 0) + 0.5
    return combo


def _can_make(dose: float, med: str) -> bool:
    target = round(sum(k * v for k, v in _pill_combo(dose, med).items()), 2)
    return math.isclose(target, dose, abs_tol=0.01)


def _assign_split(dose: float, med: str, freq: str) -> Dict[str, Dict[float, float]]:
    parts = {"once": 1, "bid": 2, "tid": 3}[freq]
    times = ["AM", "PM", "HS"][:parts]
    return {t: _pill_combo(d, med) for t, d in zip(times, _even_split(dose, parts))}


def _split_dose(dose: float, med: str = "diazepam", freq: str = "auto"
                ) -> Tuple[Dict[str, Dict[float, float]], str]:
    if freq != "auto":
        return _assign_split(dose, med, freq), freq
    if _can_make(dose, med):
        return _assign_split(dose, med, "once"), "once"
    for option, parts in (("bid", 2), ("tid", 3)):
        if all(_can_make(d, med) for d in _even_split(dose, parts)):
            return _assign_split(dose, med, option), option
    return _assign_split(dose, med, "tid"), "tid"

# ───────────────────────────────────────────────────────────── dataclass ──
@dataclass(frozen=True)
class TaperStep:
    dose_mg: float
    duration: int
    start_day: int
    end_day: int
    start_date: date
    end_date: date
    frequency: str
    schedule: Dict[str, Dict[float, float]]
    note: str | None = None

    @property
    def label(self) -> str:
        return f"Days {self.start_day}–{self.end_day}"

# ───────────────────────────────────────────────────────────── engine ─────
def generate_schedule(
    diazepam_start_mg: float,
    speed: str,
    *,
    min_mg: float = 0.5,
    round_to: float = 0.5,
    final_hold: Tuple[int, int] | None = None,
    start: date = date.today(),
    freq: str = "auto",
    max_steps: int = 50,
) -> Tuple[List[TaperStep], int, str | None]:
    i_speed = next(i for i, s in enumerate(SPEED_TABLE) if s["label"] == speed)
    warn: str | None = None
    steps: List[TaperStep] = []
    
    while i_speed < len(SPEED_TABLE):
        pct, interval = SPEED_TABLE[i_speed]["percent"], SPEED_TABLE[i_speed]["interval"]
        steps = []
        dose, day, cur = diazepam_start_mg, 1, start
        try:
            while dose > min_mg + 1e-3:
                if len(steps) >= max_steps:
                    raise RuntimeError("too_many_steps")
                if cur.toordinal() + interval - 1 >= date.max.toordinal():
                    raise RuntimeError("date_overflow")

                sched, f = _split_dose(dose, freq=freq)
                steps.append(
                    TaperStep(
                        dose, interval, day, day + interval - 1,
                        cur, cur + timedelta(days=interval - 1), f, sched)
                )
                # Calculate new dose with proper rounding
                new_dose = dose - (dose * pct / 100)
                rounded_dose = max(round(round_to * round(new_dose / round_to), 2), min_mg)
                # Ensure dose always decreases
                if math.isclose(rounded_dose, dose, abs_tol=1e-3):
                    if dose - round_to > min_mg:
                        rounded_dose = round(dose - round_to, 2)
                    else:
                        rounded_dose = min_mg
                dose = rounded_dose
                day += interval
                cur += timedelta(days=interval)

            # final plateau (only if not duplicate)
            if not math.isclose(steps[-1].dose_mg, min_mg, abs_tol=1e-3):
                sched, f = _split_dose(min_mg, freq=freq)
                steps.append(
                    TaperStep(min_mg, interval, day, day + interval - 1,
                              cur, cur + timedelta(days=interval - 1), f, sched, "final daily dose")
                )
                day += interval
                cur += timedelta(days=interval)

            # optional final-hold
            if final_hold:
                hold_days, every_n = final_hold
                sched, f = _split_dose(min_mg, freq=freq)
                steps.append(
                    TaperStep(min_mg, hold_days, day, day + hold_days - 1,
                              cur, cur + timedelta(days=hold_days - 1), f, sched,
                              f"final hold every {every_n} days")
                )
            return steps, steps[-1].end_day, warn

        except RuntimeError:
            i_speed += 1
            if i_speed < len(SPEED_TABLE):
                warn = f"Auto-accelerated taper to '{SPEED_TABLE[i_speed]['label']}' to remain ≤ {max_steps} steps."
            continue

    # exhausted ladder - return empty steps with warning
    return [], 0, "Used fastest speed but schedule still long."

# ───────────────────────────────────────────────────────────── presentation layer ─
def patient_instructions(steps: List[TaperStep]) -> List[str]:
    txt = [
        "⚠️  Do not alter this schedule without prescriber approval.",
        "📆  Benzodiazepine taper plan",
        "",
        f"Guideline reference: {ASAM_GUIDELINE_URL}",
    ]
    for s in steps:
        txt.append(f"{s.label} ({s.start_date:%b %d %Y} → {s.end_date:%b %d %Y}):")
        for t, combo in s.schedule.items():
            dose_str = " + ".join(f"{_format_tablet_count(q)} × {strg} mg" for strg, q in combo.items())
            txt.append(f"  • {t}: {dose_str}")
        if s.note:
            txt.append(f"  → {s.note}")
    txt.append("\nReport withdrawal symptoms to your provider immediately.")
    return txt


def ehr_summary(steps: List[TaperStep], total_days: int) -> str:
    return (f"Diazepam taper: {len(steps)} steps over {total_days} days, "
            f"ending at 0.5 mg daily (Feb 28 2025 guideline). Ref: {ASAM_GUIDELINE_URL}")


def pharmacy_orders(steps: List[TaperStep]) -> List[Dict[str, str]]:
    orders: List[Dict[str, str]] = []
    phr = {"AM": "in the morning", "PM": "in the afternoon", "HS": "in the evening"}
    for s in steps:
        for t, combo in s.schedule.items():
            for strength, q in combo.items():
                disp_each = math.ceil(q)       # count whole tablets
                dispense = disp_each * s.duration
                sig = (f"Take {_format_tablet_count(q)} tablet"
                       f"{'' if math.isclose(q,1,abs_tol=1e-3) else 's'} "
                       f"by mouth {phr.get(t,t.lower())}")
                orders.append({
                    "date": f"{s.start_date:%B %d %Y}",
                    "product": f"Diazepam {strength} mg tablet",
                    "sig": f"Sig: {sig}",
                    "disp": f"Disp: {dispense} tablets for {s.duration} days",
                })
    return orders


def pill_totals(steps: List[TaperStep]) -> Dict[float, int]:
    total: defaultdict[float, int] = defaultdict(int)
    for s in steps:
        for combo in s.schedule.values():
            for strg, q in combo.items():
                total[strg] += math.ceil(q) * s.duration
    return dict(sorted(total.items(), reverse=True))

# ────────────────────────────────────────────────────────── CLI / demo ──
def main() -> None:
    parser = argparse.ArgumentParser(description="Generate benzodiazepine taper")
    parser.add_argument("--med",      required=True, help="starting medication (e.g. clonazepam)")
    parser.add_argument("--dose",     required=True, type=float, help="starting dose in mg")
    parser.add_argument("--speed",    choices=[s["label"] for s in SPEED_TABLE],
                        default="standard", help="taper speed")
    parser.add_argument("--start",    type=lambda d: date.fromisoformat(d),
                        default=date.today(), help="start date YYYY-MM-DD")
    parser.add_argument("--final-hold", nargs=2, metavar=("DAYS", "EVERY_N"),
                        type=int, help="e.g. 6 3  →  6 days hold, dose every 3 days")
    args = parser.parse_args()

    diaz = (convert_to_diazepam(args.dose, args.med)
            if args.med.lower() != "diazepam" else args.dose)

    steps, total_days, warn = generate_schedule(
        diazepam_start_mg=diaz,
        speed=args.speed,
        start=args.start,
        final_hold=tuple(args.final_hold) if args.final_hold else None,
    )

    if warn:
        print("⚠️ ", warn, "\n")

    if not steps:
        print("❌ No valid taper schedule could be generated.")
        return

    print("🧑‍⚕️  PATIENT INSTRUCTIONS\n──────────────────────────")
    for ln in patient_instructions(steps):
        print(ln)

    print("\n📄  EHR SUMMARY\n──────────────")
    print(ehr_summary(steps, total_days))

    print("\n💊  PHARMACY ORDERS\n────────────────")
    for o in pharmacy_orders(steps):
        print(f"{o['date']}\n  {o['product']}\n  {o['sig']}\n  {o['disp']}\n")

    print("🧮  TOTAL PILLS NEEDED\n────────────────────")
    for strg, n in pill_totals(steps).items():
        print(f"Diazepam {strg} mg: {n} tablets")

if __name__ == "__main__":
    main()