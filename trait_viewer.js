"use strict";

const elements = {
  layout: document.getElementById("layout"),
  spriteSearch: document.getElementById("spriteSearch"),
  spriteList: document.getElementById("spriteList"),
  toggleSidebar: document.getElementById("toggleSidebar"),
  spriteTitle: document.getElementById("spriteTitle"),
  stats: document.getElementById("stats"),
  categoryFilter: document.getElementById("categoryFilter"),
  componentSelect: document.getElementById("componentSelect"),
  hoverToggle: document.getElementById("hoverToggle"),
  traitBody: document.getElementById("traitBody"),
  previewWrapper: document.getElementById("previewWrapper"),
  previewImage: document.getElementById("spritePreview"),
  highlightCanvas: document.getElementById("highlightCanvas"),
  copyMaskButton: document.getElementById("copyMaskButton"),
  pixelMaskOutput: document.getElementById("pixelMaskOutput"),
};

const highlightCtx = elements.highlightCanvas.getContext("2d");

const state = {
  spriteIds: [],
  spriteMap: new Map(),
  spriteFilterText: "",
  currentTraits: [],
  currentRows: [],
  currentMaskString: "",
  currentMasks: [],
  selectedSpriteId: null,
  selectedTraitIndex: null,
  selectedComponentIndex: -1,
  hoverPreview: true,
};

initViewer().catch((error) => {
  showError(`Failed to initialise viewer: ${error.message}`);
});

async function initViewer() {
  const rawData = await fetchTraitData();
  buildSpriteMap(rawData);
  renderSpriteList();
  populateCategoryFilter(rawData);
  attachEventListeners();
  if (state.spriteIds.length) {
    selectSprite(state.spriteIds[0]);
  }
}

async function fetchTraitData() {
  const response = await fetch("data/trait_suggestions.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to fetch data (${response.status})`);
  }
  const data = await response.json();
  return data.map(normaliseTrait);
}

function normaliseTrait(item) {
  const coverage = typeof item.coverage_pct === "number" ? item.coverage_pct : Number(item.coverage_pct || 0);
  const pixelMask = item.pixel_mask || "";
  const pixels = parsePixelMask(pixelMask);
  return {
    sprite_id: item.sprite_id,
    category: item.category,
    variant_hint: item.variant_hint,
    color_hex: item.color_hex,
    color_name: item.color_name,
    coverage_pct: coverage,
    notes: item.notes || "",
    pixel_mask: pixelMask,
    pixels,
    components: null,
  };
}

function parsePixelMask(mask) {
  if (!mask) {
    return [];
  }
  return mask
    .split(";")
    .map((pair) => {
      const [row, col] = pair.split(",").map((value) => Number(value));
      if (Number.isNaN(row) || Number.isNaN(col)) {
        return null;
      }
      return { row, col };
    })
    .filter(Boolean);
}

function buildSpriteMap(data) {
  const map = new Map();
  for (const trait of data) {
    if (!map.has(trait.sprite_id)) {
      map.set(trait.sprite_id, []);
    }
    map.get(trait.sprite_id).push(trait);
  }
  for (const traits of map.values()) {
    traits.sort((a, b) => a.category.localeCompare(b.category));
  }
  state.spriteMap = map;
  state.spriteIds = Array.from(map.keys()).sort();
}

