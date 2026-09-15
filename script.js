let values = { ph: null, tds: null, optical: null };

function fetchSensor(sensor) {
  fetch(`/get/${sensor}`)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        document.getElementById(sensor+"_status").innerHTML =
          "<span class='status-fail'>❌ No data available</span>";
      } else {
        values[sensor] = data.value;
        document.getElementById(sensor+"_status").innerHTML =
          `<span class='status-ok'>✔ ${data.value}</span>`;
        checkFinish();
      }
    });
}

function checkFinish() {
  if (values.ph && values.tds && values.optical) {
    document.getElementById("finishBtn").disabled = false;
  }
}

function finishCollect() {
  fetch("/finish", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      herb: document.getElementById("herb").value,
      purity: document.querySelector("input[name='purity']:checked").value,
      ...values
    })
  }).then(() => alert("Data stored successfully 🌿"));
}
