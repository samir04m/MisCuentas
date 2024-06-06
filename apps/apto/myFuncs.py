from datetime import datetime, timedelta
from .models import *

def GetAptoFromRequest(request) -> Apartamento:
    pagador = Pagador.objects.filter(user=request.user).first()
    if not pagador:
        raise Exception('No es posible obtener el Apartamento desde el request')
    return pagador.apto

def CalcularNumeroDias(fechaInicioStr:str, fechaFinStr:str) -> int:
    fechaInicio = datetime.strptime(fechaInicioStr, "%Y/%m/%d")
    fechaFin = datetime.strptime(fechaFinStr, "%Y/%m/%d")
    diferencia = fechaFin - fechaInicio + timedelta(days=1)
    return abs(diferencia.days)