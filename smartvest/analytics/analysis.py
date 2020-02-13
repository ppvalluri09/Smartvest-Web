import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.neural_network import MLPRegressor
	
colors = ['r', 'b', 'g', 'y', 'c', 'm'] * 3

def plot_each_timeseries(df):
	fig = plt.figure()
	for i in range(df.shape[1]):
		plt.subplot(3, 4, i+1)
		plt.plot(df.iloc[:, i], c=colors[i])
		plt.xlabel(df.columns[i])
		plt.ylabel('Price')
	fig.tight_layout()
	plt.show()

def corr_plot(df):
	fig = plt.figure()
	for i in range(df.shape[1]):
		plt.subplot(3, 4, i + 1)
		sns.distplot(df.iloc[:, i], color=colors[i])
	fig.tight_layout()
	plt.show()

	corr = df.corr().round(2)
	sns.heatmap(corr, annot=True)
	plt.show()

def build_model(shape, model_type='regressor'):
	model = keras.Sequential()
	model.add(layers.Dense(30 * shape[1], input_shape=[shape[0] * shape[1]]))
	model.add(layers.Activation('relu'))
	model.add(layers.Dense(64))
	model.add(layers.Activation('relu'))
	if model_type=='clasifier':
		model.add(layers.Dense(64))
		model.add(layers.Activation('sigmoid'))
		model.add(layers.Dense(1))
	else:
		model.add(layers.Dense(64))
		model.add(layers.Activation('relu'))
		model.add(layers.Dense(30))

	optimizer = tf.keras.optimizers.RMSprop(0.001)
	model.compile(loss='mse', optimizer=optimizer, metrics=['mae', 'mse'])
	return model

def train_nn(x_t, y_t):
	model = build_model(model_type='regressor', shape=x_t.shape)
	print('Model Summary', model.summary())

	early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
	x_t = np.array(x_t).reshape((x_t.shape[0] * x_t.shape[1], 1))
	print(x_t.shape)
	history = model.fit(x_t, y_t, epochs=10, validation_split = 0.2, callbacks=[early_stop])
	# print(history)
	# return model

def train_MLP(x_t, y_t):
	model = MLPRegressor(hidden_layer_sizes=(64, 64, 30), activation='relu', solver = 'sgd', learning_rate = 'adaptive')
	y_t = y_t.reshape((y_t.shape[0], ))
	model.fit(x_t, y_t)
	return model