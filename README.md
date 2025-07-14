# Benzodiazepine Taper Generator

A Python tool for generating diazepam-based taper schedules that comply with the 2025 ASAM guideline. Produces patient instructions, pharmacy orders, EHR summary and pill counts.

## Features

- Converts various benzodiazepines to diazepam equivalents
- Generates patient-centered taper schedules
- Multiple taper speeds (slow, standard, fast, very fast, ultra fast)
- Optional final hold periods
- Generates pharmacy orders and pill counts
- Web API for integration

## Usage

### Command Line

```bash
python taper_gen.py --med clonazepam --dose 1 --speed standard --start 2025-07-15 --final-hold 6 3
```

### Web API

POST to `/taper` with JSON:

```json
{
  "med": "clonazepam",
  "dose": 1,
  "speed": "standard",
  "start": "2025-07-15",
  "final_hold": [6, 3]
}
```

## Supported Medications

- alprazolam
- clonazepam
- lorazepam
- temazepam
- oxazepam
- chlordiazepoxide
- diazepam

## Taper Speeds

- **slow**: 2.5% reduction every 28 days
- **standard**: 5% reduction every 21 days
- **fast**: 10% reduction every 14 days
- **very fast**: 15% reduction every 14 days
- **ultra fast**: 20% reduction every 7 days

## Deployment

This project is configured for deployment on Render.com with the included `render.yaml` file.

## License

MIT License - Copyright (c) 2025 Nicolas Lescano, MD, Professor of Clinical Psychiatry, University of Pennsylvania

## Reference

Based on the 2025 ASAM Benzodiazepine Tapering Guideline: [ASAM Guideline](https://downloads.asam.org/sitefinity-production-blobs/docs/default-source/guidelines/benzodiazepine-tapering-2025/bzd-tapering-document---final-approved-version-for-distribution-02-28-25.pdf?sfvrsn=5bdf9c81_4) 