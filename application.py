from flask import Flask, request, jsonify
import os
import mysql.connector
from mysql.connector import Error

# EB looks for an 'application' callable by default.
application = Flask(__name__)

@application.route('/creartablas')
def creartablas():
    dbname = os.environ['RDS_DB_NAME']
    dbuser = os.environ['RDS_USERNAME']
    dbpwd = os.environ['RDS_PASSWORD']
    dbport = os.environ['RDS_PORT']
    dbhost = os.environ['RDS_HOSTNAME']
    try:
        connection = mysql.connector.connect(host=dbhost, database=dbname, user=dbuser, password=dbpwd)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS Cuentas (id INT AUTO_INCREMENT PRIMARY KEY, Usuario VARCHAR(255), Saldo INT)")
            connection.commit()
            return "Tabla creada"

    except Error as e:
        return "Error al crear tabla: " + str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@application.route('/crearusuario/<usuario>')
def crearusuario(usuario):
    dbname = os.environ['RDS_DB_NAME']
    dbuser = os.environ['RDS_USERNAME']
    dbpwd = os.environ['RDS_PASSWORD']
    dbport = os.environ['RDS_PORT']
    dbhost = os.environ['RDS_HOSTNAME']
    try:
        connection = mysql.connector.connect(host=dbhost, database=dbname, user=dbuser, password=dbpwd)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Cuentas (Usuario, Saldo) VALUES (%s, %s)", (usuario,100))
                           
            connection.commit()
            return "Usuario insertado"

    except Error as e:
        return "Error insertando usuario: " + str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@application.route('/transferir/<usuario>')
def transferir(usuario):
    destinatario = request.args.get("destino")
    monto = int(request.args.get("valor"))

    dbname = os.environ['RDS_DB_NAME']
    dbuser = os.environ['RDS_USERNAME']
    dbpwd = os.environ['RDS_PASSWORD']
    dbport = os.environ['RDS_PORT']
    dbhost = os.environ['RDS_HOSTNAME']
    try:
        connection = mysql.connector.connect(host=dbhost, database=dbname, user=dbuser, password=dbpwd)
        if connection.is_connected():
            cursor = connection.cursor()
               
            consulta_saldo_emisor = "SELECT Saldo FROM Cuentas WHERE Usuario = %s"
            cursor.execute(consulta_saldo_emisor, (usuario,))
            saldo_emisor = cursor.fetchone()

            if saldo_emisor is None:
                return "El emisor no existe en la base de datos"
            saldo_emisor = int(saldo_emisor[0])

            if saldo_emisor < monto:
                return "Saldo insuficiente para realizar la transferencia"
            
            consulta_saldo_destinatario = "SELECT Saldo FROM Cuentas WHERE Usuario = %s"
            cursor.execute(consulta_saldo_destinatario, (destinatario,))
            saldo_destinatario = cursor.fetchone()

            if saldo_destinatario is None:
                return "El destinatario no existe en la base de datos"
            saldo_destinatario = int(saldo_destinatario[0]) 

            actualizar_saldo_emisor = "UPDATE Cuentas SET Saldo = %s WHERE Usuario = %s"
            cursor.execute(actualizar_saldo_emisor, (saldo_emisor - monto, usuario))
            
            actualizar_saldo_destinatario = "UPDATE Cuentas SET Saldo = %s WHERE Usuario = %s"
            cursor.execute(actualizar_saldo_destinatario, (saldo_destinatario + monto, destinatario)) 

            connection.commit()
            return f"Transferencia exitosa: {monto} unidades de {usuario} a {destinatario}. Nuevo saldo de {usuario}: {saldo_emisor - monto} | Nuevo saldo de {destinatario}: {saldo_destinatario + monto}"


    except Error as e:
        return "Error en la transferencia: " + str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@application.route('/leertabla', methods=['GET'])
def obtener_todos_los_registros():
    dbname = os.environ['RDS_DB_NAME']
    dbuser = os.environ['RDS_USERNAME']
    dbpwd = os.environ['RDS_PASSWORD']
    dbport = os.environ['RDS_PORT']
    dbhost = os.environ['RDS_HOSTNAME']
    try:
        connection = mysql.connector.connect(host=dbhost, database=dbname, user=dbuser, password=dbpwd)
        if connection.is_connected():
            cursor = connection.cursor()
            consulta = "SELECT * FROM Cuentas"

            cursor.execute(consulta)
            registros = cursor.fetchall()

            resultados = []
            for registro in registros:
                registro_dict = {
                    'id': registro[0],
                    'Usuario': registro[1],
                    'Saldo': registro[2]
                }
                resultados.append(registro_dict)

            return jsonify(resultados)
    except Exception as e:
        return str(e)

# Asegúrate de tener una conexión a la base de datos establecida antes de ejecutar esta función


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
