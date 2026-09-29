/* PocketSmart AI - Client-Side Interactive JavaScript */

document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("form.ai-planner-form");
  const loadingOverlay = document.getElementById("loadingOverlay");

  forms.forEach(form => {
    form.addEventListener("submit", () => {
      if (loadingOverlay) {
        loadingOverlay.style.display = "flex";
      }
    });
  });

  const imageInput = document.getElementById("outfit_image");
  const imagePreview = document.getElementById("imagePreview");
  const previewImg = document.getElementById("previewImg");

  if (imageInput && imagePreview && previewImg) {
    imageInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        if (file.size > 5 * 1024 * 1024) {
          alert("File size exceeds 5MB limit. Please select a smaller photo.");
          imageInput.value = "";
          imagePreview.style.display = "none";
          return;
        }
        const reader = new FileReader();
        reader.onload = (event) => {
          previewImg.src = event.target.result;
          imagePreview.style.display = "block";
        };
        reader.readAsDataURL(file);
      } else {
        imagePreview.style.display = "none";
      }
    });
  }

  const addItemBtn = document.getElementById("addItemBtn");
  const itemsContainer = document.getElementById("dynamicItemsContainer");

  if (addItemBtn && itemsContainer) {
    addItemBtn.addEventListener("click", () => {
      const row = document.createElement("div");
      row.className = "item-row form-group";
      row.style.display = "flex";
      row.style.gap = "0.75rem";
      row.style.alignItems = "center";
      row.style.marginBottom = "0.75rem";

      row.innerHTML = `
        <select class="form-control room-select" style="flex: 1;">
          <option value="Living Room">Living Room</option>
          <option value="Bedroom">Bedroom</option>
          <option value="Kitchen">Kitchen</option>
          <option value="Bathroom">Bathroom</option>
          <option value="Dining Area">Dining Area</option>
        </select>
        <input type="text" class="form-control item-input" placeholder="Item name (e.g. Lamp, Table)" style="flex: 2;">
        <input type="number" class="form-control qty-input" value="1" min="1" max="20" style="width: 80px;">
        <button type="button" class="btn btn-outline btn-sm remove-row-btn" style="color: #f87171;">✕</button>
      `;

      itemsContainer.appendChild(row);

      row.querySelector(".remove-row-btn").addEventListener("click", () => {
        row.remove();
        syncHomeItemsJson();
      });

      row.querySelectorAll("input, select").forEach(el => {
        el.addEventListener("input", syncHomeItemsJson);
      });

      syncHomeItemsJson();
    });
  }
});

function syncHomeItemsJson() {
  const hiddenInput = document.getElementById("items_json");
  if (!hiddenInput) return;

  const rows = document.querySelectorAll("#dynamicItemsContainer .item-row");
  const items = [];

  rows.forEach(row => {
    const room = row.querySelector(".room-select")?.value || "Living Room";
    const item = row.querySelector(".item-input")?.value || "Decor Item";
    const qty = parseInt(row.querySelector(".qty-input")?.value || "1", 10);
    if (item.trim()) {
      items.push({ room, item: item.trim(), qty });
    }
  });

  hiddenInput.value = JSON.stringify(items);
}

function shareRecommendation() {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(window.location.href);
    alert("Recommendation link copied to clipboard!");
  }
}
