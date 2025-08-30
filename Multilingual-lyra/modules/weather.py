import datetime

def get_weather(city: str) -> str:
    if not city:
        return "Please specify a city."
    # TODO: integrate real weather API (OpenWeatherMap, etc.)
    return f"Weather in {city}: 29°C, partly cloudy."

def get_time_str() -> str:
    now = datetime.datetime.now()
    return f"It’s {now.strftime('%A, %d %B %Y, %H:%M:%S')}."