const I18N = {
  ru: {
    pageTitle: "Прогноз погоды — 7 дней",
    forecastBadge: "Прогноз погоды",
    forecastTitle: "Прогноз на 7 дней",
    loading: "Загрузка...",
    buildingForecast: "Строим прогноз...",
    lastKnownData: "Последние данные",
    model: "Модель",
    avgTempWeek: "Средняя t° за неделю",
    tempRangeWeek: "Диапазон t°",
    weeklyPrecip: "Осадки за неделю",
    avgTemperature: "средняя температура",
    min: "Мин.",
    max: "Макс.",
    tempLegend: "Слева холоднее, справа теплее",
    detailedForecast: "Подробный прогноз",
    forecastError: "Не удалось получить прогноз",
    precip: "Осадки",
    wind: "Ветер",
    gusts: "Порывы",
    direction: "Направление",
    sunrise: "Восход",
    sunset: "Закат",
    groups: {
      temperature: "Температура",
      precipitation: "Осадки",
      wind: "Ветер",
      sun: "Солнце и свет",
    },
    weekdays: [
      "Понедельник",
      "Вторник",
      "Среда",
      "Четверг",
      "Пятница",
      "Суббота",
      "Воскресенье",
    ],
    weekdaysShort: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    windDirections: ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"],
    units: {
      hours: "ч",
      mm: "мм",
      cm: "см",
      kmh: "км/ч",
      mj: "МДж/м²",
    },
    params: {
      weather_code: "Код погоды",
      temperature_2m_mean: "Температура средняя, °C",
      temperature_2m_max: "Температура макс., °C",
      temperature_2m_min: "Температура мин., °C",
      apparent_temperature_mean: "Ощущается средняя, °C",
      apparent_temperature_max: "Ощущается макс., °C",
      apparent_temperature_min: "Ощущается мин., °C",
      sunrise: "Восход",
      sunset: "Закат",
      daylight_duration: "Длительность светового дня",
      sunshine_duration: "Длительность солнечного сияния",
      precipitation_sum: "Осадки, мм",
      rain_sum: "Дождь, мм",
      snowfall_sum: "Снег, см",
      precipitation_hours: "Часы с осадками",
      wind_speed_10m_max: "Ветер макс., км/ч",
      wind_gusts_10m_max: "Порывы ветра, км/ч",
      wind_direction_10m_dominant: "Направление ветра",
      shortwave_radiation_sum: "Солнечная радиация, МДж/м²",
      et0_fao_evapotranspiration: "Испарение ET0, мм",
    },
    weather: {
      0: "Ясно",
      1: "Преимущественно ясно",
      2: "Переменная облачность",
      3: "Пасмурно",
      4: "Дымка",
      5: "Дымка",
      6: "Пыль",
      7: "Пыльное вихри",
      8: "Смерч",
      9: "Пыльная буря",
      10: "Мгла",
      11: "Ледяная крупа",
      12: "Морось",
      13: "Ледяные зёрна",
      14: "Осадки",
      15: "Ливневые осадки",
      16: "Ливневые осадки",
      17: "Гроза",
      18: "Ливневые осадки",
      19: "Ливневые осадки",
      20: "Осадки",
      21: "Осадки",
      22: "Снег",
      23: "Снег",
      24: "Мокрый снег",
      25: "Ливневые осадки",
      26: "Ливневые осадки",
      27: "Ливневые осадки",
      28: "Ливневые осадки",
      29: "Гроза с градом",
      30: "Пыльная дымка",
      31: "Пыльная дымка",
      32: "Сильный ветер",
      33: "Сильный ветер",
      34: "Сильная гроза",
      35: "Пыльная буря",
      36: "Позёмка",
      37: "Сильный ветер",
      38: "Позёмка",
      39: "Метель",
      40: "Туман",
      41: "Туман",
      42: "Туман",
      43: "Туман",
      44: "Туман",
      45: "Туман",
      46: "Туман",
      47: "Туман",
      48: "Изморозь",
      49: "Туман",
      51: "Морось",
      53: "Морось",
      55: "Сильная морось",
      56: "Ледяная морось",
      57: "Ледяная морось",
      61: "Дождь",
      63: "Дождь",
      65: "Сильный дождь",
      66: "Ледяной дождь",
      67: "Ледяной дождь",
      71: "Снег",
      73: "Снег",
      75: "Сильный снег",
      77: "Снежная крупа",
      80: "Ливень",
      81: "Ливень",
      82: "Сильный ливень",
      85: "Снегопад",
      86: "Сильный снегопад",
      95: "Гроза",
      96: "Гроза с градом",
      99: "Гроза с градом",
      decade: {
        0: "Ясно",
        10: "Осадки",
        20: "Осадки",
        30: "Метель",
        40: "Туман",
        50: "Морось",
        60: "Дождь",
        70: "Снег",
        80: "Ливень",
        90: "Гроза",
      },
      fallback: "Переменная погода",
    },
  },
  en: {
    pageTitle: "Weather Forecast — 7 Days",
    forecastBadge: "Weather forecast",
    forecastTitle: "7-Day Forecast",
    loading: "Loading...",
    buildingForecast: "Building forecast...",
    lastKnownData: "Latest data",
    model: "Model",
    avgTempWeek: "Average temp (week)",
    tempRangeWeek: "Temp range",
    weeklyPrecip: "Weekly precipitation",
    avgTemperature: "average temperature",
    min: "Min.",
    max: "Max.",
    tempLegend: "Colder on the left, warmer on the right",
    detailedForecast: "Detailed forecast",
    forecastError: "Failed to load forecast",
    precip: "Precipitation",
    wind: "Wind",
    gusts: "Gusts",
    direction: "Direction",
    sunrise: "Sunrise",
    sunset: "Sunset",
    groups: {
      temperature: "Temperature",
      precipitation: "Precipitation",
      wind: "Wind",
      sun: "Sun and light",
    },
    weekdays: [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
      "Sunday",
    ],
    weekdaysShort: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    windDirections: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    units: {
      hours: "h",
      mm: "mm",
      cm: "cm",
      kmh: "km/h",
      mj: "MJ/m²",
    },
    params: {
      weather_code: "Weather code",
      temperature_2m_mean: "Mean temperature, °C",
      temperature_2m_max: "Max temperature, °C",
      temperature_2m_min: "Min temperature, °C",
      apparent_temperature_mean: "Feels like mean, °C",
      apparent_temperature_max: "Feels like max, °C",
      apparent_temperature_min: "Feels like min, °C",
      sunrise: "Sunrise",
      sunset: "Sunset",
      daylight_duration: "Daylight duration",
      sunshine_duration: "Sunshine duration",
      precipitation_sum: "Precipitation, mm",
      rain_sum: "Rain, mm",
      snowfall_sum: "Snowfall, cm",
      precipitation_hours: "Precipitation hours",
      wind_speed_10m_max: "Max wind speed, km/h",
      wind_gusts_10m_max: "Wind gusts, km/h",
      wind_direction_10m_dominant: "Wind direction",
      shortwave_radiation_sum: "Shortwave radiation, MJ/m²",
      et0_fao_evapotranspiration: "ET0 evapotranspiration, mm",
    },
    weather: {
      0: "Clear",
      1: "Mainly clear",
      2: "Partly cloudy",
      3: "Overcast",
      4: "Haze",
      5: "Haze",
      6: "Dust",
      7: "Dust whirls",
      8: "Tornado",
      9: "Dust storm",
      10: "Mist",
      11: "Ice pellets",
      12: "Drizzle",
      13: "Ice grains",
      14: "Precipitation",
      15: "Shower precipitation",
      16: "Shower precipitation",
      17: "Thunderstorm",
      18: "Shower precipitation",
      19: "Shower precipitation",
      20: "Precipitation",
      21: "Precipitation",
      22: "Snow",
      23: "Snow",
      24: "Sleet",
      25: "Shower precipitation",
      26: "Shower precipitation",
      27: "Shower precipitation",
      28: "Shower precipitation",
      29: "Thunderstorm with hail",
      30: "Dust haze",
      31: "Dust haze",
      32: "High wind",
      33: "High wind",
      34: "Heavy thunderstorm",
      35: "Dust storm",
      36: "Blowing snow",
      37: "High wind",
      38: "Blowing snow",
      39: "Blizzard",
      40: "Fog",
      41: "Fog",
      42: "Fog",
      43: "Fog",
      44: "Fog",
      45: "Fog",
      46: "Fog",
      47: "Fog",
      48: "Rime fog",
      49: "Fog",
      51: "Drizzle",
      53: "Drizzle",
      55: "Heavy drizzle",
      56: "Freezing drizzle",
      57: "Freezing drizzle",
      61: "Rain",
      63: "Rain",
      65: "Heavy rain",
      66: "Freezing rain",
      67: "Freezing rain",
      71: "Snow",
      73: "Snow",
      75: "Heavy snow",
      77: "Snow grains",
      80: "Rain shower",
      81: "Rain shower",
      82: "Heavy rain shower",
      85: "Snow shower",
      86: "Heavy snow shower",
      95: "Thunderstorm",
      96: "Thunderstorm with hail",
      99: "Thunderstorm with hail",
      decade: {
        0: "Clear",
        10: "Precipitation",
        20: "Precipitation",
        30: "Blizzard",
        40: "Fog",
        50: "Drizzle",
        60: "Rain",
        70: "Snow",
        80: "Rain shower",
        90: "Thunderstorm",
      },
      fallback: "Mixed conditions",
    },
  },
};

