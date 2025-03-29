import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBRanker
from supabase import create_client, Client
from sklearn.preprocessing import LabelEncoder


class XGBoostRanker:
    def __init__(self, model_path='xgboost_model.json', learning_rate=0.1, n_estimators=100):
        self.model_path = model_path
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.model = None
        self.supabase = self.connect_to_supabase()
        self.airline_encoding = {"Delta": 6.574, "Alaska": 6.438, "United": 6.090, "American": 6.084, "Southwest": 5.854, "JetBlue": 4.938, "Hawaiian": 4.891, "Spirit": 4.336, "Allegiant": 3.455, "Frontier": 2.235, "Other": 4.500}

        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.model = XGBRanker(objective='rank:pairwise',learning_rate=self.learning_rate,n_estimators=self.n_estimators)

    def connect_to_supabase(self):
        url = "https://rbdpujuypscjtdmddydc.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJiZHB1anV5cHNjanRkbWRkeWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMxNDQ2MTIsImV4cCI6MjA1ODcyMDYxMn0.fLF-cTy1uYFKd5Y_N8X9Bi03e9K4yurRksdjFajwBss"
        return create_client(url, key)

    def load_data_from_supabase(self):
        response = self.supabase.table("flight_query_results").select("*").execute()
        data = pd.DataFrame(response.data)
        return data
    
    def cycle_encode_time(self, time_str):
        try:
            dt = datetime.strptime(time_str, "%I:%M %p")
            minutes = dt.hour * 60 + dt.minute
        except:
            minutes = 0
    
        angle = 2 * np.pi * (minutes / 1440)
        return np.sin(angle), np.cos(angle)


    def preprocess_data(self, data):

        def parse_row_departure(row):
            sin_val, cos_val = self.cycle_encode_time(row['departure_time'])
            row['departure_sin'] = sin_val
            row['departure_cos'] = cos_val
            return row

        def parse_row_arrival(row):
            sin_val, cos_val = self.cycle_encode_time(row['arrival_time'])
            row['arrival_sin'] = sin_val
            row['arrival_cos'] = cos_val
            return row
        
        def encode_airlines(airline_str):
            airlines_list = [a.strip() for a in airline_str.split(',')]
            total = 0.0
            for a in airlines_list:
                if a in self.airline_encoding:
                    total += self.airline_encoding[a]
                else:
                    total += self.airline_encoding['Other']
            return total / len(airlines_list)

        data = data.apply(parse_row_departure, axis=1)
        data = data.apply(parse_row_arrival, axis=1)

        data['airlines'] = data['airlines'].apply(encode_airlines)

        def normalize_group(group):
            for col in ["flight_price", "duration_minutes", "airlines"]:
                group[col] /= group[col].max()
            return group
        

        data.drop(['departure_time', 'arrival_time'], axis=1, inplace=True)
        data['is_multi_airline'] = data['is_multi_airline'].astype(int)
        new_data = data.groupby('query_id', group_keys=False).apply(normalize_group)
        return new_data

    def train(self):
        data = self.load_data_from_supabase()
        data = self.preprocess_data(data)


        data = data.sort_values(by='query_id')
        query_ids = data['query_id'].unique()

        groups = data.groupby('query_id').size().to_numpy()

        X = data[['flight_price', 'num_stops', 'duration_minutes', 'departure_sin', 'departure_cos', 'arrival_sin', 'arrival_cos', 'airlines', 'is_multi_airline']]
        y = data['rank_in_results']

        self.model.fit(X, y, group=groups)
        self.save_model()


    def save_model(self):
        self.model.save_model(self.model_path)

    def load_model(self):
        self.model = XGBRanker()
        self.model.load_model(self.model_path)

    def predict(self, X):
        if self.model is None:
            raise Exception("Model is not trained. Please train the model before making predictions.")
        return self.model.predict(X)

    def update(self, X_new, y_new):
        if self.model is None:
            raise Exception("Model is not trained. Please train the model before updating.")
        self.model.fit(X_new, y_new, xgb_model=self.model_path)
        self.save_model()


