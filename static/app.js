// app.js (Frontend)
async function getWeatherAdvice(weatherData) {
    try {
        // Doğrudan KENDİ backend'ine istek atıyorsun
        const res = await fetch('/get_recommendation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                weather: weatherData,
                time_of_day: 'sabah çıkışı'
            })
        });

        const data = await res.json();

        // Gelen veriyi arayüze bas
        console.log("Asistanın Tavsiyesi:", data.llm_text);
        console.log("Şemsiye Gerekli mi?", data.umbrella);

        // Ekranda ilgili HTML elementlerini güncelle
        // document.getElementById('advice-box').innerText = data.llm_text;

    } catch (error) {
        console.error("Bir hata oluştu:", error);
    }
}
// Butona tıklandığında asistanı çalıştıran tetikleyici
document.getElementById('adviceBtn').addEventListener('click', () => {
    // Burada normalde hava durumu servisinden gelen veri olur
    // Şimdilik test için elinle bir veri gönderelim:
    const testWeatherData = {
        temperature_c: 15.5,
        humidity_pct: 60,
        precipitation_mm: 0
    };

    getWeatherAdvice(testWeatherData);
});