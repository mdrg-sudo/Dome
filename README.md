## Comandos para instalar Dependencias:
### -> Crear entorno virtual
    python -m venv venv  
### -> Instalar django
    pip install django                                                      
### -> Instalar mysql
    pip install pymysql   
### -> libreria de criptografia
    pip install cryptography                                                
### -> activar el entorno virtual
    venv\Scripts\activate     
### ->  (cuando hacemos cambios en views para reflejarlos en la bd).
    python manage.py migrate  
### --> Solo si el coamdno anterior se ejecuta
    python manage.py makemigrations  
### -> Correr el proyecto
    python manage.py runserver        

