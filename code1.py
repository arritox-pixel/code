import argparse
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

    return None


def numero_dos_digitos(numero):
    if numero < 10:
        return "0" + str(numero)
    return str(numero)


def letras_minusculas():
    letras = []
    letra = ord("a")
    while letra <= ord("z"):
        letras.append(chr(letra))
        letra = letra + 1
    return letras


class Cliente:
    def __init__(self, cl_name, cl_cif, algoritmo):
        self.CL_NAME = str(cl_name)
        self.CL_CIF = str(cl_cif)
        self.algoritmo = str(algoritmo)

        texto_id = self.CL_CIF + "--" + self.CL_NAME
        self.CL_ID = numero_desde_texto(texto_id, 5000, 6500)

        self.CL_PASS = self.GenerarPass(self.algoritmo)

    def GenerarPass(self, algoritmo):
        texto_base = self.CL_CIF + "--" + self.CL_NAME + "--" + str(self.CL_ID)
        valor = numero_desde_texto(texto_base, 0, 999999)

        simbolos = ["-", "?", "*"]
        posicion_simbolo = valor % 3
        simbolo = simbolos[posicion_simbolo]

        letras = letras_minusculas()

        posicion_1 = valor % 26
        posicion_2 = (valor // 26) % 26

        letra_1 = letras[posicion_1]
        letra_2 = letras[posicion_2]

        numero = valor % 100
        numero_texto = numero_dos_digitos(numero)

        password_clara = simbolo + letra_1 + letra_2 + numero_texto + "-"

        password_hash = hash_hex(algoritmo, password_clara)
        return password_hash

    def DescifrarPass(self):
        simbolos = ["-", "?", "*"]
        letras = letras_minusculas()

        simbolo_pos = 0
        while simbolo_pos < len(simbolos):
            simbolo = simbolos[simbolo_pos]

            i = 0
            while i < len(letras):
                j = 0
                while j < len(letras):
                    letra_1 = letras[i]
                    letra_2 = letras[j]

                    numero = 0
                    while numero <= 99:
                        numero_texto = numero_dos_digitos(numero)
                        password_clara = simbolo + letra_1 + letra_2 + numero_texto + "-"

                        calculado = hash_hex(self.algoritmo, password_clara)
                        if calculado == self.CL_PASS:
                            return password_clara

                        numero = numero + 1

                    j = j + 1
                i = i + 1

            simbolo_pos = simbolo_pos + 1

        return None

    def RealizarEnvio(self):
        url_cliente = self.DescifrarPass()
        if url_cliente is None:
            print("No se pudo descifrar la password del cliente")
            return

        enlace = "https://www.petrol.com/cliente/" + url_cliente
        print(enlace)

    def ImprimirDatos(self):
        print("CLIENTE")
        print("CL_ID:", self.CL_ID)
        print("CL_NAME:", self.CL_NAME)
        print("CL_CIF:", self.CL_CIF)
        print("CL_PASS:", self.CL_PASS)
        print("ALGORITMO:", self.algoritmo)


class Petrolera:
    def __init__(self, nom_petrolera, dir_petrolera, suministros):
        self.NOM_PETROLERA = str(nom_petrolera)
        self.DIR_PETROLERA = str(dir_petrolera)
        self.SUMINISTROS = int(suministros)

        texto_id = self.NOM_PETROLERA + "--" + self.DIR_PETROLERA
        self.ID_PETROLERA = numero_desde_texto(texto_id, 1, 50)

        self.CONTABILIDAD = {}
        self.fecha_ultima = None

    def RealizarContabilidad(self, ruta_fichero):
        fichero = open(ruta_fichero, "r", encoding="utf-8")
        lineas = fichero.readlines()
        fichero.close()

        for linea in lineas:
            linea_limpia = linea.strip()
            if linea_limpia == "":
                continue

            partes = linea_limpia.split("--")
            if len(partes) != 6:
                continue

            fecha = partes[0].strip()
            cl_cif = partes[1].strip()
            cl_name = partes[2].strip()
            id_pedido = partes[3].strip()
            id_petrolera = partes[4].strip()
            importe_texto = partes[5].strip()

            if id_petrolera != str(self.ID_PETROLERA):
                continue

            algoritmo = "SHA256"
            if self.ID_PETROLERA % 2 != 0:
                algoritmo = "SHA512"

            cliente = Cliente(cl_name, cl_cif, algoritmo)

            importe = float(importe_texto)

            self.CONTABILIDAD[id_pedido] = [importe, fecha, cliente]
            self.fecha_ultima = fecha

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
            print("No hay pedidos para el cliente con CL_ID:", cl_id)

    def ReporteContabilidad(self):
        total = 0.0

        for id_pedido in self.CONTABILIDAD:
            datos = self.CONTABILIDAD[id_pedido]
            importe = datos[0]
            total = total + importe

        fecha = self.fecha_ultima
        if fecha is None:
            fecha = "SIN_FECHA"

        nombre_salida = "reporte_petrolera_" + str(self.ID_PETROLERA) + ".txt"
        salida = open(nombre_salida, "w+", encoding="utf-8")

        linea = str(self.ID_PETROLERA) + "@@" + str(total) + "@@" + str(fecha)
        salida.write(linea)
        salida.close()

        return nombre_salida

    def ImprimirDatos(self):
        print("PETROLERA")
        print("ID_PETROLERA:", self.ID_PETROLERA)
        print("NOM_PETROLERA:", self.NOM_PETROLERA)
        print("DIR_PETROLERA:", self.DIR_PETROLERA)
        print("SUMINISTROS:", self.SUMINISTROS)
        print("PEDIDOS EN CONTABILIDAD:", len(self.CONTABILIDAD))


def escribir_fichero_prueba(ruta, petrolera_1, petrolera_2):
    lineas = []

    lineas.append("2025-04-10--A11111111--Ana--P1001--" + str(petrolera_1.ID_PETROLERA) + "--1200.50")
    lineas.append("2025-04-11--B22222222--Luis--P1002--" + str(petrolera_1.ID_PETROLERA) + "--300.00")
    lineas.append("2025-04-12--C33333333--Marta--P1003--" + str(petrolera_1.ID_PETROLERA) + "--75.25")

    lineas.append("2025-05-01--D44444444--Pablo--P2001--" + str(petrolera_2.ID_PETROLERA) + "--500.00")
    lineas.append("2025-05-02--E55555555--Sara--P2002--" + str(petrolera_2.ID_PETROLERA) + "--999.99")
    lineas.append("2025-05-03--F66666666--Nerea--P2003--" + str(petrolera_2.ID_PETROLERA) + "--10.00")

    fichero = open(ruta, "w+", encoding="utf-8")
    for linea in lineas:
        fichero.write(linea + "\n")
    fichero.close()


def obtener_un_cliente_de_petrolera(petrolera):
    for id_pedido in petrolera.CONTABILIDAD:
        datos = petrolera.CONTABILIDAD[id_pedido]
        cliente = datos[2]
        return cliente
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fichero", required=True)
    args = parser.parse_args()

    petrolera_1 = Petrolera("Petrol Norte", "Calle 1", 100)
    petrolera_2 = Petrolera("Petrol Sur", "Calle 2", 200)

    escribir_fichero_prueba(args.fichero, petrolera_1, petrolera_2)

    petrolera_1.RealizarContabilidad(args.fichero)
    petrolera_2.RealizarContabilidad(args.fichero)

    petrolera_1.ImprimirDatos()
    petrolera_2.ImprimirDatos()

    cliente_1 = obtener_un_cliente_de_petrolera(petrolera_1)
    if cliente_1 is not None:
        cliente_1.ImprimirDatos()
        cliente_1.RealizarEnvio()
        petrolera_1.ObtenerPedidosCliente(cliente_1.CL_ID)

    cliente_2 = obtener_un_cliente_de_petrolera(petrolera_2)
    if cliente_2 is not None:
        cliente_2.ImprimirDatos()
        cliente_2.RealizarEnvio()
        petrolera_2.ObtenerPedidosCliente(cliente_2.CL_ID)

    salida_1 = petrolera_1.ReporteContabilidad()
    salida_2 = petrolera_2.ReporteContabilidad()

    print("Reporte creado:", salida_1)
    print("Reporte creado:", salida_2)


if __name__ == "__main__":
    main()
