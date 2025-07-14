# Benzodiazepine Taper Generator Web App

A web-based application for generating safe, evidence-based benzodiazepine tapering schedules according to clinical guidelines.

## Features

- **Multi-Medication Support**: Convert various benzodiazepines to diazepam equivalents
- **Flexible Tapering**: Slow, standard, and fast tapering protocols
- **Smart Dosing**: Automatic dose splitting and pill combination optimization
- **Professional Output**: Patient instructions, EHR summaries, and pharmacy orders
- **Modern UI**: Responsive design with intuitive user interface
- **Export Options**: Print, PDF, and CSV export capabilities

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd bzd-taper-gen
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web app**
   Open your browser and navigate to: `http://localhost:5000`

## Usage

### Basic Workflow

1. **Select Medication**: Choose your current benzodiazepine medication
2. **Enter Dose**: Input your current daily dose in milligrams
3. **Choose Taper Speed**: Select slow, standard, or fast tapering protocol
4. **Set Start Date**: Choose when to begin the taper
5. **Generate Plan**: Click "Generate Taper Plan" to create your schedule

### Output Sections

- **Patient Instructions**: Step-by-step dosing schedule with safety warnings
- **Schedule Summary**: Overview of the entire taper protocol
- **Pharmacy Orders**: Detailed prescriptions for each phase
- **Pill Count**: Total medication requirements

### Safety Features

- Automatic conversion to diazepam (recommended for tapering)
- Dose validation and rounding
- Safety warnings and disclaimers
- Professional medical formatting

## Technical Details

### Architecture
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Data**: JSON-based configuration
- **Deployment**: Ready for Heroku, Vercel, or Docker

### Key Components

- `app.py`: Main Flask application
- `taper_gen.py`: Core tapering algorithm
- `templates/index.html`: Main web interface
- `static/css/style.css`: Custom styling
- `static/js/app.js`: Frontend functionality

### API Endpoints

- `GET /`: Main application page
- `POST /generate`: Generate taper plan
- `GET /api/medications`: List available medications
- `GET /api/taper_speeds`: List taper speed options
- `GET /api/strengths/<medication>`: Get available strengths for medication

## Medical Disclaimer

⚠️ **Important**: This tool generates tapering schedules based on clinical guidelines but should not replace professional medical advice. Always consult with your healthcare provider before making any changes to your medication regimen.

## Development

### Project Structure
```
bzd-taper-gen/
├── app.py                 # Flask application
├── taper_gen.py          # Core tapering logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main web template
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── app.js        # Frontend JavaScript
```

### Adding New Features

1. **New Medications**: Add to `EQUIVALENTS_TO_DIAZEPAM_MG` in `taper_gen.py`
2. **New Taper Speeds**: Add to `TAPER_SPEEDS` in `taper_gen.py`
3. **UI Enhancements**: Modify `templates/index.html` and `static/css/style.css`
4. **Functionality**: Extend `static/js/app.js` for new features

### Testing

Run the application and test with various inputs:
```bash
python app.py
```

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

#### Heroku
1. Create `Procfile`:
   ```
   web: python app.py
   ```
2. Deploy to Heroku

#### Docker
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["python", "app.py"]
   ```

#### Vercel
1. Create `vercel.json`:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and clinical use. Please ensure compliance with local medical regulations.

## Support

For issues or questions:
1. Check the documentation
2. Review the code comments
3. Create an issue in the repository

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Medical Guidelines**: Based on February 28, 2025 Joint Clinical Practice Guideline 