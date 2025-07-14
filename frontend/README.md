# BZD Taper Generator Frontend

A modern React frontend for the Benzodiazepine Taper Generator API.

## Features

- 🎨 Beautiful, modern UI with Tailwind CSS
- 📱 Responsive design that works on all devices
- ⚡ Real-time form validation with React Hook Form
- 🎭 Smooth animations with Framer Motion
- 🖨️ Print functionality for generated schedules
- 📊 Detailed results display with patient instructions, EHR summary, and pharmacy orders

## Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Hook Form** with Zod validation
- **Lucide React** for icons

## Development

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ with Flask backend running

### Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. The app will open at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates a `build` folder that the Flask backend will serve.

## API Integration

The frontend communicates with the Flask backend at `/taper` endpoint. The backend should be running on port 10000 for development.

## Deployment

The frontend is automatically built and deployed with the backend on Render.com. The build process:

1. Installs Python dependencies
2. Installs Node.js dependencies
3. Builds the React app
4. Serves the built files from Flask

## Project Structure

```
frontend/
├── public/          # Static assets
├── src/
│   ├── App.tsx     # Main application component
│   ├── index.tsx   # React entry point
│   ├── index.css   # Global styles with Tailwind
│   └── lib/
│       └── utils.ts # Utility functions
├── package.json     # Dependencies and scripts
├── tailwind.config.js # Tailwind configuration
└── postcss.config.js  # PostCSS configuration
``` 