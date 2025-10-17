import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import sklearn
import seaborn as sns
import numpy as np
from scipy import ndimage

# def plot_tree_decision_function(tree, X, y, ax):
#     """Plot the different decision rules found by a `DecisionTreeClassifier`.

#     Parameters
#     ----------
#     tree : DecisionTreeClassifier instance
#         The decision tree to inspect.
#     X : dataframe of shape (n_samples, n_features)
#         The data used to train the `tree` estimator.
#     y : ndarray of shape (n_samples,)
#         The target used to train the `tree` estimator.
#     ax : matplotlib axis
#         The matplotlib axis where to plot the different decision rules.
#     """

#     h = 0.02
#     x_min, x_max = x.iloc[:, 0].min() - 1, X.iloc[:, 0].max() + 1
#     y_min, y_max = x.iloc[:, 1].min() - 1, X.iloc[:, 1].max() + 1

#     xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
#                          np.arange(y_min, y_max, h))

#     Z = tree.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
#     Z = Z.reshape(xx.shape)
#     faces = tree.tree_.apply(
#         np.c_[xx.ravel(), yy.ravel()].astype(np.float32))
#     faces = faces.reshape(xx.shape)
#     border = ndimage.laplace(faces) != 0
#     ax.scatter(X.iloc[:, 0], X.iloc[:, 1],
#                c=np.array(['tab:blue',
#                            'tab:red'])[y], s=60, alpha=0.7)
#     ax.contourf(xx, yy, Z, alpha=.4, cmap='RdBu_r')
#     ax.scatter(xx[border], yy[border], marker='.', s=1)
#     ax.set_xlabel(X.columns[0])
#     ax.set_ylabel(X.columns[1])
#     ax.set_xlim([x_min, x_max])
#     ax.set_ylim([y_min, y_max])
#     sns.despine(offset=10)
    
def plot_tree_decision_function(tree, X, y, ax):
    h = 0.02
    x_min, x_max = X.iloc[:, 0].min() - 1, X.iloc[:, 0].max() + 1
    y_min, y_max = X.iloc[:, 1].min() - 1, X.iloc[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    # Use predicted classes instead of probabilities
    Z = tree.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    ax.contourf(xx, yy, Z, alpha=0.4, cmap='RdBu')  # 2 solid colors

    # Scatter training points
    ax.scatter(X.iloc[:, 0], X.iloc[:, 1],
               c=y, cmap='RdBu', edgecolor='k', s=60, alpha=0.7)

    ax.set_xlabel(X.columns[0])
    ax.set_ylabel(X.columns[1])
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    sns.despine(offset=10)
    
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
            AND game_id LIKE '0022%';
            """)
    
    df = pd.read_sql(query, conn)
    df.sort_values(by="game_id")
    
    conn.close()
    return df

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import plot_tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import classification_report
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.model_selection import cross_val_score

if __name__ == "__main__":

    # === Decision Tree Model (Classification vs Regression): Minutes Played vs. Points Scored ===

    df = get_df()
    
    df["season_avg_minutes"] = df["minutes"].shift().expanding().mean()
    df["season_avg_fga"]     = df["field_goals_attempted"].shift().expanding().mean()
    # df["season_avg_fgm"]     = df["field_goals_made"].shift().expanding().mean()
    
    df["over25"] = (df["points"] > 25).astype(int)
    
    df = df.dropna().reset_index(drop=True)
    
    # x = df[["season_avg_minutes", "season_avg_fga", "season_avg_fgm"]]
    x = df[["season_avg_minutes", "season_avg_fga"]]
    y = df["over25"]

    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(x, y)

    for col, importance in zip(x.columns, model.feature_importances_):
        print(f"{col}: {importance:.3f}")
        
    plt.figure(figsize=(12, 6))
    plot_tree(model, feature_names=x.columns, class_names=["Under", "Over"], filled=True)
    
    fig, ax = plt.subplots()
    plot_tree_decision_function(model, x, y, ax=ax)
    
    plt.legend()
    plt.grid()
    # plt.show()

    y_pred = model.predict(x)
    print("Accuracy:", accuracy_score(y, y_pred))

    cm = confusion_matrix(y, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Under", "Over"])
    # disp.plot()
    # plt.show()
    
    y_proba = model.predict_proba(x)[:, 1]  # probability of "Over"
    fpr, tpr, _ = roc_curve(y, y_proba)

    plt.plot(fpr, tpr, label=f"AUC = {roc_auc_score(y, y_proba):.2f}")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    # plt.show()
    
    print(classification_report(y, y_pred, target_names=["Under", "Over"]))
    
    scores = cross_val_score(model, x, y, cv=5)
    print("Cross-val scores:", scores)
    print("Mean score:", scores.mean())

    # === Decision Tree Classifier Functions ===
    
    # model = DecisionTreeClassifier(max_depth=None, random_state=0)
    # model.fit(x, y)
    # model.feature_importances_
    # plot_tree(model, feature_names, class_names, filled)
    # plot_tree_decision_function(model, X, y, ax=ax)
    
    # from sklearn.metrics import accuracy_score
    # accuracy_score(y, y_pred)

    # from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
    # cm = confusion_matrix(y, y_pred)
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Under", "Over"])
    # disp.plot()
    # plt.show()
    
    # from sklearn.metrics import classification_report
    # print(classification_report(y, y_pred, target_names=["Under", "Over"]))
    
    # from sklearn.metrics import roc_curve, roc_auc_score
    # y_proba = model.predict_proba(x)[:, 1]  # probability of "Over"
    # fpr, tpr, _ = roc_curve(y, y_proba)
    
    # from sklearn.model_selection import cross_val_score
    # scores = cross_val_score(model, x, y, cv=5)
    # print("Cross-val scores:", scores)
    # print("Mean score:", scores.mean())
    # print("Standard deviation:", scores.std())
    