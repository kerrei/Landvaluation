import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt
from feature_engineering import preprocess_data, feature_engineering
try:
    from database.connect import get_db_connection
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
    from connect import get_db_connection

def load_data_from_db():
    conn = get_db_connection()
    query = "SELECT * FROM properties;"  # Update table name/fields as needed
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def train_and_evaluate(model_path):
    df = load_data_from_db()
    df = preprocess_data(df)
    df_encoded = feature_engineering(df)
    X = df_encoded.select_dtypes(include=['number']).drop(['price_avg', 'price_avg_capped'], axis=1, errors='ignore')
    y = df_encoded['price_avg_capped']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"✅ RMSE: {rmse:,.0f} KES")
    print(f"✅ R² Score: {r2:.3f}")
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--')
    plt.xlabel("Actual Prices")
    plt.ylabel("Predicted Prices")
    plt.title("Actual vs Predicted House Prices")
    plt.grid(True)
    plt.show()
    joblib.dump(model, model_path)
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, scoring='r2', cv=cv)
    print(f"✅ R² Scores from each fold: {np.round(scores, 3)}")
    print(f"✅ Mean R² Score: {scores.mean():.3f}")
    print(f"✅ Std Deviation: {scores.std():.3f}")

if __name__ == "__main__":
    model_path = "model.pkl"  # Save model in ML/
    train_and_evaluate(model_path)
