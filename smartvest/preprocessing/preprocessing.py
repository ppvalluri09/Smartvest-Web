import quandl
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler, Normalizer

quandl.ApiConfig.api_key = "_4QxLqZJwu2fhcv1evF7"

def load_data(company_symbol, domain='WIKI'):
	PATH = './smartvest/data'
	filename = company_symbol + '.csv'
	if os.path.isfile(os.path.join(PATH, filename)):
		return pd.read_csv(os.path.join(PATH, filename))
	else:
		df = quandl.get(domain + '/' + company_symbol, collapse="daily") 
		df.to_csv(os.path.join(PATH, filename))
		return df

def clean_data(df, columns):
	df.drop(columns=columns, inplace=True)
	return df

def feature_scale(df):
	return pd.DataFrame(Normalizer().fit_transform(StandardScaler().fit_transform(df.values)), columns=df.columns)