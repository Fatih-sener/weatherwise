import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import json


def render_html_dashboard(data):
    video_files = {
        "rainy": "assets/rainy.mp4",
        "winter": "assets/winter.mp4",
        "sunny": "assets/sunny.mp4",
        "cloudy": "assets/cloudy.mp4"
    }

    encoded_videos = {}
    for key, path in video_files.items():
        try:
            with open(path, "rb") as f:
                encoded_videos[key] = base64.b64encode(f.read()).decode()
        except:
            encoded_videos[key] = ""

    video_json = json.dumps(encoded_videos)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { font-family: 'DM Sans', sans-serif; background: transparent; }

      @keyframes smoothEnter {
          0% { opacity: 0; transform: translateY(30px) scale(0.98); }
          100% { opacity: 1; transform: translateY(0) scale(1); }
      }

      .dash { 
          background: rgba(13, 17, 23, 0.65); 
          backdrop-filter: blur(15px); 
          border-radius: 20px; 
          padding: 24px; 
          color: white; 
          max-width: 1400px; 
          margin: 0 auto;
          position: relative; 
          z-index: 10;
          animation: smoothEnter 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
      }

      .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
      .top-bar h1 { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 700; color: #fff; }
      .top-bar p { font-size: 13px; color: #8b949e; margin-top: 4px; }

      .main-grid { display: grid; grid-template-columns: 300px minmax(400px, 1fr) 260px; gap: 20px; }

      .left-panel { display: flex; flex-direction: column; gap: 16px; }
      .hero-card { background: linear-gradient(145deg, #ff8c00, #ffb84d); border-radius: 18px; padding: 24px; position: relative; overflow: hidden; box-shadow: 0 10px 20px rgba(255,140,0,0.2); }
      .hero-card::before { content: ''; position: absolute; top: -40px; right: -40px; width: 140px; height: 140px; background: rgba(255,255,255,0.12); border-radius: 50%; }
      .hero-card .city-row { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
      .hero-card .city-row span { font-size: 13px; color: rgba(255,255,255,0.9); font-family: 'Syne',sans-serif; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
      .hero-card .dot { width: 8px; height: 8px; background: rgba(255,255,255,0.9); border-radius: 50%; box-shadow: 0 0 10px rgba(255,255,255,0.5); }
      .hero-card .temp { font-family: 'Syne', sans-serif; font-size: 56px; font-weight: 700; color: white; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
      .hero-card .desc { font-size: 15px; font-weight: 500; color: rgba(255,255,255,0.9); margin-top: 8px; }
      .hero-card .weather-icon { position: absolute; right: 20px; bottom: 15px; font-size: 64px; line-height: 1; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.2)); }

      .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
      .stat-card { background: rgba(22, 27, 34, 0.7); border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; justify-content: center; backdrop-filter: blur(5px);}
      .stat-card .label { font-size: 12px; color: #8b949e; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; font-weight: 500; }
      .stat-card .val { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: #fff; }
      .stat-card .sub { font-size: 11px; color: #8b949e; margin-top: 4px; }

      .mid-panel { display: flex; flex-direction: column; gap: 16px; }
      .weekly-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }

      .day-card { background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(5px); border-radius: 14px; padding: 14px 8px; text-align: center; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; transition: all 0.3s ease; }
      .day-card:hover { border-color: rgba(255,167,38,0.5); transform: translateY(-3px); }
      .day-card.active { border-color: #FFA726; background: rgba(255,167,38,0.1); box-shadow: 0 4px 12px rgba(255,167,38,0.15); }
      .day-card .day-name { font-size: 11px; color: #8b949e; font-weight: 600; text-transform: uppercase; }
      .day-card .day-icon { font-size: 24px; }
      .day-card .day-temp { font-size: 14px; font-weight: 700; color: #fff; font-family: 'Syne', sans-serif; }

      .chart-area { background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(5px); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; }
      .chart-area h3 { font-size: 14px; font-weight: 600; color: #8b949e; margin-bottom: 16px; font-family: 'Syne', sans-serif; text-transform: uppercase; letter-spacing: 0.5px; }
      .chart-wrap { position: relative; height: 200px; width: 100%; flex-grow: 1; }

      .aqi-card { background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(5px); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); }
      .aqi-card h4 { font-size: 13px; color: #8b949e; margin-bottom: 16px; font-family: 'Syne', sans-serif; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
      .aqi-content { display: flex; align-items: center; gap: 24px; }
      .aqi-donut-wrap { display: flex; align-items: center; gap: 16px; width: 40%; }
      .aqi-vals { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; flex-grow: 1; }
      .aqi-val { display: flex; align-items: center; gap: 8px; }
      .aqi-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
      .aqi-name { font-size: 11px; color: #8b949e; font-weight: 500;}
      .aqi-num { font-size: 13px; font-weight: 700; color: #fff; margin-left: auto; font-family: 'Syne', sans-serif;}

      .right-panel { display: flex; flex-direction: column; gap: 16px; }

      .sun-card { background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(5px); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); }
      .sun-card h4 { font-size: 13px; color: #8b949e; margin-bottom: 16px; font-family: 'Syne', sans-serif; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
      .sun-row { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
      .sun-row:last-child { margin-bottom: 0; }
      .sun-icon-wrap { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
      .sun-icon-wrap.rise { background: rgba(255,193,7,0.1); border: 1px solid rgba(255,193,7,0.2); }
      .sun-icon-wrap.set { background: rgba(100,181,246,0.1); border: 1px solid rgba(100,181,246,0.2); }
      .sun-label { font-size: 11px; color: #8b949e; margin-bottom: 2px;}
      .sun-time { font-size: 16px; font-weight: 700; color: #fff; font-family: 'Syne', sans-serif; }

      .avatar-card { background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(5px); border-radius: 16px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 160px; gap: 10px; }

      .rain-card { background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(5px); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); flex-grow: 1; }
      .rain-card h4 { font-size: 13px; color: #8b949e; margin-bottom: 16px; font-family: 'Syne', sans-serif; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
      .rain-row { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
      .rain-row:last-child { margin-bottom: 0; }
      .rain-day { font-size: 12px; color: #8b949e; width: 30px; font-weight: 500;}
      .rain-bar-bg { flex: 1; height: 6px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden; }
      .rain-bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #378add, #85b7eb); }
      .rain-pct { font-size: 12px; color: #fff; width: 35px; text-align: right; font-weight: 600; font-family: 'Syne', sans-serif;}
    </style>
    </head>
    <body>
    <div class="dash">
      <div class="top-bar">
        <div>
          <h1>WeatherWise Dashboard</h1>
          <p>Real-time meteorological analysis panel</p>
        </div>
      </div>

      <div class="main-grid">
        <div class="left-panel">
          <div class="hero-card">
            <div class="city-row">
              <div class="dot"></div>
              <span>[[CITY]]</span>
              <span style="color:rgba(255,255,255,0.5);font-size:10px;text-transform:none;letter-spacing:0;">• Live Data</span>
            </div>
            <div class="temp">[[TEMP]]°C</div>
            <div class="desc">[[DESC]]</div>
            <div class="weather-icon">[[ICON]]</div>
          </div>

          <div class="stat-grid">
            <div class="stat-card">
              <div class="label">💧 Humidity</div>
              <div class="val">[[HUM]]%</div>
            </div>
            <div class="stat-card">
              <div class="label">💨 Wind</div>
              <div class="val">[[WIND]]</div>
              <div class="sub">km/h</div>
            </div>
            <div class="stat-card">
              <div class="label">👁 Visibility</div>
              <div class="val">[[VIS]]</div>
              <div class="sub">km</div>
            </div>
            <div class="stat-card">
              <div class="label">📊 Pressure</div>
              <div class="val">[[PRESS]]</div>
              <div class="sub">hPa</div>
            </div>
          </div>

          <div class="sun-card">
            <h4>Sunrise & Sunset</h4>
            <div class="sun-row">
              <div class="sun-icon-wrap rise">🌅</div>
              <div><div class="sun-label">Sunrise</div><div class="sun-time">[[SUNRISE]]</div></div>
            </div>
            <div class="sun-row">
              <div class="sun-icon-wrap set">🌇</div>
              <div><div class="sun-label">Sunset</div><div class="sun-time">[[SUNSET]]</div></div>
            </div>
          </div>
        </div>

        <div class="mid-panel">
          <div class="weekly-row">
            [[WEEKLY_CARDS]]
          </div>

          <div class="chart-area">
            <h3><span id="chartTitle">Today</span> — Hourly Analysis</h3>
            <div class="chart-wrap">
              <canvas id="forecastChart"></canvas>
            </div>
            <div style="display:flex;justify-content:center;gap:24px;margin-top:16px;font-size:12px;color:#8b949e;font-weight:500;">
              <span style="display:flex;align-items:center;gap:6px;"><span style="width:16px;height:16px;background:rgba(255,167,38,0.2);border:2px solid #FFA726;border-radius:4px;display:inline-block;"></span>Temperature</span>
              <span style="display:flex;align-items:center;gap:6px;"><span style="width:16px;height:4px;background:#29B6F6;display:inline-block;border-top:2px dashed #29B6F6;height:0;"></span>Nem</span>
              <span style="display:flex;align-items:center;gap:6px;"><span style="width:16px;height:4px;background:#66BB6A;display:inline-block;"></span>Rüzgar</span>
            </div>
          </div>

          <div class="aqi-card">
            <h4>Air Quality</h4>
            <div class="aqi-content">
                <div class="aqi-donut-wrap">
                  <canvas id="aqiChart" width="80" height="80"></canvas>
                  <div>
                    <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:700;color:#fff;">[[AQI_VAL]]</div>
                    <div style="font-size:13px;color:[[AQI_COLOR]];font-weight:600;text-transform:uppercase;letter-spacing:1px;">[[AQI_DESC]]</div>
                  </div>
                </div>
                <div class="aqi-vals">
                  <div class="aqi-val"><div class="aqi-dot" style="background:#EF9F27;"></div><span class="aqi-name">PM10</span><span class="aqi-num">[[PM10]]</span></div>
                  <div class="aqi-val"><div class="aqi-dot" style="background:#E24B4A;"></div><span class="aqi-name">O3</span><span class="aqi-num">[[O3]]</span></div>
                  <div class="aqi-val"><div class="aqi-dot" style="background:#378add;"></div><span class="aqi-name">SO2</span><span class="aqi-num">[[SO2]]</span></div>
                  <div class="aqi-val"><div class="aqi-dot" style="background:#1D9E75;"></div><span class="aqi-name">PM2.5</span><span class="aqi-num">[[PM25]]</span></div>
                  <div class="aqi-val"><div class="aqi-dot" style="background:#8b949e;"></div><span class="aqi-name">CO</span><span class="aqi-num">[[CO]]</span></div>
                  <div class="aqi-val"><div class="aqi-dot" style="background:#7F77DD;"></div><span class="aqi-name">NO2</span><span class="aqi-num">[[NO2]]</span></div>
                </div>
            </div>
          </div>
        </div>

        <div class="right-panel">
          <div class="avatar-card">
            <video id="asistanVideo" width="100%" autoplay loop muted playsinline style="border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); display: none;">
                <source src="" type="video/mp4">
            </video>
            <div id="robotFallback" style="font-size: 50px; opacity: 0.6;">🤖</div>
            <div style="font-size: 11px; color: #8b949e; font-weight: 600; text-transform: uppercase;">WeatherWise Assistant</div>
          </div>

          <div class="rain-card">
            <h4>Precipitation Chance</h4>
            [[RAIN_ROWS]]
          </div>
        </div>
      </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const allLabels = [[CHART_LABELS]];
    const allTemps = [[CHART_TEMPS]];
    const allHum = [[CHART_HUM]];
    const allWind = [[CHART_WIND]];
    const weeklyConditions = [[WEEKLY_CONDITIONS]];
    const encodedVideos = [[VIDEO_JSON]];

    const bgImages = {
        "clear":         "https://images.unsplash.com/photo-1506466010722-395aa2bef877?auto=format&fit=crop&w=1920&q=80",
        "sunny":         "https://images.unsplash.com/photo-1506466010722-395aa2bef877?auto=format&fit=crop&w=1920&q=80",
        "partly_cloudy": "https://images.unsplash.com/photo-1499346030926-9a72daac6c63?auto=format&fit=crop&w=1920&q=80",
        "cloudy":        "https://images.unsplash.com/photo-1499346030926-9a72daac6c63?auto=format&fit=crop&w=1920&q=80",
        "overcast":      "https://images.unsplash.com/photo-1499346030926-9a72daac6c63?auto=format&fit=crop&w=1920&q=80",
        "fog":           "https://images.unsplash.com/photo-1487621167305-5d248087c724?auto=format&fit=crop&w=1920&q=80",
        "drizzle":       "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?auto=format&fit=crop&w=1920&q=80",
        "rain":          "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?auto=format&fit=crop&w=1920&q=80",
        "heavy_rain":    "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?auto=format&fit=crop&w=1920&q=80",
        "thunderstorm":  "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?auto=format&fit=crop&w=1920&q=80",
        "snow":          "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?auto=format&fit=crop&w=1920&q=80",
        "blizzard":      "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?auto=format&fit=crop&w=1920&q=80",
        "hail":          "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?auto=format&fit=crop&w=1920&q=80",
        "sleet":         "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?auto=format&fit=crop&w=1920&q=80",
    };

    let chartInstance = null;

    function selectDay(dayIndex, element, dayName) {
        document.querySelectorAll('.day-card').forEach(card => card.classList.remove('active'));
        if(element) element.classList.add('active');
        document.getElementById('chartTitle').innerText = dayIndex === 0 ? "Today" : dayName;

        const start = dayIndex * 24;
        const end = start + 24;

        if (chartInstance && start < allLabels.length) {
            chartInstance.data.labels = allLabels.slice(start, end);
            chartInstance.data.datasets[0].data = allTemps.slice(start, end);
            chartInstance.data.datasets[1].data = allHum.slice(start, end);
            chartInstance.data.datasets[2].data = allWind.slice(start, end);
            chartInstance.update();
        }

        updateAvatar(dayIndex);

        try {
            const condKey = (weeklyConditions[dayIndex] || "clear").toLowerCase();
            const bgUrl = bgImages[condKey] || bgImages["clear"];
            const stApp = window.parent.document.querySelector('.stApp');

            let bgContainer = window.parent.document.getElementById('weather-bg-container');
            if (!bgContainer) {
                bgContainer = window.parent.document.createElement('div');
                bgContainer.id = 'weather-bg-container';
                bgContainer.style.position = 'fixed';
                bgContainer.style.top = '0';
                bgContainer.style.left = '0';
                bgContainer.style.width = '100vw';
                bgContainer.style.height = '100vh';
                bgContainer.style.zIndex = '0'; 
                stApp.insertBefore(bgContainer, stApp.firstChild);
            }

            const newLayer = window.parent.document.createElement('div');
            newLayer.style.position = 'absolute';
            newLayer.style.top = '0';
            newLayer.style.left = '0';
            newLayer.style.width = '100%';
            newLayer.style.height = '100%';
            newLayer.style.backgroundImage = `linear-gradient(rgba(13, 17, 23, 0.4), rgba(13, 17, 23, 0.7)), url("${bgUrl}")`;
            newLayer.style.backgroundSize = 'cover';
            newLayer.style.backgroundPosition = 'center';
            newLayer.style.opacity = '0';
            newLayer.style.transition = 'opacity 1.5s ease-in-out';

            bgContainer.appendChild(newLayer);
            setTimeout(() => { newLayer.style.opacity = '1'; }, 50);
            setTimeout(() => {
                while (bgContainer.children.length > 1) {
                    bgContainer.removeChild(bgContainer.firstChild);
                }
            }, 1600);

        } catch(e) {
            console.log("Arka plan değişimi için üst çerçeveye erişilemedi.");
        }
    }

    function updateAvatar(dayIndex) {
        const cond = (weeklyConditions[dayIndex] || "clear").toLowerCase();
        const temp = allTemps[dayIndex * 24];
        let videoKey = "sunny";

        if (["rain", "drizzle", "heavy_rain", "thunderstorm"].includes(cond)) {
            videoKey = "rainy";
        } else if (["snow", "blizzard", "hail", "sleet"].includes(cond) || temp < 8) {
            videoKey = "winter";
        } else if (["cloudy", "overcast", "partly_cloudy", "fog"].includes(cond) || (temp >= 8 && temp < 18)) {
            videoKey = "cloudy";
        }

        const videoBase64 = encodedVideos[videoKey];
        const videoElement = document.getElementById('asistanVideo');
        const fallback = document.getElementById('robotFallback');

        if (videoBase64) {
            videoElement.src = "data:video/mp4;base64," + videoBase64;
            videoElement.style.display = "block";
            fallback.style.display = "none";
            videoElement.load();
            videoElement.play();
        } else {
            videoElement.style.display = "none";
            fallback.style.display = "block";
        }
    }

    chartInstance = new Chart(document.getElementById('forecastChart'), {
      type: 'line',
      data: {
        labels: [], 
        datasets: [
          { label: 'Temperature', data: [], borderColor: '#FFA726', backgroundColor: 'rgba(255,167,38,0.1)', borderWidth: 3, tension: 0.4, fill: true, pointRadius: 0, pointHoverRadius: 6, pointHoverBackgroundColor: '#FFA726' },
          { label: 'Humidity',      data: [], borderColor: '#29B6F6', borderWidth: 2, borderDash: [5,4], tension: 0.4, fill: false, pointRadius: 0, pointHoverRadius: 5, pointHoverBackgroundColor: '#29B6F6' },
          { label: 'Wind',   data: [], borderColor: '#66BB6A', borderWidth: 2, tension: 0.4, fill: false, pointRadius: 0, pointHoverRadius: 5, pointHoverBackgroundColor: '#66BB6A' }
        ]
      },
      options: { 
          responsive: true, 
          maintainAspectRatio: false,
          interaction: { mode: 'index', axis: 'x', intersect: false },
          plugins: { 
              legend: { display: false },
              tooltip: { 
                  mode: 'index',
                  intersect: false,
                  backgroundColor: 'rgba(13,17,23,0.92)',
                  titleColor: '#fff',
                  titleFont: { family: 'Syne', size: 13, weight: '600' },
                  bodyColor: '#ccc',
                  bodyFont: { family: 'DM Sans', size: 12 },
                  borderColor: 'rgba(255,255,255,0.1)',
                  borderWidth: 1,
                  padding: 12,
                  callbacks: {
                      label: function(context) {
                          const label = context.dataset.label;
                          const val = context.parsed.y;
                          if (label === 'Temperature') return '  Temperature: ' + val + '°C';
                          if (label === 'Humidity')      return '  Humidity: ' + val + '%';
                          if (label === 'Wind')   return '  Rüzgar: ' + val + ' km/h';
                          return label + ': ' + val;
                      }
                  }
              }
          },
          scales: { 
              x: { grid: { display: false }, ticks: { color: '#8b949e', font: { family: 'Syne' } } }, 
              y: { display: false, grid: { display: false } } 
          }
      }
    });

    selectDay(0, document.querySelector('.day-card'), 'Today');

    const aqiCtx = document.getElementById('aqiChart').getContext('2d');
    new Chart(aqiCtx, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [[[AQI_VAL]], 100 - [[AQI_VAL]]],
          backgroundColor: ['[[AQI_COLOR]]', 'rgba(255,255,255,0.05)'],
          borderWidth: 0,
          cutout: '75%'
        }]
      },
      options: { responsive: false, plugins: { legend: { display: false }, tooltip: { enabled: false } } }
    });
    </script>
    </body>
    </html>
    """

    weekly_cards_html = ""
    for i in range(7):
        weekly_cards_html += f"""
        <div class="day-card" onclick="selectDay({i}, this, '{data['weekly_days'][i]}')">
          <div class="day-name">{data['weekly_days'][i]}</div>
          <div class="day-icon">{data['weekly_icons'][i]}</div>
          <div class="day-temp">{data['weekly_temps'][i]}°C</div>
        </div>
        """

    rain_rows_html = ""
    for i in range(7):
        prob = data['rain_probs'][i]
        rain_rows_html += f"""
        <div class="rain-row"><span class="rain-day">{data['weekly_days'][i]}</span><div class="rain-bar-bg"><div class="rain-bar-fill" style="width:{prob}%;"></div></div><span class="rain-pct">{prob}%</span></div>
        """

    final_html = html_template.replace("[[CITY]]", str(data["city"]))
    final_html = final_html.replace("[[TEMP]]", str(data["temp"]))
    final_html = final_html.replace("[[DESC]]", str(data["desc"]))
    final_html = final_html.replace("[[ICON]]", str(data["icon"]))
    final_html = final_html.replace("[[HUM]]", str(data["hum"]))
    final_html = final_html.replace("[[WIND]]", str(data["wind"]))
    final_html = final_html.replace("[[VIS]]", str(data["vis"]))
    final_html = final_html.replace("[[PRESS]]", str(data["press"]))
    final_html = final_html.replace("[[SUNRISE]]", str(data["sunrise"]))
    final_html = final_html.replace("[[SUNSET]]", str(data["sunset"]))
    final_html = final_html.replace("[[WEEKLY_CARDS]]", weekly_cards_html)
    final_html = final_html.replace("[[RAIN_ROWS]]", rain_rows_html)
    final_html = final_html.replace("[[CHART_LABELS]]", json.dumps(data["chart_labels"]))
    final_html = final_html.replace("[[CHART_TEMPS]]", json.dumps(data["chart_temps"]))
    final_html = final_html.replace("[[CHART_HUM]]", json.dumps(data["chart_hum"]))
    final_html = final_html.replace("[[CHART_WIND]]", json.dumps(data["chart_wind"]))
    final_html = final_html.replace("[[AQI_VAL]]", str(data["aqi_val"]))
    final_html = final_html.replace("[[AQI_DESC]]", str(data["aqi_desc"]))
    final_html = final_html.replace("[[AQI_COLOR]]", str(data["aqi_color"]))
    final_html = final_html.replace("[[PM10]]", str(data["pm10"]))
    final_html = final_html.replace("[[O3]]", str(data["o3"]))
    final_html = final_html.replace("[[SO2]]", str(data["so2"]))
    final_html = final_html.replace("[[PM25]]", str(data["pm25"]))
    final_html = final_html.replace("[[CO]]", str(data["co"]))
    final_html = final_html.replace("[[NO2]]", str(data["no2"]))
    final_html = final_html.replace("[[WEEKLY_CONDITIONS]]", json.dumps(data["weekly_conditions"]))
    final_html = final_html.replace("[[VIDEO_JSON]]", video_json)

    components.html(final_html, height=880, scrolling=False)