def get_avatar_url(temp, wind, condition="sun"):
    avatars = {
        "snow": "https://openweathermap.org/img/wn/13d@4x.png",
        "rain": "https://openweathermap.org/img/wn/09d@4x.png",
        "sun": "https://openweathermap.org/img/wn/01d@4x.png",
        "cloud": "https://openweathermap.org/img/wn/03d@4x.png",
        "windy": "https://openweathermap.org/img/wn/50d@4x.png"
    }

    if wind > 25:
        return avatars["windy"]

    return avatars.get(condition, avatars["sun"])