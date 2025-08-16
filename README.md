# 🏈 NFL Quarterback Data Analysis & Fantasy Strategy

This project scrapes and analyzes NFL quarterback performance data from [Pro-Football-Reference](https://www.pro-football-reference.com/), combining data engineering, statistics, and research-driven insights to inform 2025 fantasy football draft strategies.

It includes:
- Web scraping of multi-season QB stats
- Data cleaning and structuring
- Regression modeling to identify top performance indicators
- A written research report summarizing findings

---

## Features

- Scrapes passing stats from 2020–2024 NFL seasons
- Cleans and filters QB-specific data
- Builds a regression model for fantasy PPG
- Interprets key features influencing QB fantasy output
- Markdown and Word-based portfolio-ready analysis

---

## 🧰 Tech Stack

| Layer              | Technology / Library           |
|--------------------|--------------------------------|
| **Language**        | Python                         |
| **Web Scraping**    | `requests`, `beautifulsoup4`, `ssl` |
| **Data Handling**   | `pandas`                       |
| **Visualization**   | `matplotlib`                   |
| **Statistical Modeling** | `statsmodels`             |
| **Documentation**   | Markdown, PDF (`.pdf`)       |

---

## 📁 File Structure

```
📦 Project Root
├── QB_Rec.py                          # Regression and model analysis
├── webscraping.py                    # Web scraping and data prep
├── requirements.txt                  # Project dependencies
├── README.md                         # Project documentation
├── Fantasy_Football_QB_Analysis_Portfolio.pdf   # Full research report (pdf)
├── Fantasy_Football_QB_Analysis_Portfolio.md     # Markdown version for GitHub
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/nfl-qb-analysis.git
   cd nfl-qb-analysis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run web scraping**
   ```bash
   python webscraping.py
   ```

4. **Run regression analysis**
   ```bash
   python QB_Rec.py
   ```

---

## Research Report

A detailed portfolio-style report is available in both `.docx` and `.md` formats:

- `Fantasy_Football_QB_Analysis_Portfolio.docx`
- `Fantasy_Football_QB_Analysis_Portfolio.md`

---

## Acknowledgements

- [Pro-Football-Reference](https://www.pro-football-reference.com/) for public NFL data.
- Open-source Python ecosystem for data science.
