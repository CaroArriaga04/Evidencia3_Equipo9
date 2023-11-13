import datetime
import pandas as pd
import re
from tabulate import tabulate
import pandas as pd
import os
import sys
import sqlite3
from sqlite3 import Error
 
class Nota:
    def __init__(self, folio, fecha, claveCliente, monto, cancelada):
        self.folio = folio
        self.fecha = fecha
        self.claveCliente = claveCliente
        self.monto = monto
        self.cancelada = cancelada

def validar_continuidad(mensaje):
    while True:
        confirmar = input("\n" + mensaje + " (Solamente Sí/No)?: ")
        if confirmar == "":
            print("\nRespuesta omitida, ingrese nuevamente.")
            continue
        elif confirmar.upper() in ("N", "NO"):
            break
        elif confirmar.upper() in ("S", "SI"):
            print("\nDe acuerdo.")
            return True
        else:
            print("\nLa respuesta ingresada debe ser 'Si' o 'No'.")

def registrar_nota():    
    try:
        hoy = datetime.date.today()
        while True:
            fecha = input("\nIngresa la fecha (dd/mm/yyyy): ")
            try:
                fecha = datetime.datetime.strptime(fecha, "%d/%m/%Y").date()
                if fecha <= hoy:
                    break
                else:
                    print("\n* La fecha no puede ser posterior a la actual, ingrese nuevamente *")
            except Exception:
                print("\n* Fecha no ingresada o invalida, ingrese nuevamente *")
                continue

        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute("SELECT claveCliente, nombreCliente FROM Cliente where canceladaCliente = 0")
            clientes= mi_cursor.fetchall()
            if not clientes:
                print("\n* No hay clientes registrados, operación registrar nota cancelada *")
                return
            print("\n   Clientes registrados  ")
            informacion = [[clave, nombreCliente] for clave, nombreCliente in clientes]
            titulos = ["Clave", "Nombre"]
            print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            while True:
                clave_c = input("\nIngrese la clave del cliente: ")
                if clave_c == "":
                    print("La clave no se puede quedar vacía, vuelva a intentar")
                    continue
                if not (bool(re.search('^[0-9]+$', clave_c))):
                    print ("\n* Clave no valida, ingrese nuevmente *")
                    continue
                valores={"claveCliente":clave_c}
                mi_cursor.execute("SELECT * FROM Cliente WHERE claveCliente = :claveCliente \
                                  AND canceladaCliente = 0", (valores))
                cliente = mi_cursor.fetchone()
                if cliente:
                    mi_cursor.execute('SELECT claveServicio, nombre, costo FROM Servicio WHERE canceladaServicio = 0')
                    servicios = mi_cursor.fetchall()
                    if not servicios:
                        print("\n* No hay servicios disponibles, operación registrar nota cancelada *")
                        return
                    print("\n       Servicios disponibles")
                    informacion = [[claveServicio, nombre, costo] for claveServicio, nombre, costo in servicios]
                    titulos = ["Clave", "Nombre", "Costo"]
                    print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
                    detalles = []
                    while True:
                        clave_serv = input("\nIngrese la clave del servicio: ")
                        if clave_serv == "":
                            print("\n* La clave no se puede quedar vacía, vuelva a intentar *")
                            continue
                        if not clave_serv.isdigit():
                            print("\n* Clave incorrecta, intente de nuevo. *")
                            continue
                        valores = {"claveServicio": clave_serv}
                        mi_cursor.execute('SELECT * FROM Servicio WHERE claveServicio = :claveServicio \
                                          AND canceladaServicio = 0', valores)
                        servicio = mi_cursor.fetchone()
                        if servicio:
                            detalles.append(clave_serv) 
                            continuar = input("\n¿Desea agregar otro servicio? (si/no): ")
                            if continuar.lower() == "no":
                                break
                            elif continuar.lower() == "si":
                                continue
                            else:
                                print("\nOpcion no valida, intente nuevamente.")
                        else:
                            print("\n* El servicio no existe, ingrese nuevamente *")
                            continue
                    servicios_seleccionados = [mi_cursor.execute('SELECT * FROM Servicio WHERE claveServicio = ?', (clave_serv,)).fetchone() for clave_serv in detalles]
                    monto_total = sum(servicio[2] for servicio in servicios_seleccionados)
                    mi_cursor.execute('INSERT INTO Nota (fecha, claveCliente, monto) VALUES (?, ?, ?)', (fecha.strftime("%Y/%m/%d"), clave_c, monto_total))
                    print(f"\nLa clave asignada fue {mi_cursor.lastrowid}")

                    mi_cursor.executemany('INSERT INTO Detalle (folio, claveServicio) VALUES (?, ?)', [(mi_cursor.lastrowid, clave_serv) for clave_serv in detalles])
            
                    print("¡La nota fue agregada exitosamente!")
                    break
                else:
                    print("\n* El cliente no existe, vuelva a intentar. *")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def cancelar_nota():
    while True:
      can_folio = input("\nFolio de la nota a cancelar: ")

      if can_folio == "":
        print ("\n* Ingrese un folio. *")
        continue
      elif not (bool(re.search('^[0-9]+$', can_folio))):
        print ("\n* Folio no valida, ingrese nuevmente *")
        continue
      else:
        break
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            valor = {"folio":can_folio}
            mi_cursor.execute('SELECT Nota.folio, Nota.fecha, Nota.claveCliente, Cliente.nombreCliente, Cliente.rfc, Cliente.correo, \
                        Nota.monto, Servicio.nombre, Servicio.costo FROM Cliente \
                        INNER JOIN Nota ON Nota.claveCliente = Cliente.claveCliente \
                        INNER JOIN Detalle ON Nota.folio = Detalle.folio \
                        INNER JOIN Servicio ON Detalle.claveServicio = Servicio.claveServicio \
                        WHERE Nota.folio = :folio AND Nota.cancelada=0' ,(valor))

            nota= mi_cursor.fetchall()
            if nota:
                informacion = [[folio, fecha, claveCliente, nombreCliente, rfc, correo, monto, nombre, costo] 
                                for folio, fecha, claveCliente, nombreCliente, rfc, correo, monto, nombre, costo in nota]
                titulos= ["Folio", "Fecha", "Clave cliente", "Nombre Cliente", "RFC cliente", "Correo cliente",
                        "Monto", "Nombre del servicio", "Costo del servicio"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
                confirmar = input("\n¿Está seguro de que desea cancelar esta nota? (Si/No): ")
                if confirmar.lower() == "si":
                    mi_cursor.execute('UPDATE Nota SET cancelada=1 WHERE folio = :folio', (valor))
                    print("\nLa nota fue cancelada con éxito")
                else: 
                    print("\nOperacion cancelada")
            else: 
                print("\nNota no encontrada o cancelada")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")


def recuperar_nota():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute("SELECT Nota.folio, Nota.fecha, Cliente.claveCliente, Cliente.nombreCliente, Cliente.rfc, Cliente.correo,\
                                Nota.monto \
                                FROM Nota \
                                INNER JOIN Cliente ON Nota.claveCliente = Cliente.claveCliente \
                                WHERE cancelada=1")
            nota = mi_cursor.fetchall()
            if nota:
                informacion = [[folio, fecha, claveCliente, nombreCliente, rfc, correo, monto] 
                               for folio, fecha, claveCliente, nombreCliente, rfc, correo, monto in nota]
                titulos = ["Folio", "Fecha", "Clave cliente", "Nombre cliente", "RFC cliente", "Correo cliente", "Monto"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))

                while True:
                    confirmar = input("\nDesea recuperar alguna nota? (Si/No): ")
                    if confirmar.lower() == "si":
                        rec_folio = input("\nFolio de la nota a recuperar: ")

                        if rec_folio == "":
                            print ("\n* Ingrese un folio. *")
                            continue
                        elif not (bool(re.search('^[0-9]+$', rec_folio))):
                            print ("\n* Folio no valida, ingrese nuevamente *")
                            continue
                        valor= {"folio":rec_folio}
                        mi_cursor.execute('SELECT Servicio.nombre, Servicio.costo FROM Nota INNER JOIN Detalle ON Nota.folio \
                                        = Detalle.folio INNER JOIN Servicio ON Detalle.claveServicio = Servicio.claveServicio \
                                        WHERE Nota.folio = :folio' ,(valor))
                        nota= mi_cursor.fetchall()
                        if nota:
                            informacion = [[nombre, costo] for  nombre, costo in nota]
                            titulos= ["Nombre del servicio", "Costo del servicio"]
                            print(tabulate(informacion, titulos, tablefmt="fancy_grid"))

                            confirmacion= input("\nEstá seguro que desea recuperar esta nota? (Si/No): ")
                            if confirmacion.lower() == 'si':
                                mi_cursor.execute('UPDATE Nota SET cancelada= 0 WHERE folio= :folio' ,(valor))
                                print("\nNota recuperada con éxito")
                                break
                            else:
                                print("\nOperacion cancelada")
                                break
                        else: 
                            print("\n* Nota no existente, ingrese nuevamente *")
                            continue
                    elif confirmar.lower() == "no":
                        print("\nOperacion cancelada")
                        break
            else:
                print("\nNo hay notas canceladas")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                            
