import serial
import pymongo
from dotenv import load_dotenv
import os


# function to insert data into database
def insert_data(data):
  collection.insert_one(data)

# connect to databse
load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGO_URI"))

db = client['signspeak']
collection = db[('data_collection')]
print("connected to database")

# setup serial port
averageRun = 1
ser = serial.Serial('COM5', 9600)

# define variables
state = False
stop_amount = 74 #0.1 seconds pause @740Hz
word = 'none' # word to be recorded
word_count = 0 #current word amount
word_stop_amount = 50 # words to be stopped at
state_false_count = 0

# count for word
while word_count < word_stop_amount:

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
      state_false_count+= 1
    if state_false_count > stop_amount:
      state_false_count = 0
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
    # insert_data(data)
    print(data) 
    word_count += 1
    print(word_count)
    state = False

# close serial port
ser.close()
