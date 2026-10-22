# Sentiment Analysis of Product Reviews

[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.1-646CFF.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An undergraduate research project (UROP) focusing on cross-platform sentiment analysis of e-commerce customer reviews across major platforms: **Amazon**, **Flipkart**, **Myntra**, and **Meesho**.

---

## 📌 Project Overview

E-commerce customers post millions of reviews across different shopping platforms with varying tones, rating distributions, and priorities (e.g., pricing, quality, delivery, fit). This project provides:
- **Cross-Platform Sentiment Aggregation**: Unified analysis and comparative sentiment metrics across four major marketplaces.
- **Interactive Web Dashboard**: Modern, responsive analytics dashboard built with React 19 and Vite.
- **Sentiment Breakdown & Metrics**: Highlighting dominant sentiments, platform winners, average ratings, and sample reviews per platform.

---

## 📂 Repository Structure

```
.
├── Datasets/                 # Dataset documentation and schema guides
│   └── README.md             # Data sources and platform metadata
├── sentiment-dashboard/      # React + Vite interactive dashboard
│   ├── public/               # Public assets and icons
│   ├── src/
│   │   ├── assets/           # Application graphics and logos
│   │   ├── App.jsx           # Core dashboard UI component
│   │   ├── App.css           # Component styles
│   │   ├── index.css         # Modern glassmorphism design tokens & styles
│   │   ├── main.jsx          # React DOM entry point
│   │   └── mockData.js       # Sentiment evaluation & data simulation service
│   ├── index.html            # Main HTML template
│   ├── package.json          # Node dependencies and scripts
│   └── vite.config.js        # Vite build configuration
└── README.md                 # Project documentation
```

> **Note on Datasets**: The raw dataset files (~50GB+ of TSV and CSV review data from Amazon, Flipkart, Myntra, and Meesho) are excluded from this repository via `.gitignore` to comply with GitHub's storage constraints. Please refer to [`Datasets/README.md`](Datasets/README.md) for details on data acquisition and format.

---

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18 or higher recommended)
- `npm` or `yarn`

### Setup & Running the Dashboard

1. Navigate to the dashboard directory:
   ```bash
   cd sentiment-dashboard
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Build for production:
   ```bash
   npm run build
   ```

---

## 🎨 Features & Highlights

- **Dynamic Platform Winner Evaluation**: Identifies which platform has the most favorable consumer sentiment for a given search query.
- **Sentiment Distribution Bars**: Visual positive, neutral, and negative sentiment distribution bars per marketplace.
- **Curated Sample Reviews**: Real-time inspection of sample reviews labeled with model confidence scores.
- **Dark Glassmorphism Interface**: Sleek dark UI with animated transitions, responsive cards, and accessible typography.

---

## 🛠️ Tech Stack

- **Frontend Framework**: React 19
- **Build Tool**: Vite 8
- **Icons**: Lucide React
- **Linter**: Oxlint
- **Styling**: Vanilla CSS (CSS Variables, Flexbox/Grid, Glassmorphism)
