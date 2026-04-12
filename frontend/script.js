const API_BASE_URL = "http://127.0.0.1:8000";

const form = document.getElementById("analyze-form");
const output = document.getElementById("output");
const loadResultsButton = document.getElementById("load-results");
const uploadButton = document.getElementById("upload-button");
const historyContainer = document.getElementById("history");

function printJson(data) {
  output.textContent = JSON.stringify(data, null, 2);
}

function renderHistory(items) {
  if (!items || !items.length) {
    historyContainer.innerHTML = "";
    return;
  }

  historyContainer.innerHTML = items
    .map((item) => {
      const labels = (item.labels || []).join(", ");
      const imageUrl = item.image_url
        ? `<p><strong>Image URL:</strong> <a href="${item.image_url}" target="_blank" rel="noreferrer">${item.image_url}</a></p>`
        : "";

      return `
        <article class="history-card">
          <h3>${item.image_name || "Unnamed item"}</h3>
          <p><strong>Record ID:</strong> ${item.record_id || "-"}</p>
          <p><strong>Created:</strong> ${item.created_at || "-"}</p>
          <p><strong>Labels:</strong> ${labels || "-"}</p>
          ${imageUrl}
        </article>
      `;
    })
    .join("");
}

async function callApi(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.Message || "Request failed");
  }

  return data;
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result);
      const base64 = result.includes(",") ? result.split(",")[1] : result;
      resolve(base64);
    };
    reader.onerror = () => reject(new Error("Failed to read the file."));
    reader.readAsDataURL(file);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const imageName = document.getElementById("image_name").value.trim();

  if (!imageName) {
    printJson({ error: "Please type an image name before using Analyze by Name." });
    return;
  }

  printJson({ status: "Loading..." });

  try {
    const data = await callApi("/analyze", {
      method: "POST",
      body: JSON.stringify({ image_name: imageName }),
    });
    printJson(data);
  } catch (error) {
    printJson({ error: error.message });
  }
});

loadResultsButton.addEventListener("click", async () => {
  printJson({ status: "Loading history..." });
  try {
    const data = await callApi("/results");
    printJson(data);
    renderHistory(data.items || []);
  } catch (error) {
    printJson({ error: error.message });
  }
});

uploadButton.addEventListener("click", async () => {
  const fileInput = document.getElementById("image_file");
  const textInput = document.getElementById("image_name");
  const file = fileInput.files[0];

  if (!file) {
    printJson({ error: "Please choose a JPG or PNG file first." });
    return;
  }

  const imageName = textInput.value.trim() || file.name;
  textInput.value = imageName;
  printJson({ status: "Uploading file..." });

  try {
    const imageBase64 = await fileToBase64(file);
    const data = await callApi("/upload", {
      method: "POST",
      body: JSON.stringify({
        image_name: imageName,
        image_base64: imageBase64,
      }),
    });
    printJson(data);
    const history = await callApi("/results");
    renderHistory(history.items || []);
  } catch (error) {
    printJson({ error: error.message });
  }
});
