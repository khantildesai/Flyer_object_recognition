import cv2
import pytesseract
import csv

units = []

with open("units_dictionary.csv") as f:
    fl = csv.reader(f)
    for row in fl:
        units.append(row)
    for u in range(len(units)):
        units[u] = units[u][0]

products = []

with open("product_dictionary.csv") as f:
    fl = csv.reader(f)
    for row in fl:
        products.append(row)
    for u in range(len(products)):
        products[u] = products[u][0]

class Item:
    def __init__(self, text, flyer_name, product_name = "", unit_promo_price = 0, uom = "", least_unit_for_promo = 1, save_per_unit = 0, discount = 0, organic = 0):
        self.flyer_name = flyer_name
        self.product_name = product_name
        self.unit_promo_price = unit_promo_price
        self.uom = uom
        self.least_unit_for_promo = least_unit_for_promo
        self.save_per_unit = save_per_unit
        self.discount = discount
        self.organic = organic
        self.text = text
    
    def parse(self):
        for info in self.text:
            for u in units:
                if u in info:
                    self.uom = u
                    break
            if len(info) > 3:
                if "$" == info[0]:
                    a = info[-1]
                    b = info[-2]
                    t = f".{a}{b}"
                    info = info[:-2]
                    info = info + t
                    if info[-5] == "$":
                        self.unit_promo_price = info[-5:]
                    else:
                        self.unit_promo_price = info[-6:]
                    self.least_unit_for_promo = 1
                elif ("/" or "|") == info[1]:
                    a = info[-1]
                    b = info[-2]
                    t = f".{a}{b}"
                    info = info[:-2]
                    info = info + t
                    try: 
                        up = str(float(info[-4] + info[3] + info[-2] + info[-1])/float(info[0]))
                    except: 
                        up = "$5.00"
                    self.unit_promo_price = up
                    self.least_unit_for_promo = int(info[0])
                elif ("/" or "|") == info[2]:
                    a = info[-1]
                    b = info[-2]
                    t = f".{a}{b}"
                    info = info[:-2]
                    info = info + t
                    try:
                        up = str(int(info[-4] + info[3] + info[-2] + info[-1])/int(info[0] + info[1]))
                    except:
                        up = "$5.00"
                    self.unit_promo_price = up
                    self.least_unit_for_promo = int(info[0])

            
            if "organic" in info:
                self.organic = 1
            
            if info in products:
                self.product_name = info.strip()
            
            if "save" in info.lower():
                disc = ""
                for letter in range(len(info)):
                    if info[letter] == "$":
                        for l in range(letter + 1, len(info)):
                            if info[l] in ["0","1","2","3","4","5","6","7","8","9","10","."]:
                                disc = disc + info[l]
                            else:
                                break
                self.save_per_unit = disc
                if str(self.unit_promo_price)[0] == "$":
                    try: 
                        self.discount = round(float(disc) / (float(disc) + float(self.unit_promo_price[1:])), 2)
                    except:
                        self.discount = 0
                else:
                    try:
                        self.discount = round(float(disc) / (float(disc) + float(self.unit_promo_price)), 2)
                    except:
                        self.discount = 0

            elif "off" in info.lower():
                for letter in range(len(info)):
                    disc = ""
                    if info[letter] == "$":
                        for l in range(letter + 1, len(info)):
                            if l in ["0","1","2","3","4","5","6","7","8","9","10","."]:
                                disc = disc + l
                            else:
                                break
                
                self.save_per_unit = disc
                try:
                    self.discount = round((int(self.unit_promo_price) - int(disc)) / (int(disc) + int(self.unit_promo_price)), 2)
                except:
                    self.discount = 0

    def prt(self, file_name):
        with open(file_name, mode='a') as csv_file:
            cwriter = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if not (self.unit_promo_price == 0):
                cwriter.writerow([self.flyer_name, self.product_name, self.unit_promo_price, self.uom, self.least_unit_for_promo, self.save_per_unit, self.discount, self.organic])

#reads text
def read(img):
    text = pytesseract.image_to_string(img)
    #remove new line and empty strings
    text = text.split("\n")
    while "" in text:
        text.remove("")
    return text