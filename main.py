import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor

# Load the data
data = pd.read_csv('listings.csv', delimiter=';')

ALL_FEATURES=set(data.columns.values.tolist())
NUMERICAL_FEATURES={'Area', 'Rent', 'Build_year'} #[col for col in df.columns if data[col].dtype in ['int', 'float']]
CATEGORICAL_FEATURES={'District', 'Market'} #[col for col in data.columns if data[col].dtype == 'string']
#to_be_removed={'Price', 'Rent', 'Latitude', 'Longitude', 'Market', 'Build_year', 'Garage', 'Lift', 'Basement', 'Balcony', 'Garden', 'Terrace'}

# function which predicts the price of a flat using random forest regressor
def predict_price_random_forest(data, features):
    X = data[features] # features
    y = data['Price']  # target 
    features_set = set(features)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # preprocessing for numerical columns
    numerical_features = list(features_set.intersection(NUMERICAL_FEATURES))
    numerical_transformer = Pipeline(steps=[
        #('imputer', SimpleImputer(strategy='mean')),  # replace NaN values with the mean of the column
        ('scaler', StandardScaler())  # standardize 
    ])
    # preprocessing for categorical columns
    categorical_features = list(features_set.intersection(CATEGORICAL_FEATURES))
    categorical_transformer = Pipeline(steps=[
        #('imputer', SimpleImputer(strategy='most_frequent')),  # replace NaN values with the most frequent value of the column
        ('onehot', OneHotEncoder(handle_unknown='error'))  # one-hot encode categorical features 
    ])

    # combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # define the model
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(random_state=1, max_depth=10))
    ])

    # train the model
    model.fit(X_train, y_train)

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    print(f"Train R^2 score: {train_score:.2f}")
    print(f"Test R^2 score: {test_score:.2f}")

    y_pred = model.predict(X_test)
    results = X_test.copy()
    results['Actual'] = y_test
    results['Predicted'] = y_pred.astype(int)
    print(results.head(10))

predict_price_random_forest(data, ['Area', 'District'])