function attachEventListeners() {
  elements.spriteSearch.addEventListener("input", (event) => {
    renderSpriteList(event.target.value.trim().toLowerCase());
  });

  elements.toggleSidebar.addEventListener("click", () => {
    const collapsed = elements.layout.classList.toggle("collapsed-aside");
    elements.toggleSidebar.setAttribute("aria-pressed", collapsed ? "true" : "false");
  });

  elements.categoryFilter.addEventListener("change", () => {
    renderTraits();
  });

  elements.componentSelect.addEventListener("change", () => {
    state.selectedComponentIndex = Number(elements.componentSelect.value);
    if (state.selectedTraitIndex !== null) {
      const trait = state.currentTraits[state.selectedTraitIndex];
      highlightTrait(trait, state.selectedComponentIndex);
    }
  });

  elements.hoverToggle.addEventListener("change", (event) => {
    state.hoverPreview = event.target.checked;
    if (!state.hoverPreview && state.selectedTraitIndex !== null) {
      const trait = state.currentTraits[state.selectedTraitIndex];
      highlightTrait(trait, state.selectedComponentIndex);
    }
  });

  elements.previewImage.addEventListener("load", () => {
    elements.previewImage.hidden = false;
    if (state.selectedTraitIndex !== null) {
      const trait = state.currentTraits[state.selectedTraitIndex];
      highlightTrait(trait, state.selectedComponentIndex);
    } else {
      clearHighlight();
    }
  });

  elements.previewWrapper.addEventListener("click", handlePreviewClick);

  elements.copyMaskButton.addEventListener("click", () => {
    if (!state.currentMaskString) {
      return;
    }
    navigator.clipboard
      .writeText(state.currentMaskString)
      .then(() => {
        elements.copyMaskButton.textContent = "Copied pixel mask!";
        setTimeout(() => {
          elements.copyMaskButton.textContent = "Copy pixel mask";
        }, 1400);
      })
      .catch(() => {
        elements.copyMaskButton.textContent = "Copy failed";
        setTimeout(() => {
          elements.copyMaskButton.textContent = "Copy pixel mask";
        }, 1400);
      });
  });
}

function renderSpriteList(filterText = state.spriteFilterText) {
  state.spriteFilterText = filterText;
  const filteredIds = state.spriteIds.filter((id) => id.toLowerCase().includes(filterText));
  elements.spriteList.innerHTML = "";

  if (!filteredIds.length) {
    const empty = document.createElement("li");
    empty.textContent = "No sprites match";
    empty.style.justifyContent = "center";
    empty.style.opacity = "0.6";
    empty.style.cursor = "default";
    elements.spriteList.appendChild(empty);
    return;
  }

  filteredIds.forEach((id) => {
    const li = document.createElement("li");
    li.dataset.spriteId = id;
    const nameSpan = document.createElement("span");
    nameSpan.textContent = id;
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = String(state.spriteMap.get(id)?.length ?? 0);
    li.appendChild(nameSpan);
    li.appendChild(badge);
    li.addEventListener("click", () => selectSprite(id));
    elements.spriteList.appendChild(li);
  });

  if (!filteredIds.includes(state.selectedSpriteId)) {
    selectSprite(filteredIds[0]);
  } else {
    updateActiveSpriteListItem();
  }
}

function selectSprite(spriteId) {
  if (!spriteId || !state.spriteMap.has(spriteId)) {
    return;
  }
  state.selectedSpriteId = spriteId;
  state.selectedTraitIndex = null;
  state.selectedComponentIndex = -1;
  updateActiveSpriteListItem();
  elements.categoryFilter.value = "All";
  elements.componentSelect.innerHTML = '<option value="-1">Entire trait</option>';
  elements.componentSelect.disabled = true;
  updatePreviewImage(spriteId);
  updateStats(state.spriteMap.get(spriteId) || []);
  renderTraits();
}

function updateActiveSpriteListItem() {
  const items = elements.spriteList.querySelectorAll("li");
  items.forEach((item) => {
    if (item.dataset.spriteId === state.selectedSpriteId) {
      item.classList.add("active");
      item.setAttribute("aria-current", "true");
    } else {
      item.classList.remove("active");
      item.removeAttribute("aria-current");
    }
  });
  elements.spriteTitle.textContent = state.selectedSpriteId || "Select a sprite";
}

