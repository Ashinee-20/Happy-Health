import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np
from easyocr import Reader
from matplotlib.widgets import RectangleSelector
import glob
import random
import base64
import pandas as pd
from PIL import Image
from io import BytesIO
from IPython.display import HTML
from geopy.distance import distance
import pyttsx3


IMAGE_PATH = r'2medpres2.jpeg'

reader = easyocr.Reader(['en'], gpu=False)
result = reader.readtext(IMAGE_PATH)
#print(result)

img = cv2.imread(IMAGE_PATH)
spacer = 100
for detection in result:
    top_left = tuple(detection[0][0])
    top_left_int = []
    for number in top_left:
        top_left_int += [int(number)]
    bottom_right = tuple(detection[0][2])
    bottom_right_int = []
    for number in bottom_right:
        bottom_right_int += [int(number)]
    top_left_int = tuple(top_left_int)
    bottom_right_int = tuple(bottom_right_int)
    text = detection[1]
    #print(text)
    list_text = []
    list_text.append(text)
    img = cv2.rectangle(img, top_left_int, bottom_right_int, (0, 255, 0), 3)
    #img = cv2.putText(img,text,(20,spacer), cv2.FONT_HERSHEY_SIMPLEX, 8,(0,255,0),2)
    spacer+=100

plt.figure(figsize=(10,10))
plt.imshow(img)
plt.show()


def onselect(eclick, erelease):
    print("\nScan the coordinates of the medicine....")
    global x1, y1, x2, y2
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)
    print("The Scanned coordinates of the medicine are:", end=" ")
    print(x1,y1,x2,y2)

# Open the image
n = int(input("Enter the number of medicines from the prescription: "))

medicines = []
for i in range(n):
    im = cv2.imread("2medpres2.jpeg")
    plt.imshow(im)
    # Create a RectangleSelector
    rs = RectangleSelector(plt.gca(), onselect, drawtype='box', useblit=True, button=[1], minspanx=5, minspany=5, spancoords='pixels', interactive=True)
    plt.connect('key_press_event', lambda e: [exit(0) if e.key == 'escape' else None])
    plt.show()

    cropped_im = im[y1:y2, x1:x2]
    reader = Reader(['en'])

    text = reader.readtext(cropped_im)
    print(text)
    medicines.append(text[0][1])

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

if(n>1):
    print("\nThe number of medicines mentioned in the prescription is more than one, Therefore ")
    engine.say("The number of medicines mentioned in the prescription is more than one, Therefore ")

for i in range(n):
    if(n==1):
        print("\nonly one medicine is mentioned in the prescription, and the medicine is " + medicines[i])
        engine.say("only one medicine is mentioned in the prescription, and the medicine is " + medicines[i])
        engine.runAndWait()
    else:
        print("medicine " + str(i + 1) + " is " + medicines[i])
        engine.say("medicine " + str(i+1) + " is " + medicines[i])
        engine.runAndWait()



pd.set_option('display.max_colwidth', None)
def get_thumbnail(path):
    i = Image.open(path)
    i.thumbnail((150, 150), Image.Resampling.LANCZOS)
    return i

def Image_base64(img):
    if isinstance(img, str):
        img = get_thumbnail(img)
    with BytesIO() as buffer:
        img.save(buffer, 'png')
        return base64.b64encode(buffer.getvalue()).decode()

def Image_formatter(img):
    return f'<img src="data:image/png;base64, {Image_base64(img)}">'


med = pd.read_csv('medicine_dataset.csv')
med['img_file'] = med.Names.map(lambda Names: f'{Names}.png')
med['Image'] = med.img_file.map(lambda f: get_thumbnail(f))

for med_input in medicines:
    #create a copy of the dataframe
    med_temp = med.copy()
    med_low = med_input.lower()
    med_lis = med_low.split(" ")
    for i in med_lis:
        med_temp['indexes'] = med_temp['Names'].str.find(i)
    # filter the dataframe only for rows where index is greater than -1
    med_temp = med_temp[med_temp['indexes'] > -1]
    #check if filtered dataframe is not empty
    if med_temp.empty:
        print(f'{med_input} not found')
        continue
    maxi = med_temp['indexes'].max()
    med_temp = med_temp.loc[med_temp['indexes'] == maxi]
    print("\nDetails of the medicine: ")
    print("medicine name: "+med_temp['Names'])
    print("Uses of the medicine: " + med_temp['Uses'])
    print("SideEffects of the medicine: " + med_temp['SideEffects'])
    #HTML(med_temp[['Names', 'Uses', 'SideEffects', 'img_file']].to_html(formatters={'img_file': Image_formatter}, escape=False))

    print("\nPrinting the picture of the medicine from the scanned coordinates.....")
    img = cv2.imread(med_temp['img_file'].iloc[0])
    plt.imshow(img)
    plt.title(med_input)
    plt.show()
    print("Done\n")




# Coordinates of the location you want to search near
location = (74.7943, 13.0108)   #coordinates of NITK
radius = 5
df = pd.read_csv("hospitals.csv")

distances = []
for i, hospital in df.iterrows():
    hospital_location = (hospital["latitude"], hospital["longitude"])
    dist = distance(location, hospital_location).km
    distances.append(dist)

df["distance"] = distances
nearby_hospitals = df[df["distance"] < radius]

print("\nDisplaying the list of hospitals within 5 kilometers radius\n")
for _, hospital in nearby_hospitals.iterrows():
    print(hospital["name"])
    print(hospital["address"])
    print(hospital["longitude"])
    print()