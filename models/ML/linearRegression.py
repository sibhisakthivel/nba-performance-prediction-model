import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import sklearn

def get_connection():
    return psycopg2.connect(
        dbname="nba",
        user="postgres",
        password="sibi",
        host="localhost",
        port="5432"
    )
    
def get_df():
    conn = get_connection()
    query = (f"""
            SELECT game_id, points, minutes, field_goals_attempted, field_goals_made 
            FROM boxscore_traditional_v3 t 
            WHERE person_id = '203999'
            AND t.season = 2024 
            AND game_id LIKE '00224%';
            """)
    
    df = pd.read_sql(query, conn)
    df.sort_values(by="game_id")
    
    conn.close()
    return df
    
from sklearn.linear_model import LinearRegression
    
if __name__ == "__main__":

    # === Linear Regression Model: Minutes Played vs. Points Scored ===
    
    df = get_df()
    
    df["season_avg_minutes"] = df["minutes"].shift().expanding().mean()
    df["season_avg_fga"]     = df["field_goals_attempted"].shift().expanding().mean()
    df["season_avg_fgm"]     = df["field_goals_made"].shift().expanding().mean()
    
    df = df.dropna().reset_index(drop=True)
    
    # x = df[['season_avg_minutes', 'season_avg_fga', 'season_avg_fgm']].values.reshape(-1, 3)
    x = df[['season_avg_minutes', 'season_avg_fga', 'season_avg_fgm']]
    y = df['points'].values
    
    model = LinearRegression()
    model.fit(x,y)

    for col, coef in zip(x.columns, model.coef_):
        print(f"{col}: {coef:.3f}")

    y_pred = model.predict(x)

    plt.scatter(y, y_pred, alpha=0.7)
    plt.xlabel("Actual Points")
    plt.ylabel("Predicted Points")
    plt.title("Predicted vs Actual Points")
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')  # 45° line
    plt.grid()
    r2 = model.score(x, y)
    plt.text(y.min(), y.max(), f"R² = {r2:.2f}", fontsize=12)
    plt.show()
    
    # === Linear Regression Fuctions ===
    
    # model = LinearRegression()     # initialize
    # model.fit(X, y)                 # train / fit
    # model.intercept_               # bias term (baseline prediction)
    # model.coef_                    # slope(s) for each feature
    # model.predict(X_new)           # make predictions
    # model.score(X, y)              # R² (coefficient of determination)
    