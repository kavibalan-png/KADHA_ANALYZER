// ---------- Sensor Values ----------
let values = {
  ph: null,
  tds: null,
  optical: null
};

// ---------- Fetch sensor data ----------
function fetchSensor(sensor) {
  fetch(`/get/${sensor}`)
    .then(res => res.json())
    .then(data => {
      const statusEl = document.getElementById(sensor + "_status");

      if (data.error) {
        statusEl.innerHTML = "❌ No data available";
        statusEl.className = "status-fail";
        values[sensor] = null;
      } else {
        values[sensor] = data.value;
        statusEl.innerHTML = "✔ " + data.value;
        statusEl.className = "status-ok";
      }

      checkFinish();
    })
    .catch(() => {
      const statusEl = document.getElementById(sensor + "_status");
      statusEl.innerHTML = "❌ Server error";
      statusEl.className = "status-fail";
      values[sensor] = null;
      checkFinish();
    });
}

// ---------- Enable Finish Button ----------
function checkFinish() {
  const finishBtn = document.getElementById("finishBtn");
  if (!finishBtn) return;

  if (values.ph !== null && values.tds !== null && values.optical !== null) {
    finishBtn.disabled = false;
  } else {
    finishBtn.disabled = true;
  }
}

// ---------- Save Data ----------
function finishCollect() {
  const herb = document.getElementById("herb").value.trim();
  const purityEl = document.querySelector("input[name='purity']:checked");

  if (!herb) {
    alert("Please enter herb name");
    return;
  }

  if (!purityEl) {
    alert("Please select purity");
    return;
  }

  fetch("/finish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      herb: herb,
      purity: purityEl.value,
      ph: values.ph,
      tds: values.tds,
      optical: values.optical
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === "saved") {
        alert("Data saved successfully 🌿");
        clearSensors();
        document.getElementById("herb").value = "";
      }
    })
    .catch(() => {
      alert("Error saving data. Try again.");
    });
}

// ---------- Prediction ----------
function predict() {
  if (values.ph === null || values.tds === null || values.optical === null) {
    alert("Collect all sensor values before prediction");
    return;
  }

  fetch("/predict_result", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(values)
  })
    .then(res => res.json())
    .then(data => {
      const resultEl = document.getElementById("result");
      resultEl.innerHTML = `
        <h3>Prediction Result 🌿</h3>
        <p><b>Herb:</b> ${data.herb}</p>
        <p><b>Purity:</b> ${data.purity}</p>
        <p><b>Confidence:</b> ${data.confidence}%</p>
      `;
    })
    .catch(() => {
      alert("Prediction failed. Make sure model is trained & sensors sent data.");
    });
}

// ---------- Clear / Reset ----------
function clearSensors() {
  values = { ph: null, tds: null, optical: null };

  ["ph", "tds", "optical"].forEach(sensor => {
    const el = document.getElementById(sensor + "_status");
    if (el) {
      el.innerHTML = "❌ Not collected";
      el.className = "status-fail";
    }
  });

  const finishBtn = document.getElementById("finishBtn");
  if (finishBtn) finishBtn.disabled = true;

  const resultEl = document.getElementById("result");
  if (resultEl) resultEl.innerHTML = "";
}