const DETAIL_GROUP_KEYS = {
  temperature: [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
  ],
  precipitation: [
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "precipitation_hours",
  ],
  wind: [
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",
  ],
  sun: [
    "sunrise",
    "sunset",
    "daylight_duration",
    "sunshine_duration",
    "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
  ],
};

let currentLang = localStorage.getItem("forecast-lang") || "ru";

function t(key) {
  const parts = key.split(".");
  let value = I18N[currentLang];
  for (const part of parts) {
    value = value?.[part];
  }
  return value ?? key;
}

function setLanguage(lang) {
  if (!I18N[lang]) return;
  currentLang = lang;
  localStorage.setItem("forecast-lang", lang);
  document.documentElement.lang = lang;
  document.title = t("pageTitle");
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll(".lang-switch__btn").forEach((btn) => {
    btn.classList.toggle("lang-switch__btn--active", btn.dataset.lang === lang);
  });
  document.querySelectorAll(".lang-switch").forEach((switchEl) => {
    switchEl.dataset.active = lang;
  });
  if (typeof window.onLanguageChange === "function") {
    window.onLanguageChange();
  }
}

function getWeatherLabel(code) {
  const weather = I18N[currentLang].weather;
  const normalized = Math.max(0, Math.min(99, Math.round(code)));
  if (weather[normalized]) return weather[normalized];
  const decade = Math.floor(normalized / 10) * 10;
  return weather.decade[decade] || weather.fallback;
}

