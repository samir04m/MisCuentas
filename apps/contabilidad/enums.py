from enum import Enum

class EstadoTransaccion(Enum):
    Programada = 0
    Realizada = 1
    RealizadaAgrupada = 2
    PadreGrupo = 3