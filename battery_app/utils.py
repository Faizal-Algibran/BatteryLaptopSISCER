import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

def train_and_predict(features_list):
    # Membaca dataset CSV
    csv_path = os.path.join(os.getcwd(), 'laptop_battery_health_usage.csv')
    df = pd.read_csv(csv_path)

    # Label target: jika kesehatan < 75% maka PERLU_GANTI, jika tidak PRIMA
    df['status_label'] = df['battery_health_percent'].apply(lambda x: 'PERLU_GANTI' if x < 75 else 'PRIMA')
    
    X = df[['charging_cycles', 'battery_age_months', 'daily_usage_hours', 'avg_charge_limit_percent']]
    y = df['status_label']
    
    # Latih model Decision Tree
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X, y)
    
    # Prediksi data baru
    prediction = model.predict([features_list])
    return prediction[0]