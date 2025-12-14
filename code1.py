print("POLSEN PALOMO")
import hashlib
import re


class Country:
    def __init__(self, name):
        self.c_name = name
        self.alg = self.GetAlg()

    def SetAlgs(self):
        return {
            "SHA512": ["ES", "CHN", "SIN"],
            "SHA256": ["BEL", "EGY", "JAP"],
            "MD5": ["GER", "FR", "IT"]
        }

    def GetAlg(self):
        diccionario = self.SetAlgs()
        for nombre_algoritmo in diccionario:
            lista_paises = diccionario[nombre_algoritmo]
            if self.c_name in lista_paises:
                return nombre_algoritmo
        raise ValueError("País no soportado: " + str(self.c_name))


class Ship:
    def __init__(self, number, country_name):
        self.s_number = int(number)
        self.country_name = country_name
        self.s_id = self.GenID()

    def GenID(self):
        pais = Country(self.country_name)
        texto = self.GetIDClaro()
        return self._calcular_hash(pais.alg, texto)

    def _calcular_hash(self, nombre_algoritmo, texto):
        nombre = self._normalizar_algoritmo(nombre_algoritmo)
        h = hashlib.new(nombre)
        h.update(texto.encode("utf-8"))
        return h.hexdigest()

    def _normalizar_algoritmo(self, nombre_algoritmo):
        if nombre_algoritmo == "SHA512":
            return "sha512"
        if nombre_algoritmo == "SHA256":
            return "sha256"
        if nombre_algoritmo == "MD5":
            return "md5"
        raise ValueError("Algoritmo no soportado: " + str(nombre_algoritmo))

    def GetIDClaro(self):
        numero_formateado = str(self.s_number).zfill(2)
        return numero_formateado + "*" + self.country_name.upper()

    def __str__(self):
        return "Ship(numero=" + str(self.s_number) + ", pais=" + self.country_name.upper() + ", id_claro=" + self.GetIDClaro() + ")"


class Port:
    def __init__(self, name, country):
        self.p_name = name
        self.country = country
        self.ships = {}
        self.p_id = self._generar_id_puerto()

    def _generar_id_puerto(self):
        texto = self.country.c_name.upper()
        nombre = self._normalizar_algoritmo(self.country.alg)
        h = hashlib.new(nombre)
        h.update(texto.encode("utf-8"))
        return h.hexdigest()

    def _normalizar_algoritmo(self, nombre_algoritmo):
        if nombre_algoritmo == "SHA512":
            return "sha512"
        if nombre_algoritmo == "SHA256":
            return "sha256"
        if nombre_algoritmo == "MD5":
            return "md5"
        raise ValueError("Algoritmo no soportado: " + str(nombre_algoritmo))

    def DecodeShipID(self, s_id):
        paises = Country("ES").SetAlgs()
        for nombre_algoritmo in paises:
            lista_paises = paises[nombre_algoritmo]
            for codigo_pais in lista_paises:
                for numero in range(0, 100):
                    numero_formateado = str(numero).zfill(2)
                    id_claro = numero_formateado + "*" + codigo_pais.upper()
                    nombre = self._normalizar_algoritmo(nombre_algoritmo)
                    h = hashlib.new(nombre)
                    h.update(id_claro.encode("utf-8"))
                    if h.hexdigest() == s_id:
                        return id_claro
        return None

    def SetShips(self, ruta_fichero_registro):
        self.ships["ENTRADA"] = {}
        self.ships["SALIDA"] = {}

        patron = re.compile(r"^\d{4}-\d{2}-\d{2}//(ENTRADA|SALIDA)//[0-9a-fA-F]+//[0-9a-fA-F]+$")

        f = open(ruta_fichero_registro, "r", encoding="utf-8")
        lineas = f.readlines()
        f.close()

        for linea in lineas:
            linea = linea.strip()
            if linea == "":
                continue
            if patron.match(linea) is None:
                continue

            partes = linea.split("//")
            fecha = partes[0]
            registro = partes[1]
            puerto_id = partes[2]
            embarcacion_id = partes[3]

            if puerto_id != self.p_id:
                continue

            id_claro = self.DecodeShipID(embarcacion_id)
            if id_claro is None:
                continue

            partes_barco = id_claro.split("*")
            numero = int(partes_barco[0])
            codigo_pais = partes_barco[1]
            barco = Ship(numero, codigo_pais)

            if fecha not in self.ships[registro]:
                self.ships[registro][fecha] = []
            self.ships[registro][fecha].append(barco)


class Report:
    def __init__(self, port, file):
        self.port = port
        self.file = file

    def GetReport(self, tipo=None):
        tipo_normalizado = None
        if tipo is not None:
            tipo_normalizado = tipo.strip().upper()

        if tipo_normalizado == "ENTRADA":
            tipos = ["ENTRADA"]
            sufijo = "ENTRADA"
        elif tipo_normalizado == "SALIDA":
            tipos = ["SALIDA"]
            sufijo = "SALIDA"
        else:
            tipos = ["ENTRADA", "SALIDA"]
            sufijo = "COMPLETO"

        nombre_salida = "reporte_" + self.port.p_name.replace(" ", "_") + "_" + sufijo + ".txt"

        f = open(nombre_salida, "w+", encoding="utf-8")
        f.write("REPORTE DE PUERTO\n")
        f.write("Puerto: " + self.port.p_name + "\n")
        f.write("Pais: " + self.port.country.c_name.upper() + "\n")
        f.write("Puerto_ID (hash): " + self.port.p_id + "\n")
        f.write("\n")

        for t in tipos:
            f.write("=== " + t + " ===\n")
            if t not in self.port.ships:
                f.write("Sin datos.\n\n")
                continue

            fechas = list(self.port.ships[t].keys())
            fechas_ordenadas = sorted(fechas)

            for fecha in fechas_ordenadas:
                f.write(fecha + "\n")
                lista_barcos = self.port.ships[t][fecha]
                for barco in lista_barcos:
                    f.write("  - " + str(barco) + "\n")
                f.write("\n")

        f.close()
        return nombre_salida


def _encontrar_puerto_para_prueba(ruta_fichero):
    f = open(ruta_fichero, "r", encoding="utf-8")
    lineas = f.readlines()
    f.close()

    p_id_objetivo = None
    for linea in lineas:
        linea = linea.strip()
        if linea == "":
            continue
        partes = linea.split("//")
        if len(partes) == 4:
            p_id_objetivo = partes[2]
            break

    if p_id_objetivo is None:
        return Port("PuertoPrueba", Country("ES"))

    diccionario = Country("ES").SetAlgs()
    for nombre_algoritmo in diccionario:
        lista_paises = diccionario[nombre_algoritmo]
        for codigo_pais in lista_paises:
            pais = Country(codigo_pais)
            puerto = Port("PuertoPrueba", pais)
            if puerto.p_id == p_id_objetivo:
                return puerto

    return Port("PuertoPrueba", Country("ES"))


if __name__ == "__main__":
    ruta = "/mnt/data/ShipsRegisters.log"

    puerto = _encontrar_puerto_para_prueba(ruta)
    puerto.SetShips(ruta)

    reporte = Report(puerto, ruta)
    fichero_completo = reporte.GetReport()
    fichero_entrada = reporte.GetReport("ENTRADA")
    fichero_salida = reporte.GetReport("SALIDA")

    print("Puerto de prueba:", puerto.p_name, "-", puerto.country.c_name.upper())
    print("Puerto_ID:", puerto.p_id)
    print("Ficheros generados:", fichero_completo, fichero_entrada, fichero_salida)
