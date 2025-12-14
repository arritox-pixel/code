import argparse
from cryptography.hazmat.primitives import hashes


def int_a_texto(numero):
    n = int(numero)

    if n == 0:
        return "0"

    if n < 0:
        n = -n
        signo = "-"
    else:
        signo = ""

    digitos = []
    while n > 0:
        resto = n % 10
        digitos.append(chr(ord("0") + resto))
        n = n // 10

    texto = ""
    pos = len(digitos) - 1
    while pos >= 0:
        texto = texto + digitos[pos]
        pos = pos - 1

    return signo + texto


def calcular_hex(algoritmo, texto):
    if algoritmo == "SHA256":
        h = hashes.Hash(hashes.SHA256())
    else:
        if algoritmo == "SHA512":
            h = hashes.Hash(hashes.SHA512())
        else:
            if algoritmo == "MD5":
                h = hashes.Hash(hashes.MD5())
            else:
                return None

    h.update(texto.encode("utf-8"))
    return h.finalize().hex()


def numero_por_texto(texto, minimo, maximo):
    completo = calcular_hex("SHA256", texto)
    parte = completo[0:8]
    numero = int(parte, 16)

    rango = maximo - minimo + 1
    numero = numero % rango
    numero = numero + minimo
    return numero


def dos_digitos(numero):
    n = int(numero)
    if n < 10:
        return "0" + int_a_texto(n)
    return int_a_texto(n)


def lista_letras_minusculas():
    letras = []
    codigo = ord("a")
    while codigo <= ord("z"):
        letras.append(chr(codigo))
        codigo = codigo + 1
    return letras


