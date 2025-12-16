import argparse
import hashlib


def numeroDesdeTexto(texto, minimo, maximo):
    textoBytes = str(texto).encode("utf-8")
    resultado = hashlib.sha256(textoBytes).hexdigest()

    parte = resultado[0:8]
    numero = int(parte, 16)

    rango = maximo - minimo + 1
    numero = numero % rango
    numero = numero + minimo
    return numero


class Juego:
    def __init__(self, juegoNombre, juegoTipo):
        self.JUEGO_NOMBRE = juegoNombre
        self.JUEGO_TIPO = juegoTipo
        self.JUEGO_ID = self.GenerarID()

    def GenerarID(self):
        texto = self.JUEGO_NOMBRE + self.JUEGO_TIPO
        textoBytes = texto.encode("utf-8")
        return hashlib.md5(textoBytes).hexdigest()

    def Imprimir(self):
        print(self.JUEGO_NOMBRE + " - " + self.JUEGO_TIPO + " - " + self.JUEGO_ID)


class Jugador:
    def __init__(self, jugadorName, jugadorMail):
        self.JUGADOR_ID = numeroDesdeTexto(jugadorName + jugadorMail, 1000, 9999)
        self.JUGADOR_NAME = jugadorName
        self.JUGADOR_MAIL = jugadorMail
        self.JUGADOR_KEY = self.CrearKey()
        self.JUEGOS = {}

    def CrearKey(self):
        nombre = self.JUGADOR_NAME.strip()

        primeraLetra = ""
        if len(nombre) > 0:
            primeraLetra = nombre[0].upper()

        dosUltimas = ""
        if len(nombre) >= 2:
            dosUltimas = nombre[-2:].lower()

        patron = primeraLetra + dosUltimas + "ufv."
        patronBytes = patron.encode("utf-8")
        return hashlib.sha256(patronBytes).hexdigest()

    def ListaJuegos(self, ficheroRegistro, listaJuegosDisponibles):
        juegosPorId = {}

        for juegoTexto in listaJuegosDisponibles:
            partesJuego = juegoTexto.split("-", 1)
            if len(partesJuego) == 2:
                juegoNombre = partesJuego[0]
                juegoTipo = partesJuego[1]
                juego = Juego(juegoNombre, juegoTipo)
                juegosPorId[juego.JUEGO_ID] = juego

        fichero = open(ficheroRegistro, "r", encoding="utf-8")
        lineas = fichero.readlines()
        fichero.close()

        for linea in lineas:
            linea = linea.strip()
            if linea == "":
                continue

            partesRegistro = linea.split("||")
            if len(partesRegistro) != 4:
                continue

            juegoId = partesRegistro[0]
            jugadorKey = partesRegistro[1]
            puntosTexto = partesRegistro[3]

            if jugadorKey != self.JUGADOR_KEY:
                continue

            if juegoId not in juegosPorId:
                continue

            puntos = 0
            if puntosTexto.isdigit():
                puntos = int(puntosTexto)

            juego = juegosPorId[juegoId]
            juegoNombre = juego.JUEGO_NOMBRE

            if juegoNombre not in self.JUEGOS:
                self.JUEGOS[juegoNombre] = {"JUEGO": juego, "PUNTOS": 0}

            puntosActuales = self.JUEGOS[juegoNombre]["PUNTOS"]
            puntosActuales = puntosActuales + puntos
            self.JUEGOS[juegoNombre]["PUNTOS"] = puntosActuales

    def Puntuacion(self, nombreJuego=None):
        if nombreJuego is None:
            for juegoNombre in self.JUEGOS:
                puntos = self.JUEGOS[juegoNombre]["PUNTOS"]
                print(juegoNombre + ": " + str(puntos))
            return

        if nombreJuego in self.JUEGOS:
            puntos = self.JUEGOS[nombreJuego]["PUNTOS"]
            print(nombreJuego + ": " + str(puntos))
            return

        print(nombreJuego + ": 0")

    def Imprimir(self):
        print("Jugador: " + self.JUGADOR_NAME + " - " + self.JUGADOR_MAIL)
        print("ID: " + str(self.JUGADOR_ID))
        print("KEY: " + self.JUGADOR_KEY)


class ListaJugadores:
    def __init__(self, fichero):
        self.FICHERO = fichero
        self.JUGADORES = []
        self.leerJugadores()

    def leerJugadores(self):
        fichero = open(self.FICHERO, "r", encoding="utf-8")
        lineas = fichero.readlines()
        fichero.close()

        for linea in lineas:
            linea = linea.strip()
            if linea == "":
                continue

            partes = linea.split("@@")
            if len(partes) != 2:
                continue

            jugadorName = partes[0].strip()
            jugadorMail = partes[1].strip()

            jugador = Jugador(jugadorName, jugadorMail)
            self.JUGADORES.append(jugador)

    def Imprimir(self):
        for jugador in self.JUGADORES:
            jugador.Imprimir()


