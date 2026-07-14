const periodEl = document.getElementById("period");
const lastKnownDateEl = document.getElementById("last-known-date");
const loaderEl = document.getElementById("loader");
const errorEl = document.getElementById("error");
const dayTabsEl = document.getElementById("day-tabs");
const forecastPanelEl = document.getElementById("forecast-panel");
const weekOverviewEl = document.getElementById("week-overview");
const dayTabTemplate = document.getElementById("day-tab-template");
const panelTemplate = document.getElementById("forecast-panel-template");

let forecastData = null;
let activeDayIndex = 0;

function showLoader(show) {
  loaderEl.classList.toggle("hidden", !show);
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.classList.remove("hidden");
  dayTabsEl.classList.add("hidden");
  forecastPanelEl.classList.add("hidden");
  weekOverviewEl.classList.add("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}

function renderWeekOverview(days) {
  const units = I18N[currentLang].units;
  const temps = days.map((day) => day.summary.temperature_mean);
  const minTemp = Math.min(...days.map((day) => day.summary.temperature_min));
  const maxTemp = Math.max(...days.map((day) => day.summary.temperature_max));
  const totalPrecip = days.reduce((sum, day) => sum + day.summary.precipitation_sum, 0);

  weekOverviewEl.innerHTML = `
    <div class="overview-card">
      <span>${t("avgTempWeek")}</span>
      <strong>${(temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1)}°C</strong>
    </div>
    <div class="overview-card">
      <span>${t("tempRangeWeek")}</span>
      <strong>${minTemp.toFixed(1)}° … ${maxTemp.toFixed(1)}°</strong>
    </div>
    <div class="overview-card">
      <span>${t("weeklyPrecip")}</span>
      <strong>${totalPrecip.toFixed(1)} ${units.mm}</strong>
    </div>
  `;
  weekOverviewEl.classList.remove("hidden");
}

function renderDayTabs(days) {
  dayTabsEl.innerHTML = "";
  days.forEach((day, index) => {
    const node = dayTabTemplate.content.cloneNode(true);
    const button = node.querySelector(".day-tab");
    button.dataset.index = String(index);
    button.querySelector(".day-tab__weekday").textContent = getWeekdayLabel(day.weekday, true);
    button.querySelector(".day-tab__date").textContent = formatShortDate(day.date_display);
    button.querySelector(".day-tab__icon").textContent = day.weather_icon;
    if (index === activeDayIndex) button.classList.add("day-tab--active");
    button.addEventListener("click", () => selectDay(index));
    dayTabsEl.appendChild(node);
  });
  dayTabsEl.classList.remove("hidden");
}

function buildQuickStats(day, timezone) {
  const summary = day.summary;
  const units = I18N[currentLang].units;

  return [
    { icon: "💧", label: t("precip"), value: `${summary.precipitation_sum} ${units.mm}` },
    { icon: "💨", label: t("wind"), value: `${summary.wind_speed_max} ${units.kmh}` },
    { icon: "🌬️", label: t("gusts"), value: `${summary.wind_gusts_max} ${units.kmh}` },
    {
      icon: "🧭",
      label: t("direction"),
      value: getWindDirectionLabel(summary.wind_direction),
    },
    {
      icon: "🌅",
      label: t("sunrise"),
      value: formatTimeFromTimestamp(summary.sunrise, timezone),
    },
    {
      icon: "🌇",
      label: t("sunset"),
      value: formatTimeFromTimestamp(summary.sunset, timezone),
    },
  ];
}

function renderDetailGroups(container, day, timezone) {
  container.innerHTML = "";
  const detailsMap = Object.fromEntries(day.details.map((item) => [item.key, item]));

  Object.entries(DETAIL_GROUP_KEYS).forEach(([groupKey, keys]) => {
    const items = keys.map((key) => detailsMap[key]).filter(Boolean);
    if (!items.length) return;

    const group = document.createElement("section");
    group.className = "detail-group";
    group.innerHTML = `<h3>${t(`groups.${groupKey}`)}</h3>`;

    const list = document.createElement("ul");
    items.forEach((item) => {
      if (item.key === "weather_code") return;
      const li = document.createElement("li");
      const label = getParamLabel(item.key).replace(/,.*$/, "");
      const value = formatParamValue(item.key, item.raw, timezone);
      li.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
      list.appendChild(li);
    });

    group.appendChild(list);
    container.appendChild(group);
  });
}

function renderForecastPanel(day) {
  const timezone = forecastData.timezone;
  const node = panelTemplate.content.cloneNode(true);
  const summary = day.summary;
  const tempRange = Math.max(summary.temperature_max - summary.temperature_min, 1);

  node.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });

  node.querySelector(".panel__icon").textContent = day.weather_icon;
  node.querySelector(".panel__weekday").textContent = getWeekdayLabel(day.weekday);
  node.querySelector(".panel__date").textContent = day.date_display;
  node.querySelector(".panel__condition").textContent = getWeatherLabel(day.weather_code);
  node.querySelector(".panel__temp-value").textContent = summary.temperature_mean.toFixed(1);
  node.querySelector(".panel__temp-max").textContent = `${summary.temperature_max.toFixed(1)}°`;
  node.querySelector(".panel__temp-min").textContent = `${summary.temperature_min.toFixed(1)}°`;

  const meanPosition = ((summary.temperature_mean - summary.temperature_min) / tempRange) * 100;
  node.querySelector(".range-bar__marker").style.left = `${Math.min(100, Math.max(0, meanPosition))}%`;

  const quickStats = node.querySelector(".quick-stats");
  buildQuickStats(day, timezone).forEach((stat) => {
    const card = document.createElement("div");
    card.className = "quick-stat";
    card.innerHTML = `
      <span class="quick-stat__icon">${stat.icon}</span>
      <div>
        <span class="quick-stat__label">${stat.label}</span>
        <strong class="quick-stat__value">${stat.value}</strong>
      </div>
    `;
    quickStats.appendChild(card);
  });

  renderDetailGroups(node.querySelector(".details__groups"), day, timezone);

  forecastPanelEl.innerHTML = "";
  forecastPanelEl.appendChild(node);
  forecastPanelEl.classList.remove("hidden");
}

function selectDay(index) {
  if (!forecastData) return;
  activeDayIndex = index;
  renderDayTabs(forecastData.days);
  renderForecastPanel(forecastData.days[index]);
}

function renderForecast() {
  if (!forecastData) return;
  periodEl.textContent = forecastData.period_display;
  lastKnownDateEl.textContent = forecastData.last_known_date_display;
  renderWeekOverview(forecastData.days);
  selectDay(activeDayIndex);
}

async function loadForecast() {
  showLoader(true);
  hideError();
  periodEl.textContent = t("loading");

  try {
    const response = await fetch("/api/forecast");
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || t("forecastError"));
    }

    forecastData = data;
    renderForecast();
  } catch (error) {
    showError(error.message);
  } finally {
    showLoader(false);
  }
}

document.querySelectorAll(".lang-switch__btn").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
});

window.onLanguageChange = () => {
  if (forecastData) {
    renderForecast();
  } else {
    periodEl.textContent = t("loading");
  }
};

setLanguage(currentLang);
loadForecast();
