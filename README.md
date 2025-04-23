# Nikola Jokic Performance Prediction Model

# Overview

This model predicts Nikola Jokic’s Points + Rebounds + Assists (PRA) for upcoming NBA games using an XGBoost regression model trained with walk-forward validation. It incorporates engineered features such as rolling averages (3/5/10 games), season averages, head-to-head matchup stats, and opponent defensive metrics. Designed for fans, analysts, and bettors, the tool delivers real-time, data-driven forecasts that adapt dynamically throughout the 2024–25 season.

# Features

Season Average Stats

3, 5, 10-Game Rolling Average Stats

Head-to-Head Matchup Average Stats

Opponent Defensive Stats

# Directory Structure

data:

    build_rolling_opponent_stats.py

    xgboost_features.py

    linear_regression_features.py

data collection:

    scrapegamelogs.py

    defensivestatscrape.py

    jokic_gamelogs_without_teammate.py

models:

    xgboost:

        train.py

        predict.py

    linear regression:

        train.py
        
        predict.py

requirements.txt

README.md

LICENSE

# Future Implementations

Integrate injury-related statistics

Incorporate Vegas odds

Hyperparameter Optimization

Expand training dataset with previous seasons

Enhanced opponent team defensive metrics

Automate daily game-day predictions

Visualize predictions vs. actual outcomes and betting lines

Transition to deep learning frameworks (PyTorch/TensorFlow)

Implement an interactive dashboard for easy exploration and game-day usage

Expand support to multiple players

# License 

This project is licensed under the MIT License.

# Author 

Developed by Sibhi Sakthivel as part of a machine learning and sports analytics initiative. This project reflects an end-to-end data science pipeline—from raw data ingestion to real-time predictive modeling.