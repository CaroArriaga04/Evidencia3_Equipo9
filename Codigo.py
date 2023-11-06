import datetime
import re
from tabulate import tabulate
import pandas as pd
import csv
import os
import sys
import sqlite3
from sqlite3 import Error

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
    confirmar= input("¿Desea agregar una nota? (si/no)?")
    if confirmar.lower() !="si":
        print("\n Operacion cancelada")
        return
        
    try:
        fecha= datetime.datetime.now().strftime('%d-%m-%Y')
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute('SELECT claveCliente, nombre FROM Cliente')
            clientes= mi_cursor.fetchall()
            print("Clientes registrados: ")
            for cliente in clientes:
                print(f"Clave: {cliente[0]}, Nombre: {cliente[1]}")
    except Error as e:
        print(e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

            clave_c= int(input("Ingrese el ID del cliente: "))
            if clave_c == " ":
                print("El ID no se puede quedar vacío, vuelva a intentar")
                continue
            if not clave_c.isdigit():
                print("ID INCORRECTO, INTENTE DE NUEVO")
                continue

    
            mi_cursor.execute('SELECT * FROM Cliente WHERE claveCliente = ? ', (claveCliente,))
            cliente = mi_cursor.fetchone()
            if cliente:
                mi_cursor.execute('SELECT claveServicio, nombre, costo FROM Servicio')
                servicios = mi_cursor.fetchall()
                print("Servicios disponibles: ")
                for servicio in servicios:
                    print(f"{Servicio[0]}. Nombre: {servicio[1]}, Costo: {servicio[2]}")

                detalles = []
                while True: 
                    clave_serv = int(input("Ingrese la clave del servicio: "))
                    if clave_serv == " ":
                        print("La clave no se puede quedar vacía, vuelva a intentar")
                        continue
                    if not clave_serv.isdigit():
                        print("CLAVE INCORRECTA, INTENTE DE NUEVO")
                        continue

                    mi_cursor.execute('SELECT * FROM Servicio WHERE claveServicio= ?', (clave_serv,))
                    servicio= mi_cursor.fetchone()
                    if servicio:
                        cantidad= int(input("Ingrese la cantidad a requerir de este servicio: "))
                        detalles.append((clave_serv, cantidad))
                    else:
                        print("El servicio no es válido")
                    confirmar2= input("¿Desea agregar otro servicio? (si/no): ")
                    if confirmar2.lower() != 'si':
                        break

                monto_total= sum(servicio[2] * cantidad for servicio, cantidad in zip(servicios, detalles))

                mi_cursor.execute('INSERT INTO Nota (fecha, claveCliente, monto) VALUES (?, ?, ?)', (fecha, clave_c, monto_total))
                print("\n La clave asignada fue {mi_cursor.lastrowid}")

                mi_cursor.execute('INSERT INTO Detalle (folio, claveServicio, cantidad) VALUES (?, ?, ?)', [(mi_cursor.lastrowid, clave_serv, cantidad) for clave_serv, cantidad in detalles])
        
                print("La nota fue agregada correctamente")
    except Exception as e:
        print(e)

def cancelar_nota():
    try:
        can_folio = input("Ingrese el folio de la nota a cancelar: ")
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor= conn.cursor()
            mi_cursor.execute('SELECT * FROM Nota WHERE folio = ?', (can_folio,))
            nota= mi_cursor.fetchone()
            if nota:
               nota= (folio, fecha, claveCliente, monto, cancelada)
                print(f"Folio: {folio} ")
                print(f"Fecha: {fecha}")
                print(f"Clave cliente: {claveCliente}")
                print(f"Monto: {monto}")
                confirmar= input("¿EStá seguro de que desea cancelar esta nota? (si/no): ")
                if confirmar.lower() == "si":
                    mi_cursor.execute('UPDATE Nota SET cancelada= 1 WHERE folio = ?', (folio,))
                    print("La nota fue cancelada con éxito")
                else: 
                    print("Operacion cancelada")
            else: 
                print("Nota no encontrada o ya está cancelada")
    except Exception as e:
        print(e)

def recuperar_nota():
    pass

def consulta_por_periodo():
    pass

def consulta_por_folio():
    pass

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
      print ('______________')
      print ("SERVICIOS DISPONIBLES")
      print ("1. afinacion")
      print ("2. refaccion de balatas")
      print ("3. cambio de llantas")
      print ("4. cambio de aceite")
      print ("5. cambio de suspension")
      print ("6. nueva pintura")

      nombre = input("\nNombre del servicio: ")
      if nombre == "":
        print ("\n* NO SE PUEDE OMITIR ESTE DATO *")
        continue
      elif not (bool(re.search('^[a-zA-Z ]+$', nombre))):
        print ("\n* NOMBRE NO VALIDO, INGRESE NUEVAMENTE *")
        continue
      else:
        break


    while True:
        costo = input("\nIngrese el costo del servicio seleccionado: ")
        if costo == "":
            print("\n* NO PUEDE ESTAR VACÍO ESTE DATO*")
            continue
        elif not (bool(re.match(costo, 'r^[0-9]+\.[0-9]$'))):
            print("\n*EL PRECIO NO CUMPLE EL FORMATO VALIDO (XX.XX). INTENTAR DE NUEVO *")
            continue
        elif costo<=0.00:
            print ("\n*EL COSTO NO PUEDE SER MENOR A 0 PESOS.*")
            continue
        else:
            break

    try:
        with sqlite3.connect("TallerMecanico.db") as conn:
            mi_cursor = conn.cursor()
            valores = (nombre, costo)
            mi_cursor.execute("INSERT INTO Servicio (nombre, costo) VALUES (?,?,?)", valores)
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
                print(f"\nNo se encontró un cliente asociado con el nombre ingresado {v_nombre}")
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
          archivo_excel = f"ReporteServiciosActivosPorClave_{fecha_actual}.xlsx"
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
            archivo_csv = f"ReporteServiciosActivosPorNombre_{fecha_actual}.csv"
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
        print("\n** Menu Notas **")
        print("1. Registrar una nota\n2. Cancelar una nota\n3. Recuperar una nota\n4. Consultas y reportes\n5. Volver al menu principal")
        opcion_nota = input("Ingrese una opcion: ")
        if opcion_nota == "1":
            registrar_nota()
        elif opcion_nota == "2":
            cancelar_nota()
        elif opcion_nota == "3": 
            recuperar_nota()
        elif opcion_nota == "4":
            print("\nMenu consultas y reportes")
            print("\n1. Consulta por periodo\n2. Consulta por folio\n3. Volver al menu Notas")
            opcion_consultas = input("Ingresa una opcion: ")
            if opcion_consultas == "1":
                consulta_por_periodo()
            elif opcion_consultas == "2":
                consulta_por_folio()
            elif opcion_consultas == "3":
                break
            else:
                print("Opcion no valida, ingrese nuevamente.")
        elif opcion_nota == "5":
            continue
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
        print("\n** Menu Servicios **")
        print("\n1. Agregar un servicio\n2. Consultas y reportes\n3. Volver al menu principal")
        opcion_servicios = input("Ingresa una opcion: ")
        if opcion_servicios == "1":
            agregar_servicio()
        elif opcion_servicios == "2":
            print("\nMenu consultas y reportes")
            print("\n1. Busqueda por clave de servicio\n2. Busqueda por nombre de servicio\n3. Listado de servicios\n4. Volver al menu principal")
            opcion_consultas = input("Ingresa una opcion: ")
            if opcion_consultas == "1":
                busqueda_por_clave_servicio()
            elif opcion_consultas == "2":
                busqueda_por_nombre_servicio()
            elif opcion_consultas == "3":
                print("\nMenu listado de servicios")
                print("\n1. Ordenado por clave\n2. Ordenado por nombre\n3. Volver al menu principal")
                opcion = input("Ingresa una opcion: ")
                if opcion == "1":
                    servicios_por_clave()
                elif opcion == "2":
                    servicios_por_nombre()
                elif opcion == "3":
                    continue
                else:
                    print("Opcion no valida, ingrese nuevamente.")
    elif opcion == "4":
        print("\nGracias por usar este programa. 😁")
        break
    else:
        print("\nOpcion no valida, ingrese nuevamente.")