function updatePreviewImage(spriteId) {
  if (!spriteId) {
    elements.previewImage.hidden = true;
    elements.previewImage.removeAttribute("src");
    return;
  }
  const highRes = `data/punks_512px/${spriteId}.png`;
  const lowRes = `data/punks_24px/${spriteId}.png`;
  elements.previewImage.hidden = true;
  elements.previewImage.onerror = () => {
    elements.previewImage.onerror = null;
    elements.previewImage.src = lowRes;
  };
  elements.previewImage.src = highRes;
}

function renderTraits() {
  const spriteId = state.selectedSpriteId;
  const allTraits = state.spriteMap.get(spriteId) || [];
  const filterValue = elements.categoryFilter.value;
  const filteredTraits = filterValue && filterValue !== "All"
    ? allTraits.filter((trait) => trait.category === filterValue)
    : allTraits.slice();

  state.currentTraits = filteredTraits;
  state.currentRows = [];
  state.currentMasks = [];
  state.selectedTraitIndex = null;
  state.selectedComponentIndex = -1;
  state.currentMaskString = "";
  elements.traitBody.innerHTML = "";
  elements.pixelMaskOutput.textContent = "Select a trait to preview pixel coordinates.";
  elements.copyMaskButton.disabled = true;
  elements.componentSelect.innerHTML = '<option value="-1">Entire trait</option>';
  elements.componentSelect.disabled = true;

  if (!filteredTraits.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 7;
    cell.style.textAlign = "center";
    cell.style.padding = "28px";
    cell.style.color = "rgba(226,232,240,0.65)";
    cell.textContent = "No traits match this filter.";
    row.appendChild(cell);
    elements.traitBody.appendChild(row);
    clearHighlight();
    return;
  }

  filteredTraits.forEach((trait, index) => {
    const row = document.createElement("tr");
    row.dataset.index = String(index);

    const idxCell = document.createElement("td");
    idxCell.textContent = String(index + 1);
    row.appendChild(idxCell);

    const categoryCell = document.createElement("td");
    categoryCell.textContent = trait.category;
    row.appendChild(categoryCell);

    const nameCell = document.createElement("td");
    nameCell.textContent = toFriendlyName(trait.variant_hint);
    row.appendChild(nameCell);

    const copyCell = document.createElement("td");
    const copyButton = document.createElement("button");
    copyButton.className = "copy-btn";
    copyButton.textContent = trait.variant_hint;
    copyButton.title = "Copy layer name";
    copyButton.addEventListener("click", (event) => {
      event.stopPropagation();
      navigator.clipboard
        .writeText(trait.variant_hint)
        .then(() => {
          copyButton.textContent = "Copied!";
          setTimeout(() => {
            copyButton.textContent = trait.variant_hint;
          }, 1200);
        })
        .catch(() => {
          copyButton.textContent = "Copy failed";
          setTimeout(() => {
            copyButton.textContent = trait.variant_hint;
          }, 1200);
        });
    });
    copyCell.appendChild(copyButton);
    row.appendChild(copyCell);

    const colourCell = document.createElement("td");
    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = trait.color_hex;
    colourCell.appendChild(swatch);
    const colourText = document.createElement("span");
    colourText.textContent = `${trait.color_name} (${trait.color_hex})`;
    colourCell.appendChild(colourText);
    row.appendChild(colourCell);

    const coverageCell = document.createElement("td");
    coverageCell.textContent = `${trait.coverage_pct.toFixed(2)}%`;
    row.appendChild(coverageCell);

    const notesCell = document.createElement("td");
    notesCell.textContent = trait.notes;
    row.appendChild(notesCell);

    const maskSet = new Set(trait.pixels.map(({ row: r, col: c }) => `${r},${c}`));
    state.currentMasks[index] = maskSet;

    row.addEventListener("mouseenter", () => {
      if (!state.hoverPreview || state.selectedTraitIndex === Number(row.dataset.index)) {
        return;
      }
      highlightTrait(trait, state.selectedComponentIndex);
    });

    row.addEventListener("mouseleave", () => {
      if (state.selectedTraitIndex === null) {
        clearHighlight();
      } else {
        const selected = state.currentTraits[state.selectedTraitIndex];
        highlightTrait(selected, state.selectedComponentIndex);
      }
    });

    row.addEventListener("click", () => {
      selectTraitRow(row, index);
    });

    elements.traitBody.appendChild(row);
    state.currentRows.push(row);
  });

  selectTraitRow(state.currentRows[0], 0);
}