function getWeekdayLabel(weekday, short = false) {
  const labels = short ? I18N[currentLang].weekdaysShort : I18N[currentLang].weekdays;
  return labels[weekday] ?? "";
}

function getWindDirectionLabel(degrees) {
  const index = Math.floor((degrees + 22.5) / 45) % 8;
  return I18N[currentLang].windDirections[index];
}

function formatTimeFromTimestamp(timestamp, timezone) {
  return new Intl.DateTimeFormat(currentLang === "ru" ? "ru-RU" : "en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: timezone,
  }).format(new Date(timestamp * 1000));
}

function formatParamValue(key, raw, timezone) {
  const units = I18N[currentLang].units;

  if (key === "weather_code") return String(Math.round(raw));
  if (key === "sunrise" || key === "sunset") {
    return formatTimeFromTimestamp(raw, timezone);
  }
  if (key === "daylight_duration" || key === "sunshine_duration") {
    return `${(raw / 3600).toFixed(1)} ${units.hours}`;
  }
  if (key.includes("temperature")) return raw.toFixed(1);
  if (key === "precipitation_sum" || key === "rain_sum") {
    return `${raw.toFixed(1)} ${units.mm}`;
  }
  if (key === "snowfall_sum") return `${raw.toFixed(1)} ${units.cm}`;
  if (key === "precipitation_hours") return `${raw.toFixed(1)} ${units.hours}`;
  if (key.includes("wind_speed") || key.includes("wind_gusts")) {
    return `${raw.toFixed(1)} ${units.kmh}`;
  }
  if (key.includes("direction")) return `${Math.round(raw)}° (${getWindDirectionLabel(raw)})`;
  if (key === "shortwave_radiation_sum") return `${raw.toFixed(1)} ${units.mj}`;
  if (key === "et0_fao_evapotranspiration") return `${raw.toFixed(2)} ${units.mm}`;
  return raw.toFixed(2);
}

function getParamLabel(key) {
  return I18N[currentLang].params[key] || key;
}

function formatShortDate(dateDisplay) {
  return dateDisplay.slice(0, 5);
}
