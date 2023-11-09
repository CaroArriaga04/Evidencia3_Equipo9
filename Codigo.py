import datetime
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
            return False
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
            mi_cursor.execute("SELECT claveCliente, nombre FROM Cliente")
            clientes= mi_cursor.fetchall()
            print("\n   Clientes registrados  ")
            informacion = [[clave, nombre] for clave, nombre in clientes]
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
                mi_cursor.execute("SELECT * FROM Cliente WHERE claveCliente = :claveCliente ", (valores))
                cliente = mi_cursor.fetchone()
                if cliente:
                    mi_cursor.execute('SELECT * FROM Servicio')
                    servicios = mi_cursor.fetchall()
                    print("\n       Servicios disponibles")
                    informacion = [[clave, nombre, costo] for clave, nombre, costo in servicios]
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
                        mi_cursor.execute('SELECT * FROM Servicio WHERE claveServicio = :claveServicio', valores)
                        servicio = mi_cursor.fetchone()
                        if servicio:
                            detalles.append(clave_serv) 
                            continuar = input("\n¿Desea agregar otro servicio? (si/no): ")
                            if continuar.lower() != "si":
                                break
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
        print(e)
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
            mi_cursor.execute('SELECT Nota.folio, Nota.fecha, Nota.claveCliente, Cliente.nombre, Cliente.rfc, Cliente.correo, \
                        Nota.monto, Servicio.nombre, Servicio.costo FROM Cliente \
                        INNER JOIN Nota ON Nota.claveCliente = Cliente.claveCliente \
                        INNER JOIN Detalle ON Nota.folio = Detalle.folio \
                        INNER JOIN Servicio ON Detalle.claveServicio = Servicio.claveServicio \
                        WHERE Nota.folio = :folio AND Nota.cancelada=0' ,(valor))

            nota= mi_cursor.fetchall()
            if nota:
                informacion = [[folio, fecha, claveCliente, nombre, rfc, correo, monto, nombre, costo] 
                                for folio, fecha, claveCliente,nombre, rfc, correo, monto, nombre, costo in nota]
                titulos= ["Folio", "Fecha", "Clave cliente", "Nombre Cliente", "RFC cliente", "Correo cliente",
                        "Monto", "Nombre del servicio", "Costo del servicio"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            else: 
                    print("\nOperacion cancelada")

    except Exception as e:
        print(e)

def recuperar_nota():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute('SELECT folio, fecha, claveCliente, monto FROM Nota WHERE cancelada = 1')
            notas_canceladas = mi_cursor.fetchall()
            if notas_canceladas:
                informacion = [[folio, fecha, claveCliente, monto] for folio, fecha, claveCliente, monto in notas_canceladas]
                titulos= ["Folio", "Fecha", "Clave cliente", "Monto"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))

                while True:
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
            else:
                print("\nNo hay notas canceladas")
    except Exception as e:
        print(e)
                            
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
            mi_cursor.execute("SELECT Nota.folio, Nota.fecha, Cliente.claveCliente, Cliente.nombre, Cliente.rfc, Cliente.correo,\
                                Nota.monto \
                                FROM Nota \
                                INNER JOIN Cliente ON Nota.claveCliente = Cliente.claveCliente \
                                WHERE fecha BETWEEN ? AND ? AND cancelada=0", (fecha_inicial, fecha_final))
            notas = mi_cursor.fetchall()

        if notas:
            total_montos = sum(nota[6] for nota in notas)
            promedio_montos = total_montos / len(notas)

            print(f"\n                                         Notas del periodo especificado")
            informacion = [[folio, fecha, claveCliente, nombre, rfc, correo, monto] for folio, fecha, claveCliente, nombre, rfc, correo, monto in notas]
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

    except sqlite3.Error as e:
        print(f"Se produjo un error con SQLite: {e}")
    except Exception as e:
        print(f"Se produjo el siguiente error: {e}")