function selectTraitRow(row, index) {
  if (!row) {
    return;
  }
  state.currentRows.forEach((r) => r.classList.remove("active-row"));
  row.classList.add("active-row");
  state.selectedTraitIndex = index;
  state.selectedComponentIndex = -1;
  elements.componentSelect.innerHTML = '<option value="-1">Entire trait</option>';
  elements.componentSelect.disabled = true;

  const trait = state.currentTraits[index];
  const components = computeComponents(trait);
  if (components.length > 1) {
    components.forEach((component, componentIndex) => {
      const option = document.createElement("option");
      option.value = String(componentIndex);
      option.textContent = `Component ${componentIndex + 1} (${component.length} px)`;
      elements.componentSelect.appendChild(option);
    });
    elements.componentSelect.disabled = false;
    elements.componentSelect.value = "-1";
  }

  highlightTrait(trait, -1);
}

function highlightTrait(trait, componentIndex) {
  if (!trait) {
    clearHighlight();
    return;
  }
  const pixels = getPixelsForComponent(trait, componentIndex);
  if (!pixels.length) {
    clearHighlight();
    elements.pixelMaskOutput.textContent = "No pixel data available for this trait.";
    elements.copyMaskButton.disabled = true;
    state.currentMaskString = "";
    return;
  }
  drawPixels(pixels);
  const maskString = pixelsToMaskString(pixels);
  state.currentMaskString = maskString;
  elements.copyMaskButton.disabled = false;
  elements.pixelMaskOutput.textContent = formatPixelSummary(maskString, pixels.length);
}

function getPixelsForComponent(trait, componentIndex) {
  if (componentIndex === undefined || componentIndex === null || componentIndex < 0) {
    return trait.pixels;
  }
  const components = computeComponents(trait);
  if (!components.length) {
    return trait.pixels;
  }
  return components[componentIndex] || trait.pixels;
}

function computeComponents(trait) {
  if (trait.components) {
    return trait.components;
  }
  const pixels = trait.pixels;
  if (!pixels.length) {
    trait.components = [];
    return trait.components;
  }
  const lookup = new Map();
  pixels.forEach((pixel) => {
    lookup.set(`${pixel.row}:${pixel.col}`, pixel);
  });
  const visited = new Set();
  const components = [];
  const directions = [
    { dr: 1, dc: 0 },
    { dr: -1, dc: 0 },
    { dr: 0, dc: 1 },
    { dr: 0, dc: -1 },
  ];

  for (const key of lookup.keys()) {
    if (visited.has(key)) {
      continue;
    }
    const startPixel = lookup.get(key);
    const queue = [startPixel];
    const component = [];
    visited.add(key);
    while (queue.length) {
      const { row, col } = queue.shift();
      component.push({ row, col });
      for (const direction of directions) {
        const nr = row + direction.dr;
        const nc = col + direction.dc;
        const neighbourKey = `${nr}:${nc}`;
        if (lookup.has(neighbourKey) && !visited.has(neighbourKey)) {
          visited.add(neighbourKey);
          queue.push(lookup.get(neighbourKey));
        }
      }
    }
    components.push(component);
  }

  components.sort((a, b) => b.length - a.length);
  trait.components = components;
  return components;
}

