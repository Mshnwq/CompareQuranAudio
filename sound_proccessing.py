import speech_recognition as sr
import pyquran as pq
import arabic_reshaper
import pyarabic
from bidi.algorithm import get_display
import re
import jellyfish as jf
import pyrebase

# path = "test/test123.wav"
# sura = eval(input("enter sura to compare: "))
# beggin = eval(input("enter beggining ayah: "))
# finish = eval(input("enter finishing ayah: "))

def process(path, sura, beggin, finish):
    
    text = SpeechToText(path, sura)
    
    #print(Compare(text, sura, beggin, finish)) # (text, sura number, ayah beggin, ahay end)
    return Compare(text, sura, beggin, finish) # (text, sura number, ayah beggin, ahay end)

def SpeechToText(path, sura):

    r = sr.Recognizer()

    firebaseConfig = {
    "apiKey" : "AIzaSyDGSj1KuwmNYPCqvnUxp9xfBQFIudDUrOM",
    "authDomain" : "halaqh-8f1f9.firebaseapp.com",
    "projectId" : "halaqh-8f1f9",
    "databaseURL" : "",
    "storageBucket" : "halaqh-8f1f9.appspot.com",
    "messagingSenderId" : "116228115176",
    "appId" : "1:116228115176:web:93c3ae18ddf257b73c975d",
    "measurementId" : "G-WVZ5MBBWL3"
        }

    firebase = pyrebase.initialize_app(firebaseConfig)

    storage = firebase.storage()

    try:
        storage.child(path).download("test.wav")

        with sr.AudioFile("test.wav") as source:
            
            audio = r.record(source)

            text = r.recognize_google(audio, language = 'ar-SA')

        #printArabic(text) ####
        text2 = transform(text)
        text3 = checkBasmalah(sura, text2)
        return getArabic(text3)
        
    except Exception as e:                  # speech is unintelligible
            return("0".format(e)) # 0 فشل التعرف

def getURL(path):
    
    firebaseConfig = {
    "apiKey" : "AIzaSyDGSj1KuwmNYPCqvnUxp9xfBQFIudDUrOM",
    "authDomain" : "halaqh-8f1f9.firebaseapp.com",
    "projectId" : "halaqh-8f1f9",
    "databaseURL" : "",
    "storageBucket" : "halaqh-8f1f9.appspot.com",
    "messagingSenderId" : "116228115176",
    "appId" : "1:116228115176:web:93c3ae18ddf257b73c975d",
    "measurementId" : "G-WVZ5MBBWL3"
        }

    firebase = pyrebase.initialize_app(firebaseConfig)

    storage = firebase.storage()

    url = storage.child(path).get_url(token = None)

    return str(url)


def printArabic(text):
    
    text2 = transform(text)
    reshaped_text = arabic_reshaper.reshape(text2)   # corrects the Arabic text shape
    bidi_text = get_display(reshaped_text)           # corrects the direction
    print(bidi_text)

def getArabic(text):
    
    reshaped_text = arabic_reshaper.reshape(text)   # corrects the Arabic text shape
    bidi_text = get_display(reshaped_text)          # corrects the direction
    return bidi_text

def listToString(s):  # converts from list to string
    str1 = " " 
    
    return str1.join(s)

def transform(text): # replaces all "ة" into "ه"
    
    ta = u'\u0629' #"ة"
    ha = u'\u0647' #"ه"
    alif_maq = u'\u0649' #"ى"
    ya = u'\u064A' #"ي"

    text = re.sub("[إأآا]", "ا", text)
    text = re.sub(ta, ha, text)
    text = re.sub(alif_maq, ya, text)

    return text

def checkBasmalah(sura, text0):
    
    text = text0.split() # from string into list
    
    if (text[0] == "اعوذ"):
        text2 = removeAooth(text)
        return checkBasmalah(sura ,listToString(text))

    elif (text[0] == "بسم"):
        if (sura == 1):
            return listToString(text)

        else:
            text2 = removeBasmalah(text)
            return listToString(text2)

    else:
        return listToString(text)

def removeAooth(text):

    del text[0:5]
    return text

def removeBasmalah(text):

    del text[0:4]
    return text

def getAyat(sura, start, end):
    
    if (end == 0):
        ayat = sura[(start - 1):]
        return ayat

    else:
        ayat = sura[(start - 1): (end)]
        return ayat

def getSura(suraNumber):

    Q = pq.quran # Quran Object
    return Q.get_sura(suraNumber, with_tashkeel=False, basmalah=False) # returns list

def getLevenshteinRatio(text, text2):

    return round(((len(text2) - jf.levenshtein_distance(text, text2)) / len(text2)) , 2) * 100 

def Compare(text, suraNumber, ayah_start = 1, ayah_end = 0):
    
    if (text == "0"):
        return text

    # print(text)##
    # print("-------")###
    text2 = getArabic(transform(listToString(getAyat(getSura(suraNumber), ayah_start , ayah_end))))
    # print(text2)
    
    try:

        percent = getLevenshteinRatio(text, text2)
        #print(percent)
        return getReport(percent)

    except Exception as e:              
        
        return ("1".format(e)) # 1 حدث خطأ

def getReport(percent):
          
    if(90 <= percent and percent <= 100):
        return "ممتاز +"

    elif(85 <= percent and percent < 90):
        return "ممتاز"

    elif(80 <= percent and percent < 85):
        return "جيد جداً +"

    elif(75 <= percent and percent < 80):
        return "جيد جداً"

    elif(70 <= percent and percent < 75):
        return "جيد +"

    elif(65 <= percent and percent < 70):
        return "جيد"

    elif(60 <= percent and percent < 65):
        return "مقبول +"

    elif(55 <= percent and percent < 60):
        return "مقبول"

    else:
        return "ضعيف"

# process(path, sura, beggin, finish)