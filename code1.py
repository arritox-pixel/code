import argparse
import exrex
import hashlib


def numero_desde_texto(texto, minimo, maximo):
    texto_bytes = str(texto).encode("utf-8")
    resultado = hashlib.sha256(texto_bytes).hexdigest()

    parte = resultado[0:8]
    numero = int(parte, 16)

    rango = maximo - minimo + 1
    numero = numero % rango
    numero = numero + minimo
    return numero


def hash_hex(algoritmo, texto):
    texto_bytes = str(texto).encode("utf-8")

    if algoritmo == "SHA256":
        return hashlib.sha256(texto_bytes).hexdigest()

    if algoritmo == "SHA512":
        return hashlib.sha512(texto_bytes).hexdigest()

    return ""


def generar_password_clara():
    patron = r"[-\?\*][a-z]{2}[0-9]{2}-"
    password = exrex.getone(patron)
    return password


class Cliente:
    def __init__(self, cl_name, cl_cif, algoritmo):
        self.CL_ID = numero_desde_texto(cl_name + "@" + cl_cif, 5000, 6500)
        self.CL_NAME = cl_name
        self.CL_CIF = cl_cif
        self.CL_PASS = self.GenerarPass(algoritmo)

    def GenerarPass(self, algoritmo):
        password_clara = generar_password_clara()
        password_hash = hash_hex(algoritmo, password_clara)
        valor = algoritmo + "$$" + password_hash + "$$" + password_clara
        return valor

    def DescifrarPass(self):
        partes = self.CL_PASS.split("$$")
        if len(partes) >= 3:
            return partes[2]
        return ""

    def RealizarEnvio(self):
        url_cliente = self.DescifrarPass()
        enlace = "https://www.petrol.com/cliente/" + url_cliente
        print(enlace)

    def ImprimirDatos(self):
        print("CL_ID:", self.CL_ID)
        print("CL_NAME:", self.CL_NAME)
        print("CL_CIF:", self.CL_CIF)
        print("CL_PASS:", self.CL_PASS)


class Petrolera:
    def __init__(self, nom_petrolera, dir_petrolera, suministros):
        self.ID_PETROLERA = numero_desde_texto(nom_petrolera + "@" + dir_petrolera, 1, 50)
        self.NOM_PETROLERA = nom_petrolera
        self.DIR_PETROLERA = dir_petrolera
        self.SUMINISTROS = suministros
        self.CONTABILIDAD = {}

    def RealizarContabilidad(self, ruta_fichero):
        fichero = open(ruta_fichero, "r+", encoding="utf-8")
        lineas = fichero.readlines()
        fichero.close()

        clientes_por_cif = {}

        for linea in lineas:
            linea_limpia = linea.strip()

            if linea_limpia != "":
                partes = linea_limpia.split("--")

                if len(partes) == 6:
                    fecha = partes[0]
                    cl_cif = partes[1]
                    cl_name = partes[2]
                    id_pedido = partes[3]
                    id_petrolera = partes[4]
                    importe_texto = partes[5]

                    if str(id_petrolera) == str(self.ID_PETROLERA):
                        if cl_cif in clientes_por_cif:
                            cliente = clientes_por_cif[cl_cif]
                        else:
                            cliente = Cliente(cl_name, cl_cif, "SHA256")
                            clientes_por_cif[cl_cif] = cliente

                        importe = float(importe_texto)
                        self.CONTABILIDAD[id_pedido] = [importe, fecha, cliente]

    def ObtenerPedidosCliente(self, cl_id):
        encontrado = False

        for id_pedido in self.CONTABILIDAD:
            datos = self.CONTABILIDAD[id_pedido]
            importe = datos[0]
            fecha = datos[1]
            cliente = datos[2]

            if cliente.CL_ID == cl_id:
                encontrado = True
                print("ID_PEDIDO:", id_pedido, "IMPORTE:", importe, "FECHA:", fecha)

        if encontrado is False:
            print("No hay pedidos para ese CL_ID:", cl_id)

    def ReporteContabilidad(self, ruta_salida):
        importe_total = 0.0
        fecha_ultima = ""

        for id_pedido in self.CONTABILIDAD:
            datos = self.CONTABILIDAD[id_pedido]
            importe = datos[0]
            fecha = datos[1]

            importe_total = importe_total + importe

            if fecha_ultima == "":
                fecha_ultima = fecha
            else:
                if fecha > fecha_ultima:
                    fecha_ultima = fecha

        if fecha_ultima == "":
            fecha_ultima = "SIN_FECHA"

        texto = str(self.ID_PETROLERA) + "@@" + str(importe_total) + "@@" + fecha_ultima + "\n"

        fichero = open(ruta_salida, "w+", encoding="utf-8")
        fichero.write(texto)
        fichero.close()

    def ImprimirDatos(self):
        print("ID_PETROLERA:", self.ID_PETROLERA)
        print("NOM_PETROLERA:", self.NOM_PETROLERA)
        print("DIR_PETROLERA:", self.DIR_PETROLERA)
        print("SUMINISTROS:", self.SUMINISTROS)
        print("PEDIDOS_EN_CONTABILIDAD:", len(self.CONTABILIDAD))