def consulta_por_periodo():
    while True:
        fecha_inicial = input("\nIngresa la fecha inicial (dd/mm/aaaa): ")
        if fecha_inicial == "":
            fecha_inicial = "01/01/2000"
            print("\nPor omision de fecha inicial se asume 01/01/2000.")

        fecha_final = input("\nIngresa la fecha final (dd/mm/aaaa): ")
        if fecha_final == "":
            fecha_final = datetime.date.today().strftime("%d/%m/%Y")
            print("\nPor omision de fecha final se asume la fecha actual. ")

        try:
            fecha_inicial_obj = datetime.datetime.strptime(fecha_inicial, "%d/%m/%Y").date()
            fecha_final_obj = datetime.datetime.strptime(fecha_final, "%d/%m/%Y").date()
        except Exception:
            print("\n* Las fechas ingresadas deben estar en formato dd/mm/aaaa *")
            continue

        if fecha_final < fecha_inicial:
            print("\n* La fecha final no puede ser anterior a la fecha inicial *")
            continue
        else:
            break
    try:
        if fecha_final_obj >= fecha_inicial_obj:
            fecha_inicial = fecha_inicial_obj.strftime("%Y/%m/%d")
            fecha_final = fecha_final_obj.strftime("%Y/%m/%d")

        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT Nota.folio, Nota.fecha, Cliente.claveCliente, Cliente.nombreCliente, Cliente.rfc, Cliente.correo,\
                                Nota.monto \
                                FROM Nota \
                                INNER JOIN Cliente ON Nota.claveCliente = Cliente.claveCliente \
                                WHERE fecha BETWEEN ? AND ? AND cancelada=0", (fecha_inicial, fecha_final))
            notas = mi_cursor.fetchall()

        if notas:
            total_montos = sum(nota[6] for nota in notas)
            promedio_montos = total_montos / len(notas)

            print(f"\n                                         Notas del periodo especificado")
            informacion = [[folio, fecha, claveCliente, nombreCliente, rfc, correo, monto] 
                           for folio, fecha, claveCliente, nombreCliente, rfc, correo, monto in notas]
            titulos = ["Folio", "Fecha", "Clave cliente", "Nombre cliente", "RFC cliente", "Correo cliente", "Monto"]
            print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            print(f"Monto promedio: {promedio_montos}")

            df = pd.DataFrame(informacion, columns=titulos)
            while True:
                print("\nOpciones a realizar con su reporte")
                print("\n1. Exportar a CSV\n2. Exportar a Excel\n3. Regresar al menú de reportes")
                opcion = input("Ingrese una opción: ")

                if opcion == "1":
                    fecha_inicial_str = fecha_inicial_obj.strftime('%d_%m_%Y')
                    fecha_final_str = fecha_final_obj.strftime('%d_%m_%Y')
                    archivo_csv = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.csv"
                    df.to_csv(archivo_csv, index=False)
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_csv}' *")
                    print(f"\nEl archivo '{archivo_csv}' se ha guardado en la ubicación: {os.path.abspath(archivo_csv)}")
                    break
                elif opcion == "2":
                    fecha_inicial_str = fecha_inicial_obj.strftime('%d_%m_%Y')
                    fecha_final_str = fecha_final_obj.strftime('%d_%m_%Y')
                    archivo_excel = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.xlsx"
                    df.to_excel(archivo_excel, index=False, engine='openpyxl')
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_excel}' *")
                    print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
                    break
                elif opcion == "3":
                    print("\nOK")
                    break
                else:
                    print("\nOpción no válida, ingrese nuevamente.")
        else:
            print("\nNo se encontraron notas en el período especificado")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def consulta_por_folio():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute('SELECT Nota.folio, Nota.fecha, Cliente.nombreCliente FROM Nota \
                  INNER JOIN Cliente ON Nota.claveCliente = Cliente.claveCliente \
                  WHERE cancelada = 0 \
                  ORDER BY Nota.folio')
            
            nota = mi_cursor.fetchall()
            if nota:
                informacion = [[folio, fecha, nombreCliente] for folio, fecha, nombreCliente in nota]
                titulos= ["Folio", "Fecha", "Nombre cliente"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
                
                while True:
                    con_folio = input("\nFolio de la nota a consultar: ")

                    if con_folio == "":
                        print ("\n* Ingrese un folio. *")
                        continue
                    elif not (bool(re.search('^[0-9]+$', con_folio))):
                        print ("\n* Folio no valida, ingrese nuevmente *")
                        continue
                    mi_cursor= conn.cursor()
                    valor = {"folio":con_folio}
                    mi_cursor.execute('SELECT Nota.folio, Nota.fecha, Nota.claveCliente, Cliente.nombreCliente, Cliente.rfc, Cliente.correo, \
                        Nota.monto, Servicio.nombre, Servicio.costo FROM Cliente \
                        INNER JOIN Nota ON Nota.claveCliente = Cliente.claveCliente \
                        INNER JOIN Detalle ON Nota.folio = Detalle.folio \
                        INNER JOIN Servicio ON Detalle.claveServicio = Servicio.claveServicio \
                        WHERE Nota.folio = :folio AND Nota.cancelada=0' ,(valor))

                    nota= mi_cursor.fetchall()
                    if nota:
                        informacion = [[folio, fecha, claveCliente, nombreCliente, rfc, correo, monto, nombre, costo] 
                                       for folio, fecha, claveCliente,nombreCliente, rfc, correo, monto, nombre, costo in nota]
                        titulos= ["Folio", "Fecha", "Clave cliente", "Nombre Cliente", "RFC cliente", "Correo cliente",
                                  "Monto", "Nombre del servicio", "Costo del servicio"]
                        print(tabulate(informacion, titulos, tablefmt="fancy_grid"))  
                        break
                    else: 
                        print("\nNota no encontrada o cancelada")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def agregar_cliente():
    while True:
      nombre = input("\nNombre del cliente: ")
      if nombre == "":
        print ("\n* INGRESE NOMBRE DEL CLIENTE *")
        continue
      elif not (bool(re.search('^[a-zA-Z ]+$', nombre))):
        print ("\n* NOMBRE NO VALIDO, INGRESE NUEVAMENTE *")
        continue
      else:
        break
    
    rfc_registrados = set()
    while True:
        rfc = input("\nIngrese RFC del cliente: ")
        if rfc == "":
            print("\n* INGRESE UN RFC PARA EL REGISTRO DE LA NOTA *")
            continue
        elif re.search('^[A-Z]{3,4}[0-9]{6}[A-Z0-9]{3}$', rfc) is None:
            print("\n* RFC NO VALIDO, INGRESE NUEVAMENTE *")
            continue
        else:
            rfc_registrados.add(rfc)
            break
    
    while True:
        correo = input("\nIngrese el correo del cliente: ")
        if correo == "":
            print("\n* INGRESE UN CORREO PARA EL REGISTRO DE LA NOTA *")
            continue
        correo = correo.strip()
        if re.search('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', correo) is None:
            print("\n* CORREO NO VALIDO, INGRESE NUEVAMENTE *")
            continue
        else:
            break
      
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            valores = (nombre, rfc, correo)
            mi_cursor.execute("INSERT INTO Cliente (nombreCliente, rfc, correo) VALUES (?,?,?)", valores)
            print(f"\nLa clave asignada fue {mi_cursor.lastrowid}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def suspender_cliente():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute('SELECT claveCliente, nombreCliente FROM Cliente \
                                WHERE canceladaCliente=0')
            suspender_cliente= mi_cursor.fetchall()
            if suspender_cliente:
                informacion = [[claveCliente, nombreCliente] 
                                for claveCliente, nombreCliente in suspender_cliente]
                titulos= ["Clave cliente", "Nombre Cliente"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
                while True:
                    confirmar = input("\n¿Está seguro de que desea suspender algun cliente? (1.Si/0.No): ")
                    if confirmar == "1":
                        while True:
                            clave = input("\nClave del cliente a suspender: ")
                            if clave == "":
                                print ("\n* Ingrese una clave para la suspensión del cliente. *")
                            elif not (bool(re.search('^[0-9]+$', clave))):
                                print ("\n* Clave no valida, ingrese nuevmente *")
                            else:
                                break
                        mi_cursor= conn.cursor()
                        valor = {"claveCliente":clave}
                        mi_cursor.execute('SELECT claveCliente, nombreCliente, rfc, correo FROM Cliente \
                                            WHERE canceladaCliente=0 AND claveCliente = :claveCliente', valor)
                        cliente= mi_cursor.fetchall()
                        if cliente:
                            informacion = [[claveCliente, nombreCliente, rfc, correo] 
                                            for claveCliente, nombreCliente, rfc, correo in cliente]
                            titulos= ["Clave cliente", "Nombre Cliente", "RFC", "Correo"]
                            print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
                            while True:
                                print("\nOpciones a realizar")
                                opcion = input("\n1. Suspender cliente\n2. Volver al menu anterior\nIngrese una opción: ")
                                if opcion == "1":
                                    mi_cursor.execute('UPDATE Cliente SET canceladaCliente=1 WHERE claveCliente = :claveCliente', (valor))
                                    print("\nCliente suspendido con éxito")
                                    return False
                                elif opcion == "2":
                                    print("\nOperacion cancelada")
                                    return False
                                else:
                                    print("\nOpción no válida, ingrese nuevamente.")
                                    continue
                        else:
                            print("\n* Cliente no encontrado o ya suspendido *")
                            continue
                    elif confirmar == "0":
                        print("\nOperacion cancelada")
                        break
                    else:
                        print("\nOpción no válida, ingrese nuevamente.")
                        continue
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def recuperar_cliente():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute('SELECT claveCliente, nombreCliente FROM Cliente \
                                WHERE canceladaCliente=1')

            suspender_cliente= mi_cursor.fetchall()
            if suspender_cliente:
                informacion = [[claveCliente, nombreCliente] 
                                for claveCliente, nombreCliente in suspender_cliente]
                titulos= ["Clave cliente", "Nombre Cliente"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))

                while True:
                    confirmar = input("\n¿Está seguro de que desea recuperar algun cliente? (1.Si/0.No): ")
                    if confirmar == "1":
                        while True:
                            clave = input("\nClave del cliente a recuperar: ")
                            if clave == "" or clave.isspace():
                                print ("\n* Ingrese una clave para la recuperacion del cliente. *")
                            elif not (bool(re.search('^[0-9]+$', clave))):
                                print ("\n* Clave no valida, ingrese nuevmente *")
                            else:
                                break
                        mi_cursor= conn.cursor()

                        valor = {"claveCliente":clave}
                        mi_cursor.execute('SELECT claveCliente, nombreCliente, rfc, correo FROM Cliente \
                                            WHERE canceladaCliente=1 AND claveCliente = :claveCliente', valor)
                        cliente= mi_cursor.fetchall()
                        if cliente:
                            informacion = [[claveCliente, nombreCliente, rfc, correo] 
                                            for claveCliente, nombreCliente, rfc, correo in cliente]
                            titulos= ["Clave cliente", "Nombre Cliente", "RFC", "Correo"]
                            print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
                            while True:
                                print("\nOpciones a realizar")
                                opcion = input("\n1. Recuperar cliente\n2. Volver al menu anterior\nIngrese una opción: ")
                                if opcion == "1":
                                    mi_cursor.execute('UPDATE Cliente SET canceladaCliente=0 WHERE claveCliente = :claveCliente', (valor))
                                    print("\nCliente recuperado con éxito")
                                    return False
                                elif opcion == "2":
                                    print("\nOperacion cancelada")
                                    return False
                        else:
                            print("\n* Cliente no encontrado o ya recuperado *")
                            continue
                    elif confirmar == "0":
                        print("\nOperacion cancelada")
                        break
                    else:
                        print("\nOpción no válida, solamente 1 o 0.")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def clientes_ordenados_por_claves():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT claveCliente, nombreCliente, rfc, correo FROM Cliente \
                              WHERE canceladaCliente = 0 ORDER BY claveCliente")
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[clave, nombreCliente, rfc, correo] for clave, nombreCliente, rfc, correo in registro]
                titulos = ["Clave", "Nombre Cliente", "RFC", "Correo"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            else:
                print(f"\nNo hay clientes registrados")
            df = pd.DataFrame(informacion, columns=titulos)
            while True:
                print("\nOpciones a realizar con su reporte")
                print("\n1. Exportar a CSV\n2. Exportar a Excel\n3. Regresar al menú de reportes")
                opcion = input("Ingrese una opción: ")
                if opcion == "1":
                    fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
                    archivo_csv = f"ReporteClientesActivosPorClave_{fecha_actual}.csv"
                    df.to_csv(archivo_csv, index=False)
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_csv}' *")
                    print(f"\nEl archivo '{archivo_csv}' se ha guardado en la ubicación: {os.path.abspath(archivo_csv)}")
                    break
                elif opcion == "2":
                    fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
                    archivo_excel = f"ReporteClientesActivosPorClave_{fecha_actual}.xlsx"
                    df.to_excel(archivo_excel, index=False, engine='openpyxl')
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_excel}' *")
                    print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
                    break
                elif opcion == "3":
                    print("\nOK")
                    break
                else:
                    print("\nOpción no válida, ingrese nuevamente.")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def clientes_ordenados_por_nombres():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT claveCliente, nombreCliente, rfc, correo FROM Cliente \
                              WHERE canceladaCliente = 0 ORDER BY nombreCliente")
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[clave, nombreCliente, rfc, correo] for clave, nombreCliente, rfc, correo in registro]
                titulos = ["Clave", "Nombre Cliente", "RFC", "Correo"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            else:
                print(f"\nNo hay clientes registrados")
            df = pd.DataFrame(informacion, columns=titulos)
            while True:
                print("\nOpciones a realizar con su reporte")
                print("\n1. Exportar a CSV\n2. Exportar a Excel\n3. Regresar al menú de reportes")
                opcion = input("Ingrese una opción: ")
                if opcion == "1":
                    fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
                    archivo_csv = f"ReporteClientesActivosPorNombre_{fecha_actual}.csv"
                    df.to_csv(archivo_csv, index=False)
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_csv}' *")
                    print(f"\nEl archivo '{archivo_csv}' se ha guardado en la ubicación: {os.path.abspath(archivo_csv)}")
                    break
                elif opcion == "2":
                    fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
                    archivo_excel = f"ReporteClientesActivosPorNombre_{fecha_actual}.xlsx"
                    df.to_excel(archivo_excel, index=False, engine='openpyxl')
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_excel}' *")
                    print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
                    break
                elif opcion == "3":
                    print("\nOK")
                    break
                else:
                    print("\nOpción no válida, ingrese nuevamente.")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def cliente_busqueda_por_clave():
    while True:
      valor_clave = input("\nClave del cliente a consultar: ")

      if valor_clave == "":
        print ("\n* Ingrese una clave para la busqueda del cliente. *")
        continue
      elif not (bool(re.search('^[0-9]+$', valor_clave))):
        print ("\n* Clave no valida, ingrese nuevmente *")
        continue
      else:
        break
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            valores = {"claveCliente":valor_clave}
            mi_cursor.execute("SELECT claveCliente, nombreCliente, rfc, correo \
                               FROM Cliente WHERE claveCliente = :claveCliente AND canceladaCliente=0", valores)
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[claveCliente, nombreCliente, rfc, correo] for claveCliente, nombreCliente, rfc, correo in registro]
                titulos = ["Clave", "Nombre Cliente", "RFC", "Correo"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            else:
                print(f"\nNo se encontró un cliente asociado con la clave {valor_clave}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def cliente_busqueda_por_nombre():
    while True:
      valor_nombre = input("\nNombre del cliente a consultar: ")

      if valor_nombre == "":
        print ("\n* Ingrese un nombre para la busqueda del cliente. *")
        continue
      elif not (bool(re.search('^[a-zA-Z ]+$', valor_nombre))):
        print ("\n* Nombre no valido, ingrese nuevmente *")
        continue
      else:
        break
      
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            valores = {"nombreCliente":valor_nombre}
            mi_cursor.execute("SELECT claveCliente, nombreCliente, rfc, correo FROM Cliente \
                              WHERE nombreCliente = :nombreCliente AND canceladaCliente=0", valores)
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[claveCliente, nombreCliente, rfc, correo] for claveCliente, nombreCliente, rfc, correo in registro]
                titulos = ["Clave", "Nombre Cliente", "RFC", "Correo"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            else:
                print(f"\nNo se encontró un cliente asociado con el nombre ingresado {valor_nombre}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def agregar_servicio():
    while True:
      nombre = input("\nNombre del servicio: ")
      if nombre == "":
        print ("\n* INGRESE NOMBRE DE SERVICIO *")
        continue
      elif not (bool(re.search('^[a-zA-Z ]+$', nombre))):
        print ("\n* NOMBRE NO VALIDO, INGRESE NUEVAMENTE *")
        continue
      else:
        break

    while True:
        costo = input("\nIngrese el costo del servicio: ")
        if costo == "":
            print("\n* EL SERVICIO DEBE TENER SU COSTO, INGRESE POR FAVOR *")
            continue
        try:
            costo = float(costo)
            if costo != float(f"{costo:.2f}"):
                print("\n* NO SE PERMITEN MAS DE 2 DECIMALES, INGRESE NUEVAMENTE *")
                continue
        except Exception:
            print ("\n* COSTO NO VALIDO, INGRESE NUEVAMENTE *")
            continue
        if costo <= 0:
            print("\n* EL COSTO DEL SERVICIO DEBE SER MAYOR A 0, INGRESE NUEVAMENTE *")
            continue
        else:
            break
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            valores = (nombre, costo)
            mi_cursor.execute("INSERT INTO Servicio (nombre, costo) VALUES (?,?)", valores)
            print(f"\nLa clave asignada fue {mi_cursor.lastrowid}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def suspender_servicio():
   try:
       with sqlite3.connect("TallerMecanico.db") as conn:
           mi_cursor = conn.cursor()
           mi_cursor.execute('SELECT claveServicio, nombre FROM Servicio WHERE canceladaServicio=0')
           servicios = mi_cursor.fetchall()

           if servicios:
              campos = [[claveServicio, nombre] for claveServicio, nombre in servicios]
              alias = ["Clave Servicio", "Nombre Servicio"]
              print(tabulate(campos, alias, tablefmt="fancy_grid"))

              while True:
                    confirmacion = input("\n¿Desea suspender algún servicio? (Si: 1 / No: 0): ")
                    if confirmacion == "1" :
                        while True:
                            clave= input("\nIngrese la clave del servicio a suspender: ")
                            if clave.isspace():
                               print("NO SE PUEDE OMITIR LA OPCION")
                            else:
                                break
                        valor= {"claveServicio": clave}
                        mi_cursor.execute('SELECT claveServicio, nombre, costo FROM Servicio \
                                          WHERE canceladaServicio=0 AND claveServicio = :claveServicio', (valor))
                        servicio = mi_cursor.fetchall()

                        if servicio:
                            campos = [[claveServicio, nombre, costo] for claveServicio, nombre, costo in servicio]
                            alias = ["Clave Servicio", "Nombre Servicio", "Costo Servicio"]
                            print(tabulate(campos, alias, tablefmt="fancy_grid"))
                            print("\nOpciones a realizar: ")
                            opcion = input("\n1. Suspender servicio\n2. Volver al menú principal\n3. Ingrese una opción: ")
                            if opcion == "1":
                               mi_cursor.execute('UPDATE Servicio SET canceladaServicio=1 WHERE claveServicio= :claveServicio', valor)
                               print("\nSe suspendió el servicio exitosamente")
                               break
                            elif opcion ==  "2":
                                 print("\nOperacion cancelada")
                                 return False
                            else: 
                                print("\nOperacion no válida, ingrese nuevamente")
                                break
                        else: 
                            print("\n No se pudo encontrar el servicio o fue cancelado")
                    elif confirmacion == "0":
                         print("\nOperación cancelada")
                         break
                    else: 
                        print("\nOpción no válida, ingrese nuevamente")
   except Error as e: 
      print(e)
   except Exception:
      print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    
def recuperar_servicio():
   try:
      with sqlite3.connect("TallerMecanico.db") as conn:
           mi_cursor= conn.cursor()
           mi_cursor.execute('SELECT claveServicio, nombre FROM Servicio WHERE canceladaServicio=1')
           suspender_servicio= mi_cursor.fetchall()

           if suspender_servicio:
               campos = [[claveServicio, nombre] for claveServicio, nombre in suspender_servicio]
               alias = ["Clave Servicio", "Nombre Servicio"]
               print(tabulate(campos, alias, tablefmt="fancy_grid"))

               while True:
                    confirmacion= input("\n¿Desea recuperar algún servicio? (Si: 1/ No: 0): ")
                    if confirmacion == " ":
                        print("NO SE PUEDE OMITIR LA OPCION")
                        continue
                    elif confirmacion == "1":
                        while True:
                             clave = input("\nIngrese la clave del servicio a recuperar: ")
                             if clave == " ":
                                print("NO SE PUEDE OMITIR LA OPCION")
                                continue
                             else:
                                break
                        valor= {"claveServicio": clave}
                        mi_cursor.execute('SELECT claveServicio, nombre, costo FROM Servicio \
                                            WHERE canceladaServicio=1 AND claveServicio= :claveServicio', valor)
                        servicio = mi_cursor.fetchall()

                        if servicio:
                            campos = [[claveServicio, nombre, costo] for claveServicio, nombre, costo in servicio]
                            alias = ["Clave Servicio", "Nombre Servicio", "Costo Servicio"]
                            print(tabulate(campos, alias, tablefmt="fancy_grid"))
                            print("\n * Opciones a realizar: *")

                            opcion = input("\n1. Recuperar servicio\n2. Volver al menú prinipal\nIngrese una opción: ")
                            if opcion == "1":
                               mi_cursor.execute('UPDATE Servicio SET canceladaServicio=0 WHERE claveServicio= :claveServicio', valor)
                               print("\nEl servicio se recuperó con éxito")
                               break
                            elif opcion == "2":
                               print("\nOperación cancelada")
                               return False
                        else:
                           print("\n * Servicio no encontrado o ya fue recuperado *")
                           continue
                    elif confirmacion == "0":
                          print("\nOperación cancelada")
                          break
                    else: 
                     print("\nOpcion no válida")
   except Error as e:
    print(e)
   except Exception:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def busqueda_por_clave_servicio():
    while True:
      v_clave = input("\nClave del servicio a consultar: ")

      if v_clave == "":
        print ("\n* Ingrese una clave para la busqueda del servicio. *")
        continue
      elif not (bool(re.search('^[0-9]+$', v_clave))):
        print ("\n* Clave no valida, ingrese nuevmente *")
        continue
      else:
        break
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            valores = {"claveServicio":v_clave}
            mi_cursor.execute("SELECT claveServicio, nombre, costo FROM Servicio WHERE claveServicio = :claveServicio AND canceladaServicio = 0", valores)
            registro = mi_cursor.fetchall()

            if registro:
                datos = [[clave, nombre, costo] for clave, nombre, costo in registro]
                Columnas = ["Clave", "Nombre", "Costo"]
                print(tabulate(datos, Columnas, tablefmt="fancy_grid"))
            else:
                print(f"\nNo se encontró un servicio asociado con la clave ingresada: {v_clave}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def busqueda_por_nombre_servicio():
    while True:
      v_nombre = input("\nNombre del servicio a consultar: ")

      if v_nombre == "":
        print ("\n* Ingrese un nombre para la busqueda del servicio. *")
        continue
      elif not (bool(re.search('^[a-zA-Z ]+$', v_nombre))):
        print ("\n* Nombre no valido, ingrese nuevamente *")
        continue
      else:
        break
      
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            valores = {"nombre":v_nombre}
            mi_cursor.execute("SELECT claveServicio, nombre, costo FROM Servicio WHERE nombre = :nombre AND canceladaServicio=0", valores)
            registro = mi_cursor.fetchall()

            if registro:
                datos = [[clave, nombre, costo] for clave, nombre, costo in registro]
                Columnas = ["Clave", "Nombre", "Costo"]
                print(tabulate(datos, Columnas, tablefmt="fancy_grid"))
            else:
                print(f"\nNo se encontró un servicio asociado con el nombre ingresado:  {v_nombre}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def servicios_por_clave():
   try:
    with sqlite3.connect("TallerMecanico.db") as conn:
      mi_cursor = conn.cursor()
      mi_cursor.execute("SELECT claveServicio, nombre, costo FROM Servicio WHERE canceladaServicio=0 ORDER BY claveServicio")
      registro = mi_cursor.fetchall()

      if registro:
        datos = [[clave, nombre, costo] for clave, nombre, costo in registro]
        Columnas = ["Clave", "Nombre", "Costo"]
        print(tabulate(datos, Columnas, tablefmt="fancy_grid"))
      else:
        print(f"\nNo hay servicios registrados")
      df = pd.DataFrame(datos, columns=Columnas)

      while True:
        print("\nOpciones a realizar con su reporte")
        print("\n1. Exportar a CSV\n2. Exportar a Excel\n3. Regresar al menú de reportes")
        opcion = input("Ingrese una opción: ")
        if opcion == "1":
          fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
          archivo_csv = f"ReporteServiciosActivosPorClave_{fecha_actual}.csv"
          df.to_csv(archivo_csv, index=False)
          print(f"\n* El reporte se ha guardado con el nombre: '{archivo_csv}' *")
          print(f"\nEl archivo '{archivo_csv}' se ha guardado en la ubicación: {os.path.abspath(archivo_csv)}")
          break
        elif opcion == "2":
          fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
          archivo_excel = f"ReporteServiciosPorClave_{fecha_actual}.xlsx"
          df.to_excel(archivo_excel, index=False, engine='openpyxl')
          print(f"\n* El reporte se ha guardado con el nombre: '{archivo_excel}' *")
          print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
          break
        elif opcion == "3":
         print("\nOK")
         break
        else:
          print("\nOpción no válida, ingrese nuevamente.")
   except Error as e:
    print (e)
   except Exception:
    print (f"se produjo el error: {sys.exc_info()[0]}")

def servicios_por_nombre():
 try:
      with sqlite3.connect("TallerMecanico.db") as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("SELECT claveServicio, nombre, costo FROM Servicio WHERE canceladaServicio=0 ORDER BY nombre")
        registro = mi_cursor.fetchall()

        if registro:
          datos = [[clave, nombre, costo] for clave, nombre, costo in registro]
          Columnas = ["Clave", "Nombre", "Costo"]
          print(tabulate(datos, Columnas, tablefmt="fancy_grid"))
        else:
          print(f"\nNo hay servicios registrados")
        df = pd.DataFrame(datos, columns=Columnas)
        while True:
          print("\nOpciones a realizar con su reporte")
          print("\n1. Exportar a CSV\n2. Exportar a Excel\n3. Regresar al menú de reportes")
          opcion = input("Ingrese una opción: ")
          if opcion == "1":
            fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
            archivo_csv = f"ReporteServiciosPorNombre_{fecha_actual}.csv"
            df.to_csv(archivo_csv, index=False)
            print(f"\n* El reporte se ha guardado con el nombre: '{archivo_csv}' *")
            print(f"\nEl archivo '{archivo_csv}' se ha guardado en la ubicación: {os.path.abspath(archivo_csv)}")
            break
          elif opcion == "2":
            fecha_actual = datetime.datetime.now().strftime('%m_%d_%Y')
            archivo_excel = f"ReporteServiciosActivosPorNombre_{fecha_actual}.xlsx"
            df.to_excel(archivo_excel, index=False, engine='openpyxl')
            print(f"\n* El reporte se ha guardado con el nombre: '{archivo_excel}' *")
            print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
            break
          elif opcion == "3":
            print("\nOK")
            break
          else:
            print("\nOpción no válida, ingrese nuevamente.")
 except Error as e:
   print (e)
 except Exception:
   print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def servicios_mas_solicitados():
    while True:
        num_servicios = input("\nCantidad de servicios más prestados a identificar: ")
        if num_servicios == "":
            print("\n* Ingrese una cantidad, no puede quedar vacío. *")
            continue
        elif num_servicios == "0":
            print ("\nEl numero de servicios a consultar no puede ser inferior a 1 (uno).")
            continue
        elif not bool(re.search('^[0-9]+$', num_servicios)):
            print("\n* Clave no válida, ingrese nuevamente. *")
            continue
        else:
            num_servicios = int(num_servicios)
            break
    while True:
        fecha_inicial = input("\nIngrese la fecha inicial del período a reportar (dd/mm/yyyy): ")
        if fecha_inicial == "":
            print("\n* Ingrese una fecha, no puede quedar vacío. *")
            continue
        fecha_final = input("\nIngrese la fecha final del período a reportar (dd/mm/yyyy): ")
        if fecha_final == "":
            print("\n* Ingrese una fecha, no puede quedar vacío. *")
            continue
        try:
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d/%m/%Y").date()
            fecha_final = datetime.datetime.strptime(fecha_final, "%d/%m/%Y").date()
            if fecha_final < fecha_inicial:
                print("\n* La fecha final no puede ser anterior a la fecha inicial, ingrese nuevamente *")
                continue
        except Exception:
            print("\n* Fecha inválida *")
            continue
        break
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute(
                "SELECT Servicio.nombre AS NombreServicio, COUNT(Detalle.claveServicio) AS CantidadServicios "
                "FROM Detalle "
                "JOIN Servicio ON Detalle.claveServicio = Servicio.claveServicio "
                "JOIN Nota ON Detalle.folio = Nota.folio "
                "WHERE Nota.fecha BETWEEN ? AND ? "
                "GROUP BY Detalle.claveServicio "
                "ORDER BY CantidadServicios DESC "
                "LIMIT ?;",
                (fecha_inicial.strftime("%Y/%m/%d"), fecha_final.strftime("%Y/%m/%d"), num_servicios),
            )

            resultados = mi_cursor.fetchall()

            if not resultados:
                print("\n* No hay resultados para el período seleccionado *")
                return

            informacion = [[nombre_servicio, cantidad] for nombre_servicio, cantidad in resultados]
            titulos = ["Nombre del Servicio", "Cantidad de Servicios Prestados"]

            print("\nReporte de Servicios Más Prestados:")
            print(tabulate(informacion, titulos, tablefmt="fancy_grid"))

            df = pd.DataFrame(informacion, columns=titulos)
            while True:
                print("\nOpciones a realizar con su reporte")
                opcion = input("\n1. Exportar a CSV\n2. Exportar a Excel\n3. Ingrese una opción: ")

                if opcion == "1":
                    fecha_inicial_str = fecha_inicial.strftime("%d_%m_%Y")
                    fecha_final_str = fecha_final.strftime("%y_%m_%Y")
                    archivo_csv = f"ReporteServiciosMasPrestados_{fecha_inicial_str}_{fecha_final_str}.csv"
                    df.to_csv(archivo_csv, index=False)
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_csv}' *")
                    print(f"\nEl archivo '{archivo_csv}' se ha guardado en la ubicación: {os.path.abspath(archivo_csv)}")
                    break
                elif opcion == "2":
                    fecha_inicial_str = fecha_inicial.strftime("%d_%m_%Y")
                    fecha_final_str = fecha_final.strftime("%d_%m_%Y")
                    archivo_excel = f"ReporteServiciosMasPrestados_{fecha_inicial_str}_{fecha_final_str}.xlsx"
                    df.to_excel(archivo_excel, index=False, engine='openpyxl')
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_excel}' *")
                    print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
                    break
    except sqlite3.Error as e:
        print(e)
    except Exception as e:
        print(e)

def clientes_con_mas_notas():
    while True:
        num_clientes = input("\nCantidad de clientes más prestados a identificar: ")
        if num_clientes == "":
            print("\n* Ingrese una cantidad, no puede quedar vacío. *")
            continue
        elif not bool(re.search('^[0-9]+$', num_clientes)):
            print("\n* Clave no válida, ingrese nuevamente. *")
            continue
        elif num_clientes == "0":
            print ("El minimo de clientes a mostrar debe ser de 1 (uno).")
            continue
        else:
            num_clientes = int(num_clientes)
            break

    while True:
        fecha_inicial = input("\nIngrese la fecha inicial del período a reportar (dd/mm/yyyy): ")
        if fecha_inicial == "":
            print("\n* Ingrese una fecha, no puede quedar vacío. *")
            continue
        fecha_final = input("\nIngrese la fecha final del período a reportar (dd/mm/yyyy): ")
        if fecha_final == "":
            print("\n* Ingrese una fecha, no puede quedar vacío. *")
            continue
        try:
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d/%m/%Y").date()
            fecha_final = datetime.datetime.strptime(fecha_final, "%d/%m/%Y").date()
            if fecha_final < fecha_inicial:
                print("\n* La fecha final no puede ser anterior a la fecha inicial, ingrese nuevamente *")
                continue
        except Exception:
            print("\n* Fecha inválida *")
            continue
        break
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute(
                "SELECT Cliente.nombreCliente AS nombreCliente, COUNT(Nota.folio) AS CantidadNotas "
                "FROM Nota "
                "JOIN Cliente ON Nota.claveCliente = Cliente.claveCliente "
                "WHERE Nota.fecha BETWEEN ? AND ? "
                "GROUP BY Nota.claveCliente "
                "ORDER BY CantidadNotas DESC "
                "LIMIT ?;",
                (fecha_inicial.strftime("%Y/%m/%d"), fecha_final.strftime("%Y/%m/%d"), num_clientes),
            )

            resultados = mi_cursor.fetchall()

            if not resultados:
                print("\n* No hay resultados para el período seleccionado *")
                return

            informacion = [[nombre_cliente, cantidad] for nombre_cliente, cantidad in resultados]
            titulos = ["Nombre del Cliente", "Cantidad de Notas"]

            print("\nReporte de Clientes con mas notas:")
            print(tabulate(informacion, titulos, tablefmt="fancy_grid"))

            df = pd.DataFrame(informacion, columns=titulos)
            while True:
                print("\nOpciones a realizar con su reporte")
                opcion = input("\n1. Exportar a CSV\n2. Exportar a Excel\n3. Ingrese una opción: ")

                if opcion == "1":
                    fecha_inicial_str = fecha_inicial.strftime("%d_%m_%Y")
                    fecha_final_str = fecha_final.strftime("%d_%m_%Y")
                    archivo_csv = f"ReporteClientesConMasNotas_{fecha_inicial_str}_{fecha_final_str}.csv"
                    df.to_csv(archivo_csv, index=False)
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_csv}' *")
                    print(f"\nEl archivo '{archivo_csv}' se ha guardado en la ubicación: {os.path.abspath(archivo_csv)}")
                    break
                elif opcion == "2":
                    fecha_inicial_str = fecha_inicial.strftime("%d_%m_%Y")
                    fecha_final_str = fecha_final.strftime("%d_%m_%Y")
                    archivo_excel = f"ReporteClientesConMasNotas_{fecha_inicial_str}_{fecha_final_str}.xlsx"
                    df.to_excel(archivo_excel, index=False, engine='openpyxl')
                    print(f"\n* El reporte se ha guardado con el nombre: '{archivo_excel}' *")
                    print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
                    break
    except sqlite3.Error as e:
        print(e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def promedio_montos_notas():
    while True:
        fecha_inicial= input("\nDefine la fecha inicial de tu reporte(dd/mm/yyyy): ")
        if fecha_inicial == "":
            print ("\n* Ingrese una fecha, no puede quedar vacío. *")
            continue
        fecha_final= input ("\nDefine la fecha fin para tu reporte(dd/mm/yyyy): ")
        if fecha_final == "":
            print ("\n* Ingrese una fecha, no puede quedar vacío. *")
            continue
        try:
            fecha_inicial= datetime.datetime.strptime(fecha_inicial, "%d/%m/%Y").date()
            fecha_final = datetime.datetime.strptime (fecha_final, "%d/%m/%Y").date()
            if fecha_final<fecha_inicial:
                print ("\n* La fecha final no puede ser inferior a la fecha inicial del reporte, intenta de nuevo *")
                continue
        except Exception:
            print ("\n* La fecha invalida * ")
            return
        try:
            with sqlite3.connect ("TallerMecanico.db") as conn:
                mi_cursor = conn.cursor()
                mi_cursor.execute (
                    "SELECT COUNT(folio), SUM(monto) FROM Nota WHERE fecha BETWEEN ? AND ?",
                    (fecha_inicial.strftime("%Y/%m/%d"), fecha_final.strftime("%Y/%m/%d"))
                )
                resultados = mi_cursor.fetchone()
                if resultados[0] == 0:
                    print("\n* No hay notas para el período seleccionado *")
                    return
                
                cantidad_notas = resultados[0]
                total_montos = resultados[1]

                promedio = total_montos / cantidad_notas
                print("\nReporte de Montos en el Período:")
                print(f"\nTotal de Notas en el periodo: {cantidad_notas}")
                print(f"\nTotal de Montos en el periodo: {total_montos}")
                print(f"\nPromedio de los Montos: {promedio}")
                break
        except Error as e:
            print (e)
        except Exception:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        

print("** BIENVENIDO AL SERVICIO DE AUTOMOVILES **")
while True:
    print("\n** MENU PRINCIPAL **")
    print("\n1. Menu Notas\n2. Menu Clientes\n3. Menu Servicios\n4. Estadisticos\n5. Salir")
    opcion = input("Ingresa una opcion: ")
    if opcion == "1":
        while True:
            print("\n** Menu Notas **")
            print("\n1. Registrar una nota\n2. Cancelar una nota\n3. Recuperar una nota\n4. Consultas y reportes\n5. Volver al menu principal")
            opcion_nota = input("\nIngrese una opcion: ")
            if opcion_nota == "":
                print("\n* Opcion omitida, Ingrese una opcion *")
                continue

            if opcion_nota == "1":
                if validar_continuidad("¿Estas seguro de realizar un registro?"):
                    registrar_nota()
                    continue

            elif opcion_nota == "2":
                if validar_continuidad("¿Estas seguro de realizar una cancelacion?"):
                    cancelar_nota()
                    continue

            elif opcion_nota == "3": 
                if validar_continuidad("¿Estas seguro de realizar una recuperacion?"):
                    recuperar_nota()
                    continue
            elif opcion_nota == "4":
                while True:
                    print("\nMenu consultas y reportes")
                    print("\n1. Consulta por periodo\n2. Consulta por folio\n3. Volver al menu Notas")
                    opcion_consultas = input("Ingresa una opcion: ")
                    if opcion_consultas == "1":
                        if validar_continuidad("¿Estas seguro de realizar una consulta por periodo?"):
                            consulta_por_periodo()
                            continue
                    elif opcion_consultas == "2":
                        if validar_continuidad("¿Estas seguro de realizar una consulta por folio?"):
                            consulta_por_folio()
                            continue
                    elif opcion_consultas == "3":
                        break
                    else:
                        print("Opcion no valida, ingrese nuevamente.")
            elif opcion_nota == "5":
                break
            else:
                print("Opcion no valida, ingrese nuevamente.")

    elif opcion == "2":
        while True:
            print("\n** Menu Clientes **")
            print("\n1. Agregar un cliente\n2. Suspender un cliente\n3. Recuperar un cliente \n4. Consultas y reportes\n5. Volver al menu principal")
            opcion_clientes = input("Ingrese una opcion: ")
            if opcion_clientes == "":
                print("\n* Opcion omitida, Ingrese una opcion *")
                continue

            if opcion_clientes == "1":
                if validar_continuidad("¿Estas seguro de realizar un registro?"):
                    agregar_cliente()
                    continue
            
            if opcion_clientes == "2":
                if validar_continuidad("¿Estas seguro de suspender un cliente?"):
                    suspender_cliente()
                    continue
            
            if opcion_clientes == "3":
                if validar_continuidad("¿Estas seguro de recuperar un cliente?"):
                    recuperar_cliente()
                    continue

            elif opcion_clientes == "4":
                while True:
                    print("\nMenu consultas y reportes")
                    print("\n1. Listado de clientes registrados\n2. Busqueda por clave\n3. Busqueda por nombre\n4. Volver al menu de clientes")
                    opcion_consultas = input("Ingresa una opcion: ")

                    if opcion_consultas == "1":
                        while True:
                            print("\n** Listado de clientes registrados **")
                            print("\n1. Ordenado por clave\n2. Ordenado por nombre\n3. Volver al menu anterior")
                            opcion_cliente_registrados = input("Ingresa una opcion: ")
                            if opcion_cliente_registrados == "1":
                                if validar_continuidad("¿Estas seguro de realizar un listado de clientes por clave?"):
                                    clientes_ordenados_por_claves()
                            elif opcion_cliente_registrados == "2":
                                if validar_continuidad("¿Estas seguro de realizar un listado de clientes por nombre?"):
                                    clientes_ordenados_por_nombres()
                            elif opcion_cliente_registrados == "3":
                                break
                            else:
                                print("\nOpcion no valida, ingrese nuevamente.")
                        continue

                    elif opcion_consultas == "2":
                        if validar_continuidad("¿Estas seguro de realizar una busqueda de cliente por clave?"):
                            cliente_busqueda_por_clave()
                    elif opcion_consultas == "3":
                        if validar_continuidad("¿Estas seguro de realizar una busqueda de cliente por clave?"):
                            cliente_busqueda_por_nombre()
                    elif opcion_consultas == "4":
                        break
                    else:
                        print("\nOpcion no valida, ingrese nuevamente.")
            elif opcion_clientes == "5":
                break
            else:
                print("\nOpcion no valida, ingrese nuevamente.")
            
    elif opcion == "3":
        while True:
            print("\n** Menu Servicios **")
            print("\n1. Agregar un servicio\n2. Suspender servicio\n3. Recuperar servicio\n4. Consultas y reportes\n5. Volver al menu principal")
            opcion_servicios = input("Ingresa una opcion: ")
            if opcion_servicios == "":
                print("\n* Opcion omitida, Ingrese una opcion *")
                continue

            if opcion_servicios == "1":
                if validar_continuidad("¿Estas seguro de realizar un registro?"):
                    agregar_servicio()
                    continue
                 
            if opcion_servicios == "2":
                if validar_continuidad("¿Estás seguro de suspender un servicio?"):
                   suspender_servicio()
                   continue

            if opcion_servicios == "3":
                if validar_continuidad("¿Estás seguro de recuperar un servicio?"):
                   recuperar_servicio()
                   continue

            elif opcion_servicios == "4":
                while True:
                    print("\nMenu consultas y reportes")
                    print("\n1. Busqueda por clave de servicio\n2. Busqueda por nombre de servicio\n3. Listado de servicios\n4. Volver al menu servicios")
                    opcion_consultas = input("Ingresa una opcion: ")

                    if opcion_consultas == "1":
                        busqueda_por_clave_servicio()

                    elif opcion_consultas == "2":
                        busqueda_por_nombre_servicio()

                    elif opcion_consultas == "3":
                        while True:
                            print("\nMenu listado de servicios")
                            print("\n1. Ordenado por clave\n2. Ordenado por nombre\n3. Volver al menu anterior")
                            opcion = input("Ingresa una opcion: ")
                            if opcion == "1":
                                servicios_por_clave()
                            elif opcion == "2":
                                servicios_por_nombre()
                            elif opcion == "3":
                                break
                            else:
                                print("Opcion no valida, ingrese nuevamente.")
                    elif opcion_consultas == "4":
                        break
            elif opcion_servicios == "5":
                break   
            else:
                print("\nOpcion no valida, ingrese nuevamente.")
    elif opcion == "4":
        while True:
            print("\n** Menu Estadisticos **")
            print("\n1. Servicios mas prestados\n2. Clientes con mas notas\n3. Promedio de montos de notas\n4. Volver al menu anterior")
            opcion_estadisticos = input("Ingresa una opcion: ")
            if opcion_estadisticos == "":
                print("\n* Opcion omitida, Ingrese una opcion *")
                continue
            elif opcion_estadisticos == "1":
                if validar_continuidad("¿Estas seguro de realizar un listado de servicios mas prestados?"):
                    servicios_mas_solicitados()
                    continue
            elif opcion_estadisticos == "2":
                if validar_continuidad("¿Estas seguro de realizar un listado de clientes con mas notas?"):
                    clientes_con_mas_notas()
                    continue
            elif opcion_estadisticos == "3":
                if validar_continuidad("¿Estas seguro de realizar un promedio de montos de notas?"):
                    promedio_montos_notas()
                    continue
            elif opcion_estadisticos == "4":
                break
            else:
                print("\nOpcion no valida, ingrese nuevamente.")

    elif opcion == "5":
        if validar_continuidad("¿Estas seguro de salir del programa?"):
            print("\nGracias por usar este programa. 😁")
            break
    else:
        print("\nOpcion no valida, ingrese nuevamente.")
