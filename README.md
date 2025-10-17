# NBA Player Performance Prediction Model

Predicts NBA player statistical performances using machine learning to identify sportsbook betting line discrepancies.

## Overview

This repository forms the foundation for an ensemble-based NBA player performance prediction system that integrates deep learning, machine learning, and statistical modeling techniques. It includes an automated ETL pipeline for real-time data ingestion and feature simulation, along with modular model architecture outlines that can scale to more complex databases and simulation frameworks.

The system is designed to explore how machine learning can simulate player performance under varying contextual conditions and opponent matchups, bridging traditional statistical modeling with modern AI experimentation.

## Key Objectives

- Develop a modular ensemble framework that integrates deep learning, machine learning, and statistical models for player performance simulation and prediction
- Automate end-to-end data ingestion, transformation, and feature simulation across multi-season NBA datasets
- Enhance model interpretability and robustness through feature attribution (SHAP), comparative visualization, and LLM-assisted diagnostic analysis of ensemble outputs
- Develop scalable, simulation-ready pipelines and schemas that support model evaluation, optimization, and expansion into multi-agent, physics-informed sports simulations

## Tools & Libraries

Core environment built in **Python**, integrating end-to-end data processing, modeling, and simulation workflows.

- **SQL**, **PostgreSQL (psycopg2)** — relational data storage, query design, and ETL integration  
- **pandas**, **numpy** — data manipulation, aggregation, and feature computation  
- **nba_api** — real-time NBA data access and ingestion  
- **scikit-learn**, **XGBoost** — ensemble modeling, regression, and performance evaluation  
- **SHAP**, **StatsModels**, **SciPy** — interpretability, statistical analysis, and simulation validation  
- **matplotlib**, **seaborn** — visualization and model diagnostics  
- **joblib** — lightweight model persistence and caching  
- **PyTorch** *(experimental)* — deep learning architectures for behavioral and simulation-based modeling  
- **Git**, **JupyterLab** — version control, experiment documentation, and reproducible research workflows  
- *(In progress)* **Optuna**, **FastAPI**, **Docker** — optimization, deployment, and pipeline orchestration  

## Repository Structure

- `data/` — stores all raw, processed, and reference datasets used across modeling and simulation pipelines  
- `data_collection/` — automated data ingestion and update scripts leveraging the NBA API and PostgreSQL integration  
- `data_processing/` — data cleaning, normalization, patching, and transformation modules forming the ETL backbone  
- `models/` — machine learning and deep learning prototypes, ensemble frameworks, and experimental model artifacts  
- `.gitignore` — defines ignored files and large data directories (e.g., model outputs, features)  
- `requirements.txt` — specifies key Python dependencies and reproducible environment setup  
- `LICENSE` — defines intellectual property and usage permissions  
- `README.md` — repository overview, objectives, and technical documentation  

## License  
This project is licensed under a **custom restricted-use license**.  
See the [`LICENSE`](./LICENSE) file for details regarding permitted usage and distribution.  

## Author  
Developed by **Sibhi Sakthivel** as part of a broader **machine learning and sports analytics initiative**.  
This repository serves as the foundation for an end-to-end predictive modeling system, integrating automated data pipelines, advanced feature engineering, and ensemble learning methods to analyze player performance and guide betting decision-making.