class Diagnostico:
    def __init__(self, ficheroRegistro, jugadores, juegos):
        self.FICHERO_REGISTRO = ficheroRegistro
        self.JUGADORES = jugadores
        self.JUEGOS = juegos

        self.jugadoresValidos = set()
        self.juegosValidos = set()

        self.cargarValidos()

    def cargarValidos(self):
        for jugador in self.JUGADORES:
            self.jugadoresValidos.add(jugador.JUGADOR_KEY)

        for juegoTexto in self.JUEGOS:
            partesJuego = juegoTexto.split("-", 1)
            if len(partesJuego) == 2:
                juegoNombre = partesJuego[0]
                juegoTipo = partesJuego[1]
                juego = Juego(juegoNombre, juegoTipo)
                self.juegosValidos.add(juego.JUEGO_ID)

    def GenFraudulentos(self):
        fichero = open(self.FICHERO_REGISTRO, "r", encoding="utf-8")
        lineas = fichero.readlines()
        fichero.close()

        lineasSalida = []
        lineasUnicas = set()

        contadorPlayer = 0
        contadorGame = 0
        fechasTipos = {}

        for linea in lineas:
            linea = linea.strip()
            if linea == "":
                continue

            partesRegistro = linea.split("||")
            if len(partesRegistro) != 4:
                continue

            juegoId = partesRegistro[0]
            jugadorKey = partesRegistro[1]
            fecha = partesRegistro[2]

            jugadorInvalido = False
            juegoInvalido = False

            if jugadorKey not in self.jugadoresValidos:
                jugadorInvalido = True

            if juegoId not in self.juegosValidos:
                juegoInvalido = True

            if jugadorInvalido:
                salida = "PLAYER##" + jugadorKey + "##" + fecha
                if salida not in lineasUnicas:
                    lineasUnicas.add(salida)
                    lineasSalida.append(salida)
                contadorPlayer = contadorPlayer + 1
                self.anadirTipoFecha(fechasTipos, fecha, "PLAYER")

            if juegoInvalido:
                salida = "GAME##" + juegoId + "##" + fecha
                if salida not in lineasUnicas:
                    lineasUnicas.add(salida)
                    lineasSalida.append(salida)
                contadorGame = contadorGame + 1
                self.anadirTipoFecha(fechasTipos, fecha, "GAME")

        ficheroSalida = open("BAD_REGISTERS.log", "w+", encoding="utf-8")
        for salida in lineasSalida:
            ficheroSalida.write(salida + "\n")
        ficheroSalida.close()

        return contadorPlayer, contadorGame, fechasTipos

    def anadirTipoFecha(self, fechasTipos, fecha, tipo):
        if fecha not in fechasTipos:
            fechasTipos[fecha] = []

        if tipo not in fechasTipos[fecha]:
            fechasTipos[fecha].append(tipo)

    def Informe(self, fechasTipos):
        fechasOrdenadas = sorted(fechasTipos.keys(), key=self.claveFecha)
        for fecha in fechasOrdenadas:
            tipos = fechasTipos[fecha]
            textoTipos = ", ".join(tipos)
            print(fecha + ": " + textoTipos)

    def claveFecha(self, fecha):
        partes = fecha.split("/")
        if len(partes) != 3:
            return fecha

        dia = partes[0]
        mes = partes[1]
        anio = partes[2]

        return anio + mes + dia


def crearParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--players", default="PLAYERS-1.txt")
    parser.add_argument("-r", "--registros", default="REGISTROS-2.log")
    return parser


if __name__ == "__main__":
    listaJuegosDisponibles = [
        "Mus-Cartas",
        "Laberinto-Tablero",
        "Poker-Cartas",
        "Basket-Deporte",
        "LOL-Videojuego",
        "Fornite-Videojuego",
        "Pocha-Cartas",
        "Catan-Tablero",
        "Monopoly-Tablero",
        "Virus-Cartas",
        "Heroquest-Tablero",
        "Futbol-Deporte",
        "Damas-Tablero",
        "Ajedrez-Tablero",
    ]

    parser = crearParser()
    args = parser.parse_args()

    listaJugadores = ListaJugadores(args.players)

    diagnostico = Diagnostico(args.registros, listaJugadores.JUGADORES, listaJuegosDisponibles)
    registrosPlayerFalsos, registrosGameFalsos, fechasTipos = diagnostico.GenFraudulentos()

    print("Registros falsos de jugadores: " + str(registrosPlayerFalsos))
    print("Registros falsos de juegos: " + str(registrosGameFalsos))
    print("Dias con registros falsos (y tipo):")
    diagnostico.Informe(fechasTipos)

    if len(listaJugadores.JUGADORES) > 0:
        jugador = listaJugadores.JUGADORES[0]
        jugador.ListaJuegos(args.registros, listaJuegosDisponibles)
        print("Puntuaciones del primer jugador:")
        jugador.Puntuacion()

