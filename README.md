**Natural English Rewrite:** "Could you please help me draft a README file for this project?"

---

### Bazi Collection API & Visualization System

This repository contains a professional implementation of a Four Pillars of Destiny (四柱命理学) data processing system. It provides a structured interface for calculating elemental balances and generating visual energy reports based on birth metadata (元数据).

### Core Features

* **Automated Calculation Engine**: Processes birth dates and times to derive the Eight Characters (八字) and Day Master (日主) via a specialized core logic.
* **Energy Visualization**: Generates Five-Element (五行) energy charts delivered as Base64-encoded images for seamless frontend integration.
* **RESTful Architecture**: Implements a clean separation between the data processing backend and the interactive web interface.
* **Cross-Origin Support**: Features built-in Cross-Origin Resource Sharing (跨域资源共享) configurations to facilitate communication between different local or remote environments.

### Technology Stack

* **Backend**: Python 3.x, Flask
* **Frontend**: Vanilla JavaScript, HTML5, CSS3
* **Communication**: JSON-based RESTful API
* **Logic**: Custom `baazi_core` algorithm

### Project Structure

```text
├── app.py              # Flask application server and API routes
├── baazi_core.py       # Core logic for Bazi calculations and chart generation
├── index.html          # Frontend user interface
└── .gitignore          # Rules for excluding temporary files and cache
```

### Getting Started

#### Prerequisites

Ensure Python 3.x is installed on your system. You will also need the `flask` and `flask-cors` libraries.

#### Installation

1. Clone the repository to your local machine.
2. Install the necessary dependencies using pip:
   `pip install flask flask-cors`
3. Run the backend server:
   `python app.py`

#### Usage

1. Open the `index.html` file in any modern web browser.
2. Enter the birth year, month, day, and hour.
3. Click "开始数据计算" (Start Data Calculation) to receive the analysis report.

### API Documentation

#### POST /api/calculate

This endpoint accepts user time data and returns a structured analysis object.

**Request Body Example:**

```json
{
  "year": 1989,
  "month": 8,
  "day": 26,
  "hour": 1,
  "minute": 30
}
```

**Success Response:**

* **Status Code**: 200 OK
* **Content**: A JSON object containing the Bazi array, Day Master information, and a Base64 string for the energy chart.

### Maintenance Notes

* Ensure `baazi_core.py` remains in the same directory as `app.py`.
* Development mode is enabled by default in `app.py` for easier debugging.
* Future updates may include Data Ingestion (数据接入) for database persistence.
