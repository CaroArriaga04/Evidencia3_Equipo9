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
    pass

def cancelar_nota():
    pass

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
            print(f"La clave asignada fue {mi_cursor.lastrowid}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    finally:
        conn.close()

def cliente_por_clave():
    pass

def cliente_por_nombre():
    pass

def cliente_busqueda_por_clave():
    pass

def cliente_busqueda_por_nombre():
    pass

def agregar_servicio():
    pass

def busqueda_por_clave_servicio():
    pass

def busqueda_por_nombre_servicio():
    pass

def servicios_por_clave():
    pass

def servicios_por_nombre():
    pass


print("** BIENVENIDO AL SERVICIO DE AUTOMOVILES **")
while True:
    print("\nMENU PRINCIPAL")
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

    if opcion == "2":
        while True:
            print("\n** Menu Clientes **")
            print("\n1. Agregar un cliente\n2. Consultas y reportes\n3. Volver al menu principal")
            opcion_clientes = input("Ingrese una opcion: ")
            if opcion_clientes == "":
                print("\n* OPCION OMITIDA, INGRESE UNA OPCION *")
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
                            print("\nListado de clientes registrados")
                            print("\n1. Ordenado por clave\n2. Ordenado por nombre\n3. Volver al menu anterior")
                            opcion_cliente_registrados = input("Ingresa una opcion: ")
                            if opcion_cliente_registrados == "1":
                                if validar_continuidad("¿Estas seguro de realizar un listado de clientes por clave?"):
                                    cliente_por_clave()
                            elif opcion_cliente_registrados == "2":
                                if validar_continuidad("¿Estas seguro de realizar un listado de clientes por nombre?"):
                                    cliente_por_nombre()
                            elif opcion_cliente_registrados == "3":
                                break
                            else:
                                print("Opcion no valida, ingrese nuevamente.")
                        continue

                    elif opcion_consultas == "2":
                        cliente_busqueda_por_clave()
                    elif opcion_consultas == "3":
                        cliente_busqueda_por_nombre()
                    elif opcion_consultas == "4":
                        break
                    else:
                        print("\nOpcion no valida, ingrese nuevamente.")
            elif opcion_clientes == "3":
                break
            else:
                    print("\nOpcion no valida, ingrese nuevamente.")
            
    if opcion == "3":
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