#Este archivo contiene las configuraciones particulares de cada instancia.

#1. Base de datos.
#2. Tiempo para logout
#3. Path estatico para cargar recursos como imagenes, css, etc.

# Configuracion del acceso a la base de datos
CONFIGURACION_BASE_DE_DATOS = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Libreria de python para conectarse a la bd. Debe estar instalada en el sistema.
        'NAME': 'empresa_xxxx',  # NOMBRE de la BD.
        'USER': 'empresa_xxxx_db_owner',  # USUARIO de la BD
        'PASSWORD': 'xxxxxxx',  # # Contraseña de la BD
        'HOST': '<ip del host de la BD>',  # ip del HOST
        'PORT': '<puerto de la BD>',  # Usualmente 5432
    }
}

# Tiempo logout
TIEMPO_LOGOUT = 15

# Direccion de archivos estaticos
PATH_ESTATICO = '/Users/xxxxxxxxxxxx/xxxxxx/xxxxxx/principal/static'

# Codigo de empresa
CODIGO_DE_EMPRESA = 'EMP'
