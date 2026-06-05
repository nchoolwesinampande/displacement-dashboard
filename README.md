# Beneficiary Solutions Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An interactive dashboard for visualizing beneficiary progress along durable solutions pathways (Return, Local Integration, Relocation) in humanitarian displacement programming.

## 🎯 Overview

This dashboard was designed to support evidence-based programming for protracted displacement situations. It visualizes how displaced populations progress through solutions pathways, aligned with the **IASC Framework on Durable Solutions** and **OECD-DAC** evaluation criteria.

### Key Features

- **Sankey Diagrams**: Visualize beneficiary flow from displacement status through solutions pathways to achievement stages
- **Geographic Mapping**: Interactive cluster maps showing spatial distribution of beneficiaries
- **KPI Tracking**: Real-time metrics on programme reach and impact
- **Progress Analysis**: Multi-dimensional charts for monitoring and reporting
- **Filter Controls**: Dynamic filtering by region, pathway, stage, and date range

## 📸 Screenshots

*Screenshots will be added after deployment*

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly, Folium
- **Data Processing**: Pandas
- **Mapping**: Folium with MarkerCluster

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/displacement-solutions-dashboard.git
cd displacement-solutions-dashboard
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the dashboard:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
displacement-solutions-dashboard/
├── README.md
├── requirements.txt
├── app.py                      # Main Streamlit application
├── data/
│   ├── sample_data.csv         # Sample displacement dataset (generated)
│   └── generate_data.py        # Reproducible, internally-coherent data generator
├── components/
│   ├── __init__.py
│   ├── charts.py               # Minimal bar / funnel / trend charts
│   ├── sankey_diagram.py       # Sankey flow visualization
│   ├── map_visualization.py    # Geographic mapping
│   ├── indicator_cards.py      # KPI cards and target bars
│   └── filters.py              # Sidebar filter controls
├── utils/
│   ├── __init__.py
│   ├── theme.py                # Design tokens + Plotly styling helper
│   └── data_processing.py      # Data loading and processing
└── assets/
    └── custom.css              # Custom styling
```

## 📊 Data Schema

The dashboard expects data with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `beneficiary_id` | Unique identifier | BEN-001 |
| `registration_date` | Date of registration | 2024-01-15 |
| `region` | Geographic region | Baidoa |
| `district` | District within region | Baidoa Central |
| `displacement_status` | Current status | IDP, Returnee, Host Community |
| `solutions_pathway` | Chosen pathway | Return, Local Integration, Relocation |
| `pathway_stage` | Progress stage | Assessment, Planning, Implementation, Achieved |
| `household_size` | Number in household | 5 |
| `gender_hoh` | Gender of head of household | Male, Female |
| `shelter_status` | Housing situation | Emergency, Transitional, Permanent |
| `livelihood_support` | Received livelihood support | Yes, No |
| `documentation_status` | Legal documentation | None, Partial, Complete |
| `latitude` | GPS latitude | 2.0469 |
| `longitude` | GPS longitude | 45.3182 |

## 🎨 Customization

### Adding Your Own Data

Replace `data/sample_data.csv` with your own dataset following the schema above.

The bundled sample is synthetic but internally coherent — solutions pathways
respect displacement status, progress follows a realistic funnel, and shelter /
documentation / livelihood status improve with the pathway stage. Regenerate it
(reproducibly, via a fixed seed) with:

```bash
python data/generate_data.py
```

### Modifying Colors

Edit the color palettes in:
- `components/sankey_diagram.py` for flow diagram colors
- `components/map_visualization.py` for map marker colors
- `assets/custom.css` for overall theme

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Nchoolwe Progress Sinampande**
- LinkedIn: [Your LinkedIn]
- Portfolio: [Your Portfolio]

## 🙏 Acknowledgments

- Inspired by humanitarian programming frameworks from IOM, UNDP, and UN-Habitat
- Built with guidance from the IASC Framework on Durable Solutions
- Data visualization patterns informed by OECD-DAC evaluation criteria
