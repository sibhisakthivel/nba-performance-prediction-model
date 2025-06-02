# NBA Player Performance Prediction Model

Predicts NBA player statistical performances using machine learning to identify sportsbook betting line discrepancies.

## Overview

This project uses real-game and team-level data to predict NBA player performances — specifically points, rebounds, and assists. The model helps identify potentially mispriced sportsbook props by comparing data-driven projections to betting lines.

## Key Objectives

- Predict statistcal outputs using historical, contextual, and opponent-adjusted data
- Benchmark model performance using walk-forward validation
- Applies SHAP to explain which features most influence predictions

## Tools & Libraries

- **Python**, **pandas**, **numpy** — data manipulation
- **XGBoost**, **scikit-learn** — modeling and evaluation
- **SHAP** — feature attribution and model interpretability
- **joblib** — model persistence
- **nba_api** — real-time NBA data access

## Repo Structure

- `data/`: raw and processed datasets
- `models/`: model training, prediction, and artifacts
- `datacollection/`: NBA API-based data scraping
- `assets/`: visualizations (SHAP plots, etc.)
- `requirements.txt`: Python dependencies

## License 

MIT License — see `LICENSE` for details.

## Author 

Developed by Sibhi Sakthivel as part of a machine learning and sports analytics initiative. This project reflects an end-to-end data science pipeline—from raw data ingestion to real-time predictive modeling.