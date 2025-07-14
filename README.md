# Benzodiazepine Taper Generator

A Python tool for generating diazepam-based taper schedules that comply with the 2025 ASAM guideline. Produces patient instructions, pharmacy orders, EHR summary and pill counts.

## Features

- Converts various benzodiazepines to diazepam equivalents
- Generates patient-centered taper schedules
- Multiple taper speeds (slow, standard, fast, very fast, ultra fast)
- Optional final hold periods
- Generates pharmacy orders and pill counts
- Web API for integration
- **NEW**: Beautiful React frontend with modern UI

## Quick Start

### Development

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Node.js dependencies:
   ```bash
   cd frontend && npm install
   ```

3. Run both frontend and backend:
   ```bash
   ./dev.sh
   ```

   Or run them separately:
   ```bash
   # Backend (port 10000)
   python app.py
   
   # Frontend (port 3000)
   cd frontend && npm start
   ```

### Production

The app is automatically deployed to Render.com with the included `render.yaml` configuration.

## Usage

### Web Interface

Visit the React frontend at `http://localhost:3000` (development) or your deployed URL for a beautiful, user-friendly interface.

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

## Frontend Features

- 🎨 Modern, responsive UI with Tailwind CSS
- 📱 Works on desktop, tablet, and mobile
- ⚡ Real-time form validation
- 🎭 Smooth animations and transitions
- 🖨️ Print functionality for schedules
- 📊 Detailed results display

## Tech Stack

### Backend
- Python 3.8+
- Flask
- Flask-CORS

### Frontend
- React 18 with TypeScript
- Tailwind CSS
- Framer Motion
- React Hook Form with Zod validation
- Lucide React icons

## Deployment

This project is configured for deployment on Render.com with the included `render.yaml` file. The build process automatically:

1. Installs Python dependencies
2. Installs Node.js dependencies  
3. Builds the React frontend
4. Serves the built files from Flask

## License

MIT License - Copyright (c) 2025 Nicolas Lescano, MD, Professor of Clinical Psychiatry, University of Pennsylvania

## Reference

Based on the 2025 ASAM Benzodiazepine Tapering Guideline: [ASAM Guideline](https://downloads.asam.org/sitefinity-production-blobs/docs/default-source/guidelines/benzodiazepine-tapering-2025/bzd-tapering-document---final-approved-version-for-distribution-02-28-25.pdf?sfvrsn=5bdf9c81_4) 