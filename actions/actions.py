import json
import os.path
from typing import Any, Text, Dict, List
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from swiplserver import PrologMQI
from unidecode import unidecode
import requests


def simplificar_nombre_asignatura(s):

    def reemplazar_romanos(s):
        if (s[-3:] == " ii"):
            s = s[:-2] + "2"
        elif (s[-2:] == " i"):
            s = s[:-1] + "1"

        if s[-1] != "1" and s[-1] != "2":
            s = s + " 1"

        return s

    return reemplazar_romanos(unidecode(s).strip().lower())


def comparar_asignaturas(a, b):
    a = simplificar_nombre_asignatura(a)
    b = simplificar_nombre_asignatura(b)

    return a == b


class ActionClima(Action):
    def name(self):
        return "action_clima"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        ciudad = tracker.get_slot('localidad')

        # print(ciudad)
        # api_key = "afae512bb4cb0ed78833952e89f8617b"

        owm = OWM('afae512bb4cb0ed78833952e89f8617b')
        mgr = owm.weather_manager()


        observation = mgr.weather_at_place(ciudad)
        w = observation.weather

        w.detailed_status  # 'clouds'
        w.wind()  # {'speed': 4.6, 'deg': 330}
        w.humidity  # 87
        temp = w.temperature('celsius')["temp"]  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
        w.rain  # {}

        # Will it be clear tomorrow at this time in Milan (Italy) ?
        # forecast = mgr.forecast_at_place('Milan,IT', 'daily')
        # answer = forecast.will_be_clear_at(timestamps.tomorrow())

        clima_data = f" Hace {temp}°C actualmente en {ciudad}"
        dispatcher.utter_message(clima_data)

        return [SlotSet("localidad", ciudad)]

class ActionPresentacion(Action):

    def name(self):
        return "action_presentacion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nombre_persona = tracker.latest_message["metadata"]["from"]["first_name"]

        texto = f"Hola {nombre_persona} ¿Todo bien?"
        dispatcher.utter_message(texto)

        return []

class ActionDespedida(Action):

    def name(self):
        return "action_despedida"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nombre= tracker.latest_message["metadata"]["from"]["first_name"]

        texto = f"Chau {nombre} nos vemos!"
        dispatcher.utter_message(texto)

        return []

class ActionEstadoMateria(Action):

    def name(self) -> Text:
        return "action_estado_materia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if len(tracker.latest_message["entities"][0]) == 0:
            print("No se detecto la entidad")
            return []

        # materia = str(tracker.latest_message['entities'][0]['value'])
        materia = tracker.get_slot("materia")

        message = None
        if comparar_asignaturas("Programacion Exploratoria", materia):
            message = "Voy justo tirando a atrasado, lamentablemente mi padre estuvo delicado de salud y tuve que dejar el tiempo de estudio para ir a cuidarlo"
        elif comparar_asignaturas("Investigacion Operativa", materia):
            message = "Es la que mejor voy! Todo ok por ahora"
        elif comparar_asignaturas("Programacion Orientada a Objetos", materia):
            message = "Todavia no he tocado nada de objetos, pero como la estoy recursando me acuerdo algunos conceptos, cuando tenga tiempo me pondre al dia"
        elif comparar_asignaturas("Comunicacion de Datos I", materia):
            message = "Lastimosamente creo que voy a dejar de cursarla porque no llego con los tiempos y trabajos que piden"
        else:
            message = "No estoy cursando esa materia"

        dispatcher.utter_message(text=message)
        return [SlotSet("materia", materia)]


class ActionOpinionMateria(Action):

    def name(self) -> Text:
        return "action_opinion_materia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        materia = tracker.get_slot("materia")

        message = None

        if comparar_asignaturas("Programacion Exploratoria", materia):
            message = "Me encanta la materia, me gustaria aprender mas a futuro relacionado a IA y Machine learning o Deep Learning"
        elif comparar_asignaturas("Investigacion Operativa", materia) or comparar_asignaturas("Comunicacion de Datos I", materia):
            message = "No me esta gustando mucho pero se la utilidad que tiene"
        elif comparar_asignaturas("Programacion Orientada a Objetos", materia):
            message = "Me encanta aunque me cuesta, la veo muy util para poder conseguir un trabajo a corto plazo"
        else:
            message = "Me encanta esa materia" # ASD

        dispatcher.utter_message(text=message)

        return []


class OperarArchivo():

    @staticmethod
    def guardar(AGuardar):
        with open("./actions/data.json", "w") as archivo_descarga:
            json.dump(AGuardar, archivo_descarga, indent=4)
        archivo_descarga.close()

    @staticmethod
    def cargarArchivo():
        if os.path.isfile("/home/rama/PycharmProjects/proyectoRasa/actions/data.json"):
            with open("/home/rama/PycharmProjects/proyectoRasa/actions/data.json", "r") as archivo_carga:
                retorno = json.load(archivo_carga)
                archivo_carga.close()
        else:
            retorno = {}
        return retorno


class ActionExtraerDatosHorarios(Action):

    def name(self) -> Text:
        return "action_horarios_materia"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        materia = tracker.get_slot("materia")
        horarios = OperarArchivo.cargarArchivo()

        listaClaves = list(horarios.keys())
        claveJson = None

        for clave in listaClaves:
            if comparar_asignaturas(materia, clave):
                claveJson = clave
                break

        if not claveJson:
            dispatcher.utter_message(text="No estoy cursando eso.")
            return []

        message = f"{materia} curso los "

        for i in range(len(horarios[claveJson]["dia"])):
            dia = horarios[claveJson]["dia"][i]
            horario = horarios[claveJson]["horario"][i]
            message += f"{dia} de {horario} y los "

        message = message[:-7]

        dispatcher.utter_message(text=message)

        return []


class ActionPROLOGMateriasCursando(Action):

    def name(self) -> Text:
        return "action_materias_cursando"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query_async(r"consult('/home/rama/PycharmProjects/proyectoRasa/data/Materias IS prolog.pl')", find_all=False)
                prolog_thread.query_async(f"materias_cursando(Lista)", find_all=False)
                result = prolog_thread.query_async_result()[0]['Lista']
                dispatcher.utter_message(f"Estoy cursando 3 materias de 3er año y una de segundo: \n")
                for materia in result:
                    dispatcher.utter_message(text=f"- {materia}")
        return []


class ActionPROLOGMateriasAnio(Action):

    def name(self) -> Text:
        return "action_materias_de_anio"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query_async(r"consult('/home/rama/PycharmProjects/proyectoRasa/data/Materias IS prolog.pl')", find_all=False)
                anio = next(tracker.get_latest_entity_values("anio"), None)
                if (int(anio) < 6):
                    prolog_thread.query_async(f"materias_de({anio},Lista)", find_all=False)
                    result = prolog_thread.query_async_result()[0]['Lista']
                    dispatcher.utter_message(f"Materias de {anio} : \n")
                    for materia in result:
                        dispatcher.utter_message(text=f"- {materia}")
                else:
                    dispatcher.utter_message(text="La duracion de la carrera es de 5 años!")
        return []