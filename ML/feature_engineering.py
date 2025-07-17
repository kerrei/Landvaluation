import os
import googlemaps
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
from textblob import TextBlob

GOOGLE_MAPS_API_KEY = "AIzaSyC3Cv9TTnsvXOJAgjYaXrUirnkiQJ4CC28"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import OneHotEncoder

def extract_price_range(price_str):
    matches = re.findall(r'\d[\d\s]*', str(price_str))
    numbers = [int(p.replace(' ', '')) for p in matches]
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    elif len(numbers) >= 2:
        return numbers[0], numbers[1]
    else:
        return None, None

def preprocess_data(df):
    df[['price_min', 'price_max']] = df['price'].apply(lambda x: pd.Series(extract_price_range(x)))
    df[['price_min', 'price_max']] = df[['price_min', 'price_max']].apply(pd.to_numeric, errors='coerce')
    df['price_avg'] = df[['price_min', 'price_max']].mean(axis=1)
    df['price_min'].fillna(df['price_min'].mean(), inplace=True)
    df['price_max'].fillna(df['price_max'].mean(), inplace=True)
    df['price_avg'].fillna(df['price_avg'].mean(), inplace=True)
    drop_cols = ['price', 'location', 'price_clean', 'price_numeric', 'price_original', 'price_outlier', 'price_category', 'location_clean', 'city_region']
    df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)
    df.rename(columns={'processed_date': 'date'}, inplace=True)
    return df

def categorize_price(price):
    if price < 5_000_000:
        return 'Affordable'
    elif price <= 12_000_000:
        return 'Mid-range'
    elif price <= 25_000_000:
        return 'High-end'
    else:
        return 'Luxury'

def feature_engineering(df):
    df['price_category'] = df['price_avg'].apply(categorize_price)
    Q1 = df['price_avg'].quantile(0.25)
    Q3 = df['price_avg'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df['price_avg_capped'] = df['price_avg'].clip(lower=lower_bound, upper=upper_bound)


    # --- Advanced Feature Engineering with Real APIs ---
    # Ensure latitude and longitude columns exist
    if 'latitude' in df.columns and 'longitude' in df.columns:
        # Distance to CBD (Nairobi CBD coordinates)
        cbd_coords = (-1.286389, 36.817223)
        def get_distance_to_cbd(lat, lon):
            try:
                result = gmaps.distance_matrix(
                    origins=[(lat, lon)],
                    destinations=[cbd_coords],
                    mode="driving"
                )
                meters = result['rows'][0]['elements'][0]['distance']['value']
                return meters / 1000  # km
            except Exception:
                return np.nan
        df['distance_to_cbd'] = df.apply(lambda row: get_distance_to_cbd(row['latitude'], row['longitude']), axis=1)

        # Distance to nearest road using OpenStreetMap
        def get_distance_to_road(lat, lon):
            try:
                G = ox.graph_from_point((lat, lon), dist=1000, network_type='drive')
                nodes, edges = ox.graph_to_gdfs(G)
                property_point = Point(lon, lat)
                edges['distance'] = edges.geometry.distance(property_point)
                return edges['distance'].min()
            except Exception:
                return np.nan
        df['distance_to_road'] = df.apply(lambda row: get_distance_to_road(row['latitude'], row['longitude']), axis=1)

        # Proximity to bodies of water (OpenStreetMap water features)
        def get_distance_to_water(lat, lon):
            try:
                water = ox.geometries.geometries_from_point((lat, lon), tags={'natural': 'water'}, dist=2000)
                property_point = Point(lon, lat)
                if not water.empty:
                    water['distance'] = water.geometry.distance(property_point)
                    return water['distance'].min()
                else:
                    return np.nan
            except Exception:
                return np.nan
        df['distance_to_water'] = df.apply(lambda row: get_distance_to_water(row['latitude'], row['longitude']), axis=1)

        # Proximity to services (schools, hospitals, malls) using Google Maps Places API
        def get_distance_to_place(lat, lon, place_type):
            try:
                places = gmaps.places_nearby(location=(lat, lon), radius=5000, type=place_type)
                if places['results']:
                    place = places['results'][0]['geometry']['location']
                    result = gmaps.distance_matrix(
                        origins=[(lat, lon)],
                        destinations=[(place['lat'], place['lng'])],
                        mode="driving"
                    )
                    meters = result['rows'][0]['elements'][0]['distance']['value']
                    return meters / 1000
                else:
                    return np.nan
            except Exception:
                return np.nan
        df['distance_to_school'] = df.apply(lambda row: get_distance_to_place(row['latitude'], row['longitude'], 'school'), axis=1)
        df['distance_to_hospital'] = df.apply(lambda row: get_distance_to_place(row['latitude'], row['longitude'], 'hospital'), axis=1)
        df['distance_to_mall'] = df.apply(lambda row: get_distance_to_place(row['latitude'], row['longitude'], 'shopping_mall'), axis=1)

    # Flood risk (placeholder: binary flag, real integration would use GIS flood maps)
    df['flood_risk'] = np.random.choice([0, 1], size=len(df))

    # Sentiment score (using TextBlob on a 'news_headline' or 'description' column)
    if 'news_headline' in df.columns:
        df['sentiment_score'] = df['news_headline'].apply(lambda text: TextBlob(str(text)).sentiment.polarity)
    elif 'description' in df.columns:
        df['sentiment_score'] = df['description'].apply(lambda text: TextBlob(str(text)).sentiment.polarity)
    else:
        df['sentiment_score'] = np.random.uniform(-1, 1, size=len(df))

    # Crime rate (placeholder: random value, real integration would use public crime datasets)
    df['crime_rate'] = np.random.uniform(0, 100, size=len(df))

    # Zoning/land use (placeholder: random category, real integration would use government zoning data)
    df['zoning'] = np.random.choice(['Residential', 'Commercial', 'Agricultural'], size=len(df))

    # One-hot encode categorical features
    enc_neigh = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    neigh_encoded = enc_neigh.fit_transform(df[['neighborhood']]) if 'neighborhood' in df.columns else None
    enc_price_cat = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    price_cat_encoded = enc_price_cat.fit_transform(df[['price_category']])
    enc_zoning = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    zoning_encoded = enc_zoning.fit_transform(df[['zoning']])

    df_encoded = df.copy()
    if neigh_encoded is not None:
        neigh_df = pd.DataFrame(neigh_encoded, columns=enc_neigh.get_feature_names_out(['neighborhood']))
        df_encoded = pd.concat([df_encoded.reset_index(drop=True), neigh_df], axis=1)
        df_encoded.drop('neighborhood', axis=1, inplace=True)
    price_cat_df = pd.DataFrame(price_cat_encoded, columns=enc_price_cat.get_feature_names_out(['price_category']))
    df_encoded = pd.concat([df_encoded.reset_index(drop=True), price_cat_df], axis=1)
    zoning_df = pd.DataFrame(zoning_encoded, columns=enc_zoning.get_feature_names_out(['zoning']))
    df_encoded = pd.concat([df_encoded.reset_index(drop=True), zoning_df], axis=1)

    return df_encoded