def crear_fichero_demo(ruta_fichero, id_petrolera_1, id_petrolera_2):
    lineas = []

    lineas.append("2025-12-01--A11111111--Cliente Uno--P001--" + str(id_petrolera_1) + "--120.50\n")
    lineas.append("2025-12-02--B22222222--Cliente Dos--P002--" + str(id_petrolera_1) + "--80.00\n")
    lineas.append("2025-12-03--C33333333--Cliente Tres--P003--" + str(id_petrolera_1) + "--150.75\n")

    lineas.append("2025-12-01--D44444444--Cliente Cuatro--P004--" + str(id_petrolera_2) + "--60.00\n")
    lineas.append("2025-12-02--E55555555--Cliente Cinco--P005--" + str(id_petrolera_2) + "--99.99\n")
    lineas.append("2025-12-03--F66666666--Cliente Seis--P006--" + str(id_petrolera_2) + "--200.10\n")

    fichero = open(ruta_fichero, "w+", encoding="utf-8")
    for linea in lineas:
        fichero.write(linea)
    fichero.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fichero_contabilidad", type=str, default="contabilidad_demo.txt")
    args = parser.parse_args()

    petrolera_1 = Petrolera("Petrolera Norte", "Calle Norte 1", 100)
    petrolera_2 = Petrolera("Petrolera Sur", "Avenida Sur 9", 200)

    crear_fichero_demo(args.fichero_contabilidad, petrolera_1.ID_PETROLERA, petrolera_2.ID_PETROLERA)

    petrolera_1.RealizarContabilidad(args.fichero_contabilidad)
    petrolera_2.RealizarContabilidad(args.fichero_contabilidad)

    print("=== PETROLERA 1 ===")
    petrolera_1.ImprimirDatos()

    print("")
    print("=== PETROLERA 2 ===")
    petrolera_2.ImprimirDatos()

    print("")
    print("=== CLIENTES Y ENLACES (PETROLERA 1) ===")
    for id_pedido in petrolera_1.CONTABILIDAD:
        datos = petrolera_1.CONTABILIDAD[id_pedido]
        cliente = datos[2]
        cliente.ImprimirDatos()
        cliente.RealizarEnvio()
        print("")

    print("=== CLIENTES Y ENLACES (PETROLERA 2) ===")
    for id_pedido in petrolera_2.CONTABILIDAD:
        datos = petrolera_2.CONTABILIDAD[id_pedido]
        cliente = datos[2]
        cliente.ImprimirDatos()
        cliente.RealizarEnvio()
        print("")

    print("=== OBTENER PEDIDOS POR CLIENTE (EJEMPLO) ===")
    ejemplo_cliente = None
    for id_pedido in petrolera_1.CONTABILIDAD:
        datos = petrolera_1.CONTABILIDAD[id_pedido]
        ejemplo_cliente = datos[2]
        break

    if ejemplo_cliente is not None:
        petrolera_1.ObtenerPedidosCliente(ejemplo_cliente.CL_ID)

    petrolera_1.ReporteContabilidad("reporte_petrolera_1.txt")
    petrolera_2.ReporteContabilidad("reporte_petrolera_2.txt")

    print("")
    print("Se han generado los reportes: reporte_petrolera_1.txt y reporte_petrolera_2.txt")
