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
    pass

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
    print("MENU PRINCIPAL")
    print("1. Menu Notas\n2. Menu Clientes\n3. Menu Servicios\n4. Salir")
    opcion = int(input("Ingresa una opcion: "))
    if opcion == 1:
        print("Menu Notas")
        print("1. Registrar una nota\n2. Cancelar una nota\n3. Recuperar una nota\n4. Consultas y reportes\n5. Volver al menu principal")
        opcion_nota = int(input("Ingrese una opcion: "))
        if opcion_nota == 1:
            registrar_nota()
        elif opcion_nota == 2:
            cancelar_nota()
        elif opcion_nota == 3: 
            recuperar_nota()
        elif opcion_nota == 4:
            print("Menu consultas y reportes")
            print("1. Consulta por periodo\n2. Consulta por folio\n3. Volver al menu Notas")
            opcion_consultas = int(input("Ingresa una opcion: "))
            if opcion_consultas == 1:
                consulta_por_periodo()
            elif opcion_consultas == 2:
                consulta_por_folio()
            elif opcion_consultas == 3:
                break
            else:
                print("Opcion no valida, ingrese nuevamente.")
        elif opcion_nota == 5:
            continue
        else:
            print("Opcion no valida, ingrese nuevamente.")
    if opcion == 2:
        print("Menu Clientes")
        print("1. Agregar un cliente\n2. Consultas y reportes\n3. Volver al menu principal")
        opcion_clientes = int(input("Ingrese una opcion: "))
        if opcion_clientes == 1:
            agregar_cliente()
        elif opcion_clientes == 2:
            print("Menu consultas y reportes")
            print("1. Listado de clientes registrados\n2. Busqueda por clave\n3. Busqueda por nombre\n4. Volver al menu de clientes")
            opcion_consultas = int(input("Ingresa una opcion: "))
            if opcion_consultas == 1:
                print("Listado de clientes registrados")
                print("1. Ordenado por clave\n2. Ordenado por nombre\n3. Volver al menu anterior")
                opcion_cliente_registrados = int(input("Ingresa una opcion: "))
                if opcion_cliente_registrados == 1:
                    cliente_por_clave()
                elif opcion_cliente_registrados == 2:
                    cliente_por_nombre()
                elif opcion_cliente_registrados == 3:
                    break
                else:
                    print("Opcion no valida, ingrese nuevamente.")
            elif opcion_consultas == 2:
                cliente_busqueda_por_clave()
            elif opcion_consultas == 3:
                cliente_busqueda_por_nombre()
            elif opcion_consultas == 4:
                continue
            else:
                print("Opcion no valida, ingrese nuevamente.")
    if opcion == 3:
        print("Menu Servicios")
        print("1. Agregar un servicio\n2. Consultas y reportes\n3. Volver al menu principal")
        opcion_servicios = int(input("Ingresa una opcion: "))
        if opcion_servicios == 1:
            agregar_servicio()
        elif opcion_servicios == 2:
            print("Menu consultas y reportes")
            print("1. Busqueda por clave de servicio\n2. Busqueda por nombre de servicio\n3. Listado de servicios\n4. Volver al menu principal")
            opcion_consultas = int(input("Ingresa una opcion: "))
            if opcion_consultas == 1:
                busqueda_por_clave_servicio()
            elif opcion_consultas == 2:
                busqueda_por_nombre_servicio()
            elif opcion_consultas == 3:
                print("Menu listado de servicios")
                print("1. Ordenado por clave\n2. Ordenado por nombre\n3. Volver al menu principal")
                opcion = int(input("Ingresa una opcion: "))
                if opcion == 1:
                    servicios_por_clave()
                elif opcion == 2:
                    servicios_por_nombre()
                elif opcion == 3:
                    continue
                else:
                    print("Opcion no valida, ingrese nuevamente.")
    elif opcion == 4:
        print("Gracias por usar este programa")
        break
    else:
        print("Opcion no valida, ingrese nuevamente.")