import sys
import sqlite3
from sqlite3 import Error

try:
    with sqlite3.connect("TallerMecanico.db") as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS Cliente\
                          (claveCliente INTEGER PRIMARY KEY, nombreCliente TEXT NOT NULL, rfc TEXT NOT NULL, correo TEXT NOT NULL, \
                          canceladaCliente INTEGER DEFAULT 0);")
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS Nota\
                          (folio INTEGER PRIMARY KEY, fecha timestamp NOT NULL, monto REAL,cancelada INTEGER DEFAULT 0, claveCliente INTEGER NOT NULL,\
                           FOREIGN KEY(claveCliente) REFERENCES Cliente(claveCliente));")
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS Servicio\
                          (claveServicio INTEGER PRIMARY KEY, nombre TEXT NOT NULL, costo REAL, canceladaServicio INTEGER DEFAULT 0);")
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS Detalle\
                          (claveServicio INTEGER, folio INTEGER,\
                          FOREIGN KEY(claveServicio) REFERENCES Servicio(claveServicio),\
                          FOREIGN KEY(folio) REFERENCES Nota(folio));")
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS ServiciosSolicitados\
                          (PuestoServicio INTEGER PRIMARY KEY, claveServicio INTEGER, nombre, NumSolicitudes INTEGER,\
                          FOREIGN KEY (claveServicio) REFERENCES Servicio (claveServicio));")
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS NotasPorCliente\
                          (PuestoCliente INTEGER PRIMARY KEY, claveCliente INTEGER, NumNotas INTEGER,\
                          FOREIGN KEY (claveCliente) REFERENCES Cliente (claveCliente));")
except Error as e:
    print (e)
except Exception:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
finally:
    conn.close()
