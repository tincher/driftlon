import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

from datetime import datetime


# https://www.tensorflow.org/guide/keras/rnn#create_a_model_instance_and_compile_it
# https://www.tensorflow.org/guide/keras/rnn

(train_images, train_labels), _ = tf.keras.datasets.fashion_mnist.load_data()
train_images = train_images / 255.0




model = Sequential()
model.add(LSTM(128, input_shape=(28, 28), activation='relu', return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(128, activation='relu'))
model.add(Dropout(0.1))

model.add(Dense(32, activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(10, activation='softmax'))


model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              optimizer='sgd',
              metrics=['accuracy'])


logdir='tb_logs/fit/' + datetime.now().strftime('%Y%m%d-%H%M%S')
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)

# Train the model.
model.fit(
    train_images,
    train_labels,
    batch_size=1000,
    epochs=1,
    callbacks=[tensorboard_callback])

# model.fit(x_train, y_train,
#           validation_data=(x_test, y_test),
#           batch_size=batch_size,
#           epochs=5)

# model.summary()
