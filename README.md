# Documentación Django 2 Windows
Se requiere de Python en su versión 3.6.8. En este caso uso 3.9.9.

### Entorno Virtual
Creación
```
python -m venv venvMisCuentas
```
Activación del entorno virtual: ```venvMisCuentas\Scripts\activate```

Una vez activado el entorno virtual verificar que la versión de python predeterminada sea la 3.9.9: ```python --version```

### Instalación de pip
Primero instalar y/o actualizar el gestor de paquetes:
```
python -m pip install --upgrade pip
```
### Instalación de Django
Crear en la raiz del projecto un archivo ```requirements.txt```
El cual contenga lo siguente ```Django~=2.2.4```
Ahora en cmd ejecutar:
```
python -m pip install -r requirements.txt
```
Sino instalar manualmente cada paquete:
```
pip install Django~=2.2.4
```
```
pip install django-import-export
``