function drawPixels(pixels) {
  resizeCanvas();
  const rect = elements.previewWrapper.getBoundingClientRect();
  if (!rect.width || !rect.height) {
    clearHighlight();
    return;
  }
  const scaleX = rect.width / 24;
  const scaleY = rect.height / 24;
  clearHighlight();

  highlightCtx.fillStyle = "rgba(96, 165, 250, 0.32)";
  highlightCtx.strokeStyle = "rgba(14, 165, 233, 0.95)";
  highlightCtx.lineWidth = 2.8;
  pixels.forEach(({ row, col }) => {
    highlightCtx.fillRect(col * scaleX, row * scaleY, scaleX, scaleY);
  });

  const rows = pixels.map((pixel) => pixel.row);
  const cols = pixels.map((pixel) => pixel.col);
  const minRow = Math.min(...rows);
  const maxRow = Math.max(...rows);
  const minCol = Math.min(...cols);
  const maxCol = Math.max(...cols);

  highlightCtx.strokeRect(
    minCol * scaleX,
    minRow * scaleY,
    (maxCol - minCol + 1) * scaleX,
    (maxRow - minRow + 1) * scaleY
  );
}

function resizeCanvas() {
  const rect = elements.previewWrapper.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  elements.highlightCanvas.width = rect.width * dpr;
  elements.highlightCanvas.height = rect.height * dpr;
  elements.highlightCanvas.style.width = `${rect.width}px`;
  elements.highlightCanvas.style.height = `${rect.height}px`;
  highlightCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function clearHighlight() {
  highlightCtx.save();
  highlightCtx.setTransform(1, 0, 0, 1, 0, 0);
  highlightCtx.clearRect(0, 0, elements.highlightCanvas.width, elements.highlightCanvas.height);
  highlightCtx.restore();
}

function pixelsToMaskString(pixels) {
  return pixels.map(({ row, col }) => `${row},${col}`).join(";");
}

function formatPixelSummary(maskString, count) {
  const limit = 200;
  if (maskString.length <= limit) {
    return `Pixels (${count}): ${maskString}`;
  }
  return `Pixels (${count}): ${maskString.slice(0, limit)}…`;
}

function updateStats(traits) {
  if (!traits.length) {
    elements.stats.innerHTML = "";
    return;
  }
  const items = [];
  items.push(`<span>Traits <strong>${traits.length}</strong></span>`);
  const background = traits.find((trait) => trait.category === "Background");
  if (background) {
    items.push(`<span>Background <strong>${background.variant_hint}</strong></span>`);
  }
  const uniqueColours = new Set(traits.map((trait) => trait.color_hex));
  items.push(`<span>Unique colours <strong>${uniqueColours.size}</strong></span>`);
  elements.stats.innerHTML = items.join("");
}

function populateCategoryFilter(data) {
  const categories = new Set([
    "All",
    ...data.map((trait) => trait.category),
  ]);
  elements.categoryFilter.innerHTML = "";
  Array.from(categories)
    .sort()
    .forEach((category) => {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      elements.categoryFilter.appendChild(option);
    });
  elements.categoryFilter.disabled = false;
  elements.categoryFilter.value = "All";
}

function toFriendlyName(variantHint) {
  return variantHint
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function showError(message) {
  elements.traitBody.innerHTML = "";
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 7;
  cell.style.textAlign = "center";
  cell.style.padding = "28px";
  cell.textContent = message;
  row.appendChild(cell);
  elements.traitBody.appendChild(row);
}

function handlePreviewClick(event) {
  if (!state.currentTraits.length) {
    return;
  }
  const rect = elements.previewWrapper.getBoundingClientRect();
  const relX = event.clientX - rect.left;
  const relY = event.clientY - rect.top;
  if (relX < 0 || relY < 0 || relX > rect.width || relY > rect.height) {
    return;
  }
  const col = Math.floor((relX / rect.width) * 24);
  const row = Math.floor((relY / rect.height) * 24);
  selectTraitByPixel(row, col);
}

function selectTraitByPixel(row, col) {
  const key = `${row},${col}`;
  for (let index = 0; index < state.currentMasks.length; index += 1) {
    const mask = state.currentMasks[index];
    if (mask && mask.has(key)) {
      selectTraitRow(state.currentRows[index], index);
      return;
    }
  }
}
