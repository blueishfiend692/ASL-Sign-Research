import serial
import pymongo
from dotenv import load_dotenv
import os

# connect to databse
load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGO_URI"))

db = client['cluster0']
collection = db[('EEDatabase')]
print("connected to database")

# setup serial port
averageRun = 2
ser = serial.Serial('COM5', 9600)

# define variables
state = False
stop_amount = 2
word = 'none' # word to be recorded
word_count = 0

# function to insert data into database
def insert_data(data):
  collection.insert_one(data)

# count for word (100 words to be recorded)
while word_count < 100:

  # run while hand sesnor is in off mode
  while state == False:

    line = ser.readline().decode('utf-8').strip()
    temp = line
    print("off", ' ', temp)
    arr = list(map(int,temp.split(' ')))
    sum = 0
    for i in arr:
      sum += i
    if sum < 5000:
      state = True

  # run while hand sensor is in on mode
  while  state == True:
    count = 0
    final_arr = []
    # while hand is not in off mode
    while count < stop_amount:

      # setup variables for reading
      sum = 0
      average_reading = [0,0,0,0,0]
      res_arr = [0,0,0,0,0]

      # read data from serial port
      for i in range(0,averageRun):
        line = ser.readline().decode('utf-8').strip()
        if line:
          current_line = line
          current_arr = list(map(int,current_line.split(' ')))
          for i in range(0,5):
            average_reading[i] += current_arr[i]

      # calculate average of readings to minimize noise
      for i in range(0,5):
        res_arr[i] = average_reading[i]/averageRun
        sum += res_arr[i]
      print("on", ' ', res_arr)

      # check if hand is in off mode
      if sum >= 5000:
        count += 1
        print(count)
      else:
        final_arr.append(res_arr) # append reading to final array

    # store, and insert data into database and update hand sensor state
    data = {"word": word, "hand": final_arr}
    insert_data(data)
    word_count += 1
    print(word_count)
    state = False

# close serial port
ser.close()

