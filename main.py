import flet as ft
import swisseph as swe
import matplotlib.pyplot as plt
from geopy.geocoders import OpenCage
from assets.interpretations import interpretations

# Установите путь к файлам эфемерид
swe.set_ephe_path("ephemeris")  # Замените на путь к вашим файлам

# Настройка геокодера OpenCage
geolocator = OpenCage(api_key='01fac9ae579e4eadb5c080253e952fcf')

# Получение координат по названию города
def get_coordinates(city_name):
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None, None

# Получение знака зодиака
def get_zodiac_sign(degree):
    signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn",
             "aquarius", "pisces"]
    return signs[int(degree / 30)]

# Интерпретация планет в знаках
def interpret_planet_sign(planet, sign):
    return interpretations.get(planet, {}).get(sign, "No interpretation available.")

def main(page: ft.Page):
    page.adaptive = True
    page.title = "Natal Chart Generator"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    history = []  # Список для хранения истории интерпретаций

    def process_data(e):
        try:
            date_of_birth = entry_date.value
            time_of_birth = entry_time.value
            city_name = entry_city.value

            year, month, day = map(int, date_of_birth.split('-'))
            hour, minute = map(int, time_of_birth.split(':'))
            latitude, longitude = get_coordinates(city_name)

            if latitude is None or longitude is None:
                ft.dialog("Ошибка", "Неверное название города")
                return

            julday = swe.julday(year, month, day, hour + minute / 60.0)
            planets = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
                       swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO]

            planet_positions = {}
            for planet in planets:
                lon, lat, rad = swe.calc_ut(julday, planet)[0][:3]
                planet_positions[planet] = lon

            houses, ascmc = swe.houses(julday, latitude, longitude, b'P')

            interpretation = "Интерпретация натальной карты:\n\n"
            for planet, position in planet_positions.items():
                sign = get_zodiac_sign(position)
                planet_name = swe.get_planet_name(planet).lower()
                interpretation += f"{swe.get_planet_name(planet)} в {sign.capitalize()}:\n"
                interpretation += f"{interpret_planet_sign(planet_name, sign)}\n\n"

            # Добавляем интерпретацию в историю
            history.append(interpretation)

            text_output.content.controls[0].value = interpretation

            plt.figure(figsize=(10, 10))
            plt.polar([position for position in planet_positions.values()], [1] * len(planet_positions), 'o')
            plt.title("Расположение планет при рождении")
            for planet, position in planet_positions.items():
                plt.text(position, 1, swe.get_planet_name(planet), horizontalalignment='center',
                         verticalalignment='center')
            plt.savefig('natal_chart.png')
            image.src = 'natal_chart.png'
            page.update()

        except Exception as e:
            ft.dialog("Ошибка", f"Произошла ошибка при обработке данных: {e}")

    entry_date = ft.TextField(label="Дата рождения (ГГГГ-ММ-ДД)", width=400)
    entry_time = ft.TextField(label="Время рождения (ЧЧ:ММ)", width=400)
    entry_city = ft.TextField(label="Город рождения", width=400)
    button_generate = ft.ElevatedButton(text="Сгенерировать натальную карту", on_click=process_data, width=400)

    text_output = ft.Container(
        content=ft.ListView(
            controls=[
                ft.Text(expand=True, selectable=False)
            ],
            spacing=0,
            padding=0,
            expand=True,
            auto_scroll=True,
        ),
        height=300
    )
    image = ft.Image(width=500, height=500)

    left_column = ft.Column(
        [
            entry_date,
            entry_time,
            entry_city,
            button_generate,
            text_output,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=600,
    )

    right_column = ft.Column(
        [
            image,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=600,
    )

    page.add(
        ft.Row(
            [
                left_column,
                right_column,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
    )
    page.update()  # Обновляем страницу

ft.app(target=main)