def consulta_por_folio():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute('SELECT Nota.folio, Nota.fecha, Cliente.nombre FROM Nota \
                  INNER JOIN Cliente ON Nota.claveCliente = Cliente.claveCliente \
                  WHERE cancelada = 0 \
                  ORDER BY Nota.folio')
            
            notas_canceladas = mi_cursor.fetchall()
            if notas_canceladas:
                informacion = [[folio, fecha, nombre] for folio, fecha, nombre in notas_canceladas]
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
                    mi_cursor.execute('SELECT Nota.folio, Nota.fecha, Nota.claveCliente, Cliente.nombre, Cliente.rfc, Cliente.correo, \
                        Nota.monto, Servicio.nombre, Servicio.costo FROM Cliente \
                        INNER JOIN Nota ON Nota.claveCliente = Cliente.claveCliente \
                        INNER JOIN Detalle ON Nota.folio = Detalle.folio \
                        INNER JOIN Servicio ON Detalle.claveServicio = Servicio.claveServicio \
                        WHERE Nota.folio = :folio AND Nota.cancelada=0' ,(valor))

                    nota= mi_cursor.fetchall()
                    if nota:
                        informacion = [[folio, fecha, claveCliente, nombre, rfc, correo, monto, nombre, costo] 
                                       for folio, fecha, claveCliente,nombre, rfc, correo, monto, nombre, costo in nota]
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
            mi_cursor.execute("INSERT INTO Cliente (nombre, rfc, correo) VALUES (?,?,?)", valores)
            print(f"\nLa clave asignada fue {mi_cursor.lastrowid}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    finally:
        conn.close()

def clientes_ordenados_por_claves():
    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT * FROM Cliente ORDER BY claveCliente")
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[clave, nombre, rfc, correo] for clave, nombre, rfc, correo in registro]
                titulos = ["Clave", "Nombre", "RFC", "Correo"]
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
            mi_cursor.execute("SELECT * FROM Cliente ORDER BY nombre")
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[clave, nombre, rfc, correo] for clave, nombre, rfc, correo in registro]
                titulos = ["Clave", "Nombre", "RFC", "Correo"]
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
            mi_cursor.execute("SELECT * FROM Cliente WHERE claveCliente = :claveCliente", valores)
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[clave, nombre, rfc, correo] for clave, nombre, rfc, correo in registro]
                titulos = ["Clave", "Nombre", "RFC", "Correo"]
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
            valores = {"nombre":valor_nombre}
            mi_cursor.execute("SELECT * FROM Cliente WHERE nombre = :nombre", valores)
            registro = mi_cursor.fetchall()

            if registro:
                informacion = [[clave, nombre, rfc, correo] for clave, nombre, rfc, correo in registro]
                titulos = ["Clave", "Nombre", "RFC", "Correo"]
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
    finally:
        conn.close()

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
            mi_cursor.execute("SELECT * FROM Servicio WHERE claveServicio = :claveServicio", valores)
            registro = mi_cursor.fetchall()

            if registro:
                datos = [[clave, nombre, costo] for clave, nombre, costo in registro]
                Columnas = ["Clave", "Nombre", "Costo"]
                print(tabulate(datos, Columnas, tablefmt="fancy_grid"))
            else:
                print(f"\nNo se encontró un cliente asociado con el nombre ingresado {v_clave}")
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
            mi_cursor.execute("SELECT * FROM Servicio WHERE nombre = :nombre", valores)
            registro = mi_cursor.fetchall()

            if registro:
                datos = [[clave, nombre, costo] for clave, nombre, costo in registro]
                Columnas = ["Clave", "Nombre", "Costo"]
                print(tabulate(datos, Columnas, tablefmt="fancy_grid"))
            else:
                print(f"\nNo se encontró un servicio asociado con el nombre ingresado {v_nombre}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def servicios_por_clave():
   try:
    with sqlite3.connect("TallerMecanico.db") as conn:
      mi_cursor = conn.cursor()
      mi_cursor.execute("SELECT * FROM Servicio ORDER BY claveServicio")
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
   finally:
    conn.close()
def servicios_por_nombre():
 try:
      with sqlite3.connect("TallerMecanico.db") as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("SELECT * FROM Servicio ORDER BY nombre")
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



print("** BIENVENIDO AL SERVICIO DE AUTOMOVILES **")
while True:
    print("\n** MENU PRINCIPAL **")
    print("\n1. Menu Notas\n2. Menu Clientes\n3. Menu Servicios\n4. Salir")
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
            print("\n1. Agregar un cliente\n2. Consultas y reportes\n3. Volver al menu principal")
            opcion_clientes = input("Ingrese una opcion: ")
            if opcion_clientes == "":
                print("\n* Opcion omitida, Ingrese una opcion *")
                continue

            if opcion_clientes == "1":
                if validar_continuidad("¿Estas seguro de realizar un registro?"):
                    agregar_cliente()
                    continue

            elif opcion_clientes == "2":
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
            elif opcion_clientes == "3":
                break
            else:
                print("\nOpcion no valida, ingrese nuevamente.")
            
    elif opcion == "3":
        while True:
            print("\n** Menu Servicios **")
            print("\n1. Agregar un servicio\n2. Consultas y reportes\n3. Volver al menu principal")
            opcion_servicios = input("Ingresa una opcion: ")
            if opcion_servicios == "":
                print("\n* Opcion omitida, Ingrese una opcion *")
                continue

            if opcion_servicios == "1":
                if validar_continuidad("¿Estas seguro de realizar un registro?"):
                    agregar_servicio()
                    continue

            elif opcion_servicios == "2":
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
            elif opcion_servicios == "3":
                break   
            else:
                print("\nOpcion no valida, ingrese nuevamente.")
    elif opcion == "4":
        print("\nGracias por usar este programa. 😁")
        break
    else:
        print("\nOpcion no valida, ingrese nuevamente.")
