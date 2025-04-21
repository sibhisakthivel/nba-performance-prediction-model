# Nikola Jokic Performance Prediction Model

# Overview

A predictive modeling pipeline that projects Nikola Jokic's Points + Rebounds + Assists (PRA) using recent performance trends, opponent history, and machine learning. This tool is useful for fans, analysts, and bettors interested in data-driven projections.

# Features

Scrapes and stores full-season Jokic game logs

Computes rolling averages, season averages, and head-to-head stats

Trains a linear regression model using walk-forward validation

Predicts PRA for upcoming games based on real-time features

Modular design for adding new features and expanding to other players

# Directory Structure

data/                # Feature values and game logs
  feature_pipeline.py
  jokic_game_logs.csv
  jokic_features_24-25.csv

datacollection/      # Data scraping scripts
  scrapegamelogs.py
  jokic_gamelogs_without_teammate.py

src/                 # Core ML pipeline
  train.py           # Trains model and prints prediction accuracy
  main.py            # Outputs predicted PRA for upcoming matchup

notebooks/           # Placeholder for any exploratory notebooks
requirements.txt     # Python dependencies
README.md            # You're reading it!

# How It Works

# Data Collection

scrapegamelogs.py pulls Jokic's full game history from the NBA API

jokic_gamelogs_without_teammate.py filters games based on teammate availability

# Feature Engineering

feature_pipeline.py calculates:

    Rolling 10-game PRA average

    Season average PRA

    Head-to-head average PRA vs each opponent

Outputs jokic_features_24-25.csv

# Model Training

train.py performs walk-forward linear regression:

    For each game: uses only prior games as training set

    Computes mean absolute error (MAE)

    Saves predictions to data/jokic_model_predictions.csv

# Prediction

main.py prompts: Who is Jokic's next opponent?

Uses most recent season/rolling stats + H2H vs selected team

Applies model weights to generate PRA prediction

# Example Usage

$ python src/train.py
📊 Mean Absolute Error (MAE): 11.37

$ python src/main.py
📝 Who is Jokic's next opponent (e.g., LAL)? LAC
📊 Predicted PRA: 52.94

# Requirements

Python 3.9+

pandas

scikit-learn

Install dependencies:
pip install -r requirements.txt

# Future Implementations

Add features for teammate injury context

Auto-detect Jokic's next matchup from NBA API

Incorporate betting lines to compare with model predictions

Expand support to multiple players

Explore non-linear or ensemble models

# License 

This project is licensed under the MIT License.

# Author 

Developed by Sibhi Sakthivel as part of a machine learning and sports analytics initiative. This project reflects an end-to-end data science pipeline—from raw data ingestion to real-time predictive modeling.