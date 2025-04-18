# Nikola Jokic Performance Prediction Model

# Overview

This project uses machine learning to model Nikola Jokic’s game-by-game performance, including points, rebounds, assists, and other key stats. It is designed for use in sports analytics and player prop line evaluation.

The model currently performs:

Data ingestion from structured CSV logs

Feature extraction and transformation

Initial model training and evaluation

# Data Source

Data is based on Jokic’s official game logs scraped from NBA.com and stored in a CSV file. Features include:

Box score stats

Game date and opponent

Matchup type (home/away)

Win/loss outcomes

# Current Progress

✅ Preprocessing and feature engineering

✅ Game log parser (Python)

🔄 Initial model training and evaluation (in progress)

🔜 Integration with real-time APIs

# Features

Rolling averages (e.g., last 5 games)

Opponent-specific performance trends

Game location (home vs. away)

Win/loss binary indicator

Matchup parsing (e.g., @ vs vs.)

# Tech Stack

Language: Python

Libraries: Pandas, NumPy, Scikit-learn

Tools: Git, Jupyter, matplotlib

Environment: Local + GitHub

# Installation

Clone the repository:

git clone https://github.com/sibhisakthivel/nba-prediction-model-jokic.git
cd nba-prediction-model-jokic

Install dependencies:

pip install -r requirements.txt

Run the training script (once available):

python train.py

# Planned Improvements

Integrate real-time API data (e.g., injuries, odds)

Expand to cover multiple players and teams

Improve model accuracy using ensemble or neural models

Deploy a web interface to visualize predictions
