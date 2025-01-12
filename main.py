from telegram.ext import *
from io import BytesIO
import cv2
import numpy as np
import tensorflow as tf
from asyncio import Queue

with open("token.txt") as file:
    token = file.read()

async def start(update,context):
    await update.message.reply_text("Hello! I am a bot that can detect the object in the image. Send me an image and I will tell you the object in the image.")
    
async def help(update,context):
    await update.message.reply_text("Send me an image and I will tell you the object in the image. \n/start - To start the bot \n/help - To get help \n/train - To train the model \n")

async def train(update,context):
    await update.message.reply_text("Training the model...")
    model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])
    model.fit(x_train,y_train,epochs=10,validation_data=(x_test,y_test))
    await update.message.reply_text("Model trained successfully! Please send a photo!")
    model.save("cifar_classifier_model.keras")
    print("model saved!")

    
async def handle_message(update,context):
    update.message.reply_text("Please send an image to detect the object in the image.")
    
async def handle_photo(update,context):
    file = context.bot.get_file(update.message.photo[-1].file_id)
    f = BytesIO(file.download_as_bytearray())
    file_bytes = np.asarray(bytearray(f.read()),dtype=np.uint8)
    img = cv2.imdecode(file_bytes,cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img = cv2.resize(img,(32,32),interpolation=cv2.INTER_AREA)
    
    prediction = model.predict(np.array([img/255]))
    update.message.reply_text(f"Object in the image is {class_names[np.argmax(prediction)]}")

(x_train,y_train),(x_test,y_test) = tf.keras.datasets.cifar10.load_data()
x_train, x_test = x_train/255.0, x_test/255.0

class_names = ["Plane","Car","Bird","Cat","Deer","Dog","Frog","Horse","Ship","Truck"]

my_queue = Queue()

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Conv2D(32,(3,3),activation='relu',input_shape=(32,32,3)))
model.add(tf.keras.layers.MaxPooling2D((2,2)))
model.add(tf.keras.layers.Conv2D(64,(3,3),activation='relu'))
model.add(tf.keras.layers.MaxPooling2D((2,2)))
model.add(tf.keras.layers.Conv2D(64,(3,3),activation='relu'))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(64,activation='relu')) 
model.add(tf.keras.layers.Dense(10,activation="softmax"))

app = Application.builder().token(token).build()
print("Bot started")
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("help",help))
app.add_handler(CommandHandler("train",train))
app.add_handler(MessageHandler(filters.TEXT,handle_message))
app.add_handler(MessageHandler(filters.PHOTO ,handle_photo))

app.run_polling()
print("Polling")
app.idle()