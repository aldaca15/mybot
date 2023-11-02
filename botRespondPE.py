from botConfig import confidenceLevel
from difflib import SequenceMatcher
import re
import urllib.parse
import csv
import random
import os
import requests
#pip install requests to add it
import csv
import datetime

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def writeToCSV(nuevo_registro):
    # 1. Leer el contenido existente del archivo CSV en una lista
    registros_existentes = []
    nombre_archivo = os.path.abspath('mybot/data/phonebook.csv')
    try:
        with open(nombre_archivo, 'r', newline='') as archivo_csv:
            lector = csv.reader(archivo_csv)
            for fila in lector:
                registros_existentes.append(fila)
    except FileNotFoundError:
        # Si el archivo no existe, se crea uno nuevo con el encabezado
        registros_existentes.append(["Tel/cel", "Comentario", "Date"])
    # 2. Agregar el nuevo registro a la lista
    now = datetime.datetime.now()
    nuevo_registro.insert(0, str(now)) # add date at the beginning
    registros_existentes.append(nuevo_registro)
    # 3. Escribir la lista actualizada de registros en el archivo CSV
    with open(nombre_archivo, 'w', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        for fila in registros_existentes:
            escritor.writerow(fila)

def checkPhoneNum(texto):
    texto = texto.replace(',', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    # Define una exp regular para buscar series de digitos con comas, espacios y parentesis
    patron = r'\d{9,}|\d{1,3}(?:[, -]?\d{3}){2,}\d{1,3}'
    # Busca todas las coincidencias en el texto
    coincidencias = re.findall(patron, texto)
    # Filtra las coincidencias para asegurarse de que tengan al menos 9 dig
    numeros_validos = []

    for c in coincidencias:
        # Elimina comas, guiones, espacios y parentesis
        #print(c)
        numeros_validos.append(c)

    #return numeros_validos
    return numeros_validos

def getResponse(sendMsg):
    #return "You said: " + sendMsg
    sendMsg = urllib.parse.unquote(sendMsg)
    #Loop through CSV knowledge file.  If a question is equal to or greater than the confidence level, add it to a list of possible responses. Then return a random responses
    lineCount = 0
    successCount = 0
    exactCount = 0
    comeBacks = []
    exactReply = []
    exactMatch = .9

    botBrain = os.path.abspath('mybot/data/chatbot.csv')

    with open(botBrain) as g:
        lines = csv.reader(g)
        for line in lines:
            lineCount += 1
            if not line[0] or not line[1]:
                emptyCount += 1
                print("WARNING: I had to skip row #" + str(lineCount) + " due to missing data.")
            if lineCount > 1 and line[0] and line[1]:
                userText = line[0]
                botReply = line[1]
                separatorP = "|"
                contadorAltQ = userText.count(separatorP)
                if contadorAltQ == 0:
                    checkMatch = similar(sendMsg, userText)
                    if checkMatch >= exactMatch:
                        exactCount += 1
                        exactReply.append(botReply)
                        print("Likely match: " + userText)
                        print("Match is: " + str(checkMatch))
                    elif checkMatch >= confidenceLevel:
                        successCount += 1
                        comeBacks.append(botReply)
                        print("Possible match: " + userText)
                        print("Match is: " + str(checkMatch))
                # AdditionalFlow20231022 now able to detect multiple entries for one response on data csv. ex:
                # fuck you|go to hell|you suck, you too!
                else:
                    subcadenasQ = userText.split(separatorP)
                    for subQuestion in subcadenasQ:
                        checkMatch = similar(sendMsg, subQuestion)
                        if checkMatch >= exactMatch:
                            exactCount += 1
                            exactReply.append(botReply)
                            print("Likely match: " + subQuestion)
                            print("Match is: " + str(checkMatch))
                        elif checkMatch >= confidenceLevel:
                            successCount += 1
                            comeBacks.append(botReply)
                            print("Possible match: " + subQuestion)
                            print("Match is: " + str(checkMatch))
                ### end of AdditionalFlow20231022
    if exactCount >= 1:
        botResponsePick = random.choice(exactReply)
    elif successCount >= 1:
        botResponsePick = random.choice(comeBacks)
    elif len(checkPhoneNum(sendMsg)) > 0:
        numbers = checkPhoneNum(sendMsg)
        phoneNum = numbers[0]
        #url = 'https://radionautas.com/chatbotdemo/contact.php' #saves csv
        #url = "https://radionautas-com.translate.goog/chatbotdemo/contact.php?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=en-US&_x_tr_pto=wapp"
        #url = "https://feeling.com.mx/andarez/secompra/api/public/email/interested" #send email
        url = "https://feeling-com-mx.translate.goog/andarez/secompra/api/public/email/interested?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=en-US&_x_tr_pto=wapp"
        params = {'tel': phoneNum, "data": sendMsg}
        response = requests.get(url, params=params)
        botResponsePick = "IKrespNumber"
        '''if response.status_code == 200:
            print('La llamada GET se realizó con éxito.')
            botResponsePick = "IKrespNumber"
        else:
            print('Hubo un problema al realizar la llamada GET. Código de estado:', response.status_code)
            botResponsePick = "IKrespNoNumber"'''
        # BACKUP ON CSV - JIC
        nuevo_registro = [phoneNum, sendMsg]
        writeToCSV(nuevo_registro)
    else:
        botResponsePick = "IDKresponse"
    return botResponsePick
