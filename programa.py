import os
import smtplib
import ssl
from email.message import EmailMessage
import arrow
import requests


def media_horas(json_data, parametro, h1, h2):
  if h2 == None:
    return (json_data['hours'][(h1 - 3)][parametro]['icon'] + json_data['hours'][(h1 - 3)][parametro]['noaa'] + json_data['hours'][(h1 - 3)][parametro]['sg']) / 3
  
  quant_horas = (h2 - h1) + 1

  count = 0
  media = 0
  while(count < quant_horas):
    media += (json_data['hours'][(h1 - 3) + count][parametro]['icon'] + json_data['hours'][(h1 - 3) + count][parametro]['noaa'] + json_data['hours'][(h1 - 3) + count][parametro]['sg']) / 3
    count += 1
  
  media = media / quant_horas
  return media 

def media_horas_temp(json_data, parametro, h1, h2):
  if h2 == None:
    return (json_data['hours'][(h1 - 3)][parametro]['meto'] + json_data['hours'][(h1 - 3)][parametro]['noaa'] + json_data['hours'][(h1 - 3)][parametro]['sg']) / 3
  
  quant_horas = (h2 - h1) + 1

  count = 0
  media = 0
  while(count < quant_horas):
    media += (json_data['hours'][(h1 - 3) + count][parametro]['meto'] + json_data['hours'][(h1 - 3) + count][parametro]['noaa'] + json_data['hours'][(h1 - 3) + count][parametro]['sg']) / 3
    count += 1
  
  media = media / quant_horas
  return media 

def direcao_graus(media):
  if media <= 11.25:
    return "N"
  if media <= 33.75:
    return "NNE"
  elif media <= 56.25:
    return "NE"
  elif media <= 78.75:
    return "ENE"
  elif media <= 101.25:
    return "E"
  elif media <= 123.75:
    return "ESE"
  elif media <= 146.25:
    return "SE"
  elif media <= 168.75:
    return "SSE"
  elif media <= 191.25:
    return "S"
  elif media <= 213.75:
    return "SSW"
  elif media <= 236.25:
    return "SW"
  elif media <= 258.75:
    return "WSW"
  elif media <= 281.25:
    return "W"
  elif media <= 303.75:
    return "WNW"
  elif media <= 326.25:
    return "NW"
  elif media <= 348.25:
    return "NNW"
  elif media <= 360:
    return "N"
    
def print_direcao_swell(json_data):
  media_direcao = media_horas(json_data, "swellDirection", 3, 23)
  direcao = direcao_graus(media_direcao)
  return f"Direção do swell: {direcao}"

def print_waveHeight(json_data):
  string_final = ""
  count = 1
  hora = 3
  while(count <= 7):
    prox_hora = hora + 3 
    media_altura = media_horas(json_data, "waveHeight", hora, prox_hora)
    media_altura -= 0.3
    string_final += f"{hora}:00 - {prox_hora}:00:\n"
    string_final += f"\tAltura do surf: {media_altura: .1f}m\n"

    media_vento = media_horas(json_data, "windDirection", hora, prox_hora)
    media_vento = direcao_graus(media_vento)
    string_final += f"\tDireção do vento: {media_vento}\n"
    hora += 3
    count += 1
    
  return string_final




hj = arrow.now()
amanha = hj.shift(days=1)

# Get first hour of today
start = amanha.floor('day')

# Get last hour of today
end = amanha.ceil('day')

response = requests.get(
  'https://api.stormglass.io/v2/weather/point',
  params={
    'lat': -22.990391, 
    'lng': -43.193531,
    'params': ','.join(['waveHeight', 'swellDirection','windDirection','waterTemperature']),
    'start': start.to('UTC').timestamp(),
    'end': end.to('UTC').timestamp(),
  },
  headers={
    'Authorization': API_KEY
  }
)


#Create the email message
json_data = response.json()


temp = media_horas_temp(json_data, 'waterTemperature',3, 23)

string_final = f"""
Previsão do dia: {amanha.strftime('%d/%m/%Y')}
Temperatura da água: {temp: .0f}ºC
{print_direcao_swell(json_data)}

{print_waveHeight(json_data)}
"""


#sends email
email_sender = "previsaodeamanha@gmail.com"
email_password = EMAIL_PASSWORD
email_receiver = EMAIL_LIST



subject = "Previsão para o surf de amanha"
body = string_final

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())

print("EMAIL SENT")





