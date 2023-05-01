from datetime import datetime

def getDate(inputDate):
    now = datetime.now()
    if inputDate:
        grupos = inputDate.split(" ")
        fecha = grupos[0].split("/")
        hora = grupos[1].split(":")
        hour = getHour24(hora[0], grupos[2])
        date = datetime(int(fecha[2]), int(fecha[1]), int(fecha[0]), hour, int(hora[1]), now.second)
        return date
    else:
        return now

def getHour24(hour, xm):
    if xm == "AM" and hour == "12":
        return 0
    elif xm == "AM":
        return int(hour)
    elif xm == "PM" and hour == "12":
        return int(hour)
    else:
        return int(hour) + 12

def validarMiles(cantidad) -> int:
    if len(str(cantidad)) < 4:
        return cantidad * 1000
    else:
        return cantidad