class Cliente:
    def __init__(self, nombre_cliente, cif_cliente, algoritmo):
        self.CL_NAME = nombre_cliente
        self.CL_CIF = cif_cliente
        self.algoritmo = algoritmo

        texto_para_id = self.CL_CIF + "--" + self.CL_NAME
        self.CL_ID = numero_por_texto(texto_para_id, 5000, 6500)

        self.CL_PASS = self.GenerarPass(self.algoritmo)

    def GenerarPass(self, algoritmo):
        texto_base = self.CL_CIF + "--" + self.CL_NAME + "--" + int_a_texto(self.CL_ID)
        semilla = numero_por_texto(texto_base, 0, 999999)

        simbolos = ["-", "?", "*"]
        pos_simbolo = semilla % 3
        simbolo = simbolos[pos_simbolo]

        letras = lista_letras_minusculas()

        pos_1 = semilla % 26
        pos_2 = (semilla // 26) % 26

        letra_1 = letras[pos_1]
        letra_2 = letras[pos_2]

        num = semilla % 100
        num_texto = dos_digitos(num)

        clave_clara = simbolo + letra_1 + letra_2 + num_texto + "-"

        clave_hash = calcular_hex(algoritmo, clave_clara)
        if clave_hash is None:
            raise ValueError("Algoritmo no soportado")

        return clave_hash

    def DescifrarPass(self):
        simbolos = ["-", "?", "*"]
        letras = lista_letras_minusculas()

        pos_simbolo = 0
        while pos_simbolo < len(simbolos):
            simbolo = simbolos[pos_simbolo]

            i = 0
            while i < len(letras):
                j = 0
                while j < len(letras):
                    letra_1 = letras[i]
                    letra_2 = letras[j]

                    numero = 0
                    while numero <= 99:
                        num_texto = dos_digitos(numero)
                        candidata = simbolo + letra_1 + letra_2 + num_texto + "-"

                        calculada = calcular_hex(self.algoritmo, candidata)
                        if calculada == self.CL_PASS:
                            return candidata

                        numero = numero + 1

                    j = j + 1
                i = i + 1

            pos_simbolo = pos_simbolo + 1

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
    def __init__(self, nombre_petrolera, direccion_petrolera, suministros):
        self.NOM_PETROLERA = nombre_petrolera
        self.DIR_PETROLERA = direccion_petrolera
        self.SUMINISTROS = int(suministros)

        texto_id = self.NOM_PETROLERA + "--" + self.DIR_PETROLERA
        self.ID_PETROLERA = numero_por_texto(texto_id, 1, 50)

        self.CONTABILIDAD = {}
        self.fecha_ultima = None

    def RealizarContabilidad(self, ruta_fichero):
        archivo = open(ruta_fichero, "r", encoding="utf-8")
        lineas = archivo.readlines()
        archivo.close()

        for linea in lineas:
            linea_limpia = linea.strip()
            if linea_limpia == "":
                continue

            partes = linea_limpia.split("--")
            if len(partes) != 6:
                continue

            fecha = partes[0].strip()
            cif_cliente = partes[1].strip()
            nombre_cliente = partes[2].strip()
            id_pedido = partes[3].strip()
            id_petrolera = partes[4].strip()
            importe_texto = partes[5].strip()

            if id_petrolera != int_a_texto(self.ID_PETROLERA):
                continue

            algoritmo = "SHA256"
            if self.ID_PETROLERA % 2 != 0:
                algoritmo = "SHA512"

            cliente = Cliente(nombre_cliente, cif_cliente, algoritmo)
            importe = float(importe_texto)

            self.CONTABILIDAD[id_pedido] = [importe, fecha, cliente]
            self.fecha_ultima = fecha

    def ObtenerPedidosCliente(self, cl_id):
        encontrado = False

        for pedido in self.CONTABILIDAD:
            datos = self.CONTABILIDAD[pedido]
            importe = datos[0]
            fecha = datos[1]
            cliente = datos[2]

            if cliente.CL_ID == cl_id:
                encontrado = True
                print("ID_PEDIDO:", pedido, "IMPORTE:", importe, "FECHA:", fecha)

        if encontrado is False:
            print("No hay pedidos para el cliente con CL_ID:", cl_id)

    def ReporteContabilidad(self):
        total = 0.0

        for pedido in self.CONTABILIDAD:
            datos = self.CONTABILIDAD[pedido]
            importe = datos[0]
            total = total + importe

        fecha = self.fecha_ultima
        if fecha is None:
            fecha = "SIN_FECHA"

        nombre_archivo = "reporte_petrolera_" + int_a_texto(self.ID_PETROLERA) + ".txt"
        salida = open(nombre_archivo, "w+", encoding="utf-8")

        texto_total = format(total, "f")
        linea = int_a_texto(self.ID_PETROLERA) + "@@" + texto_total + "@@" + fecha
        salida.write(linea)
        salida.close()

        return nombre_archivo

    def ImprimirDatos(self):
        print("PETROLERA")
        print("ID_PETROLERA:", self.ID_PETROLERA)
        print("NOM_PETROLERA:", self.NOM_PETROLERA)
        print("DIR_PETROLERA:", self.DIR_PETROLERA)
        print("SUMINISTROS:", self.SUMINISTROS)
        print("PEDIDOS EN CONTABILIDAD:", len(self.CONTABILIDAD))


def crear_fichero_prueba(ruta, petrolera_1, petrolera_2):
    lineas = []

    id_1 = int_a_texto(petrolera_1.ID_PETROLERA)
    id_2 = int_a_texto(petrolera_2.ID_PETROLERA)

    lineas.append("2025-04-10--A11111111--Ana--P1001--" + id_1 + "--1200.50")
    lineas.append("2025-04-11--B22222222--Luis--P1002--" + id_1 + "--300.00")
    lineas.append("2025-04-12--C33333333--Marta--P1003--" + id_1 + "--75.25")

    lineas.append("2025-05-01--D44444444--Pablo--P2001--" + id_2 + "--500.00")
    lineas.append("2025-05-02--E55555555--Sara--P2002--" + id_2 + "--999.99")
    lineas.append("2025-05-03--F66666666--Nerea--P2003--" + id_2 + "--10.00")

    archivo = open(ruta, "w+", encoding="utf-8")
    for linea in lineas:
        archivo.write(linea + "\n")
    archivo.close()


def elegir_cliente(petrolera):
    for pedido in petrolera.CONTABILIDAD:
        datos = petrolera.CONTABILIDAD[pedido]
        cliente = datos[2]
        return cliente
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fichero", required=True)
    args = parser.parse_args()

    petrolera_a = Petrolera("Petrol Norte", "Calle 1", 100)
    petrolera_b = Petrolera("Petrol Sur", "Calle 2", 200)

    crear_fichero_prueba(args.fichero, petrolera_a, petrolera_b)

    petrolera_a.RealizarContabilidad(args.fichero)
    petrolera_b.RealizarContabilidad(args.fichero)

    petrolera_a.ImprimirDatos()
    petrolera_b.ImprimirDatos()

    cliente_a = elegir_cliente(petrolera_a)
    if cliente_a is not None:
        cliente_a.ImprimirDatos()
        cliente_a.RealizarEnvio()
        petrolera_a.ObtenerPedidosCliente(cliente_a.CL_ID)

    cliente_b = elegir_cliente(petrolera_b)
    if cliente_b is not None:
        cliente_b.ImprimirDatos()
        cliente_b.RealizarEnvio()
        petrolera_b.ObtenerPedidosCliente(cliente_b.CL_ID)

    reporte_a = petrolera_a.ReporteContabilidad()
    reporte_b = petrolera_b.ReporteContabilidad()

    print("Reporte creado:", reporte_a)
    print("Reporte creado:", reporte_b)


if __name__ == "__main__":
    main()
