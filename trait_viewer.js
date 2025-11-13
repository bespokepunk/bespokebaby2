function updateSpriteBadge(badgeElement) {
  const spriteId = badgeElement.dataset.spriteId;
  const traits = state.spriteMap.get(spriteId) || [];
  const categoryFilter = elements.categoryFilter.value;
  const visibleCount =
    !categoryFilter || categoryFilter === "All"
      ? traits.filter((trait) => trait.category !== "Palette").length
      : traits.filter((trait) => trait.category === categoryFilter).length;
  badgeElement.textContent = String(visibleCount);
}

function updateAllBadges() {
  const badges = elements.spriteList.querySelectorAll(".badge");
  badges.forEach((badge) => updateSpriteBadge(badge));
}

"use strict";

const elements = {
  layout: document.getElementById("layout"),
  spriteSearch: document.getElementById("spriteSearch"),
  spriteList: document.getElementById("spriteList"),
  toggleSidebar: document.getElementById("toggleSidebar"),
  spriteTitle: document.getElementById("spriteTitle"),
  stats: document.getElementById("stats"),
  paletteSection: document.getElementById("paletteSection"),
  paletteMeta: document.getElementById("paletteMeta"),
  palettePreview: document.getElementById("palettePreview"),
  paletteCanvas: document.getElementById("paletteMiniCanvas"),
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

const CATEGORY_ORDER = {
  Background: 0,
  Base: 1,
  Face: 2,
  Hair: 3,
  FacialHair: 4,
  Headwear: 5,
  Eyewear: 6,
  FaceAccessory: 7,
  Jewelry: 8,
  Clothing: 9,
  Palette: 200,
  Unassigned: 300,
};

function getCategoryPriority(category) {
  return CATEGORY_ORDER[category] ?? 1000;
}

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
  selectedComponentKey: "-1",
  hoverPreview: true,
};

const palettePixelCache = new Map();

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
    traits.sort((a, b) => {
      const priorityA = getCategoryPriority(a.category);
      const priorityB = getCategoryPriority(b.category);
      if (priorityA !== priorityB) {
        return priorityA - priorityB;
      }
      return a.variant_hint.localeCompare(b.variant_hint);
    });
  }
  state.spriteMap = map;
  state.spriteIds = Array.from(map.keys()).sort();
}

function groupTraitsByVariant(traits) {
  const groups = [];
  const map = new Map();
  const totalPixels = 24 * 24;

  for (const trait of traits) {
    const key = `${trait.category}||${trait.variant_hint}`;
    let group = map.get(key);
    if (!group) {
      group = {
        sprite_id: trait.sprite_id,
        category: trait.category,
        variant_hint: trait.variant_hint,
        pixelSet: new Set(),
        pixels: [],
        pixel_mask: "",
        coverage_pct: 0,
        color_hex: trait.color_hex,
        color_name: trait.color_name,
        notes: "",
        slices: [],
        sliceSummary: "",
        multiColor: false,
      };
      map.set(key, group);
      groups.push(group);
    }
    const slicePixels = trait.pixels || [];
    const sliceSet = new Set(slicePixels.map(({ row, col }) => `${row},${col}`));
    group.slices.push({
      color_hex: trait.color_hex,
      color_name: trait.color_name,
      coverage_pct: trait.coverage_pct,
      notes: trait.notes || "",
      pixels: slicePixels,
      pixel_mask: trait.pixel_mask,
      pixelSet: sliceSet,
    });
  }

  for (const group of groups) {
    const unionSet = new Set();
    const noteSet = new Set();
    const colourNames = new Set();
    const colourHexes = new Set();

    group.slices.forEach((slice) => {
      slice.pixelSet.forEach((coord) => unionSet.add(coord));
      if (slice.notes) {
        noteSet.add(slice.notes);
      }
      if (slice.color_name) {
        colourNames.add(slice.color_name);
      }
      if (slice.color_hex) {
        colourHexes.add(slice.color_hex.toLowerCase());
      }
    });

    group.pixelSet = unionSet;
    const pixels = Array.from(unionSet, (coord) => {
      const [rowStr, colStr] = coord.split(",");
      return { row: Number(rowStr), col: Number(colStr) };
    }).sort((a, b) => (a.row === b.row ? a.col - b.col : a.row - b.row));
    group.pixels = pixels;
    group.pixel_mask = pixels.map(({ row, col }) => `${row},${col}`).join(";");
    group.coverage_pct = unionSet.size
      ? Number(((unionSet.size / totalPixels) * 100).toFixed(2))
      : 0;

    const sliceSummary = group.slices
      .map((slice) => {
        const pct = ((slice.pixels.length / totalPixels) * 100).toFixed(2);
        return `${slice.color_name || "Unnamed"} (${slice.pixels.length} px, ${pct}%)`;
      })
      .join(" • ");
    group.sliceSummary = sliceSummary;

    const combinedNotes = Array.from(noteSet).join(" · ");
    group.notes = combinedNotes;

    if (colourHexes.size === 1) {
      const firstSlice = group.slices[0];
      group.color_hex = firstSlice.color_hex;
      group.color_name = firstSlice.color_name;
      group.multiColor = false;
    } else {
      group.color_hex = null;
      group.color_name = `${colourHexes.size} colours`;
      group.multiColor = true;
    }
    group.priority = getCategoryPriority(group.category);
    if (!group.notes && colourNames.size) {
      group.notes = `Unique colours ${Array.from(colourNames).join(", ")}`;
    }
  }

  groups.sort((a, b) => {
    if (a.priority !== b.priority) {
      return a.priority - b.priority;
    }
    if (a.category !== b.category) {
      return a.category.localeCompare(b.category);
    }
    return a.variant_hint.localeCompare(b.variant_hint);
  });

  return groups;
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
    const { value } = elements.componentSelect;
    if (!value) {
      state.selectedComponentKey = "-1";
      return;
    }
    state.selectedComponentKey = value;
    if (state.selectedTraitIndex !== null) {
      const trait = state.currentTraits[state.selectedTraitIndex];
      highlightTrait(trait, state.selectedComponentKey);
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
    badge.dataset.spriteId = id;
    updateSpriteBadge(badge);
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
  state.selectedComponentKey = "-1";
  updateActiveSpriteListItem();
  elements.categoryFilter.value = "All";
  elements.componentSelect.innerHTML = '<option value="-1">Entire trait</option>';
  elements.componentSelect.disabled = true;
  updatePreviewImage(spriteId);
  updatePalettePreview(spriteId).catch((error) => {
    console.error(error);
  });
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

async function loadSpritePalettePixels(spriteId) {
  if (palettePixelCache.has(spriteId)) {
    return palettePixelCache.get(spriteId);
  }
  const image = new Image();
  image.src = `data/punks_24px/${spriteId}.png`;
  const counts = await new Promise((resolve, reject) => {
    image.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 24;
      canvas.height = 24;
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        reject(new Error("Unable to obtain canvas context for palette extraction."));
        return;
      }
      ctx.clearRect(0, 0, 24, 24);
      ctx.drawImage(image, 0, 0, 24, 24);
      const { data } = ctx.getImageData(0, 0, 24, 24);
      const map = new Map();
      for (let i = 0; i < data.length; i += 4) {
        const alpha = data[i + 3];
        if (alpha < 16) {
          continue;
        }
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const hex = `#${r.toString(16).padStart(2, "0")}${g
          .toString(16)
          .padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
        map.set(hex, (map.get(hex) || 0) + 1);
      }
      resolve(
        Array.from(map.entries()).map(([hex, count]) => ({
          hex,
          count,
        }))
      );
    };
    image.onerror = () => reject(new Error(`Failed to load low-res sprite for ${spriteId}`));
  });
  palettePixelCache.set(spriteId, counts);
  return counts;
}

async function updatePalettePreview(spriteId) {
  const section = elements.paletteSection;
  const preview = elements.palettePreview;
  const meta = elements.paletteMeta;
  const canvas = elements.paletteCanvas;
  if (!section || !preview || !meta || !canvas) {
    return;
  }

  if (!spriteId || !state.spriteMap.has(spriteId)) {
    section.hidden = true;
    preview.innerHTML = "";
    meta.textContent = "";
    clearPaletteCanvas();
    return;
  }

  const traits = state.spriteMap.get(spriteId) || [];
  const nameMap = new Map();
  const registerName = (hex, name) => {
    if (!hex || !name) {
      return;
    }
    const normalized = hex.startsWith("#") ? hex.toLowerCase() : `#${hex.toLowerCase()}`;
    if (!nameMap.has(normalized)) {
      nameMap.set(normalized, name);
    }
  };

  traits.forEach((trait) => {
    if (trait.color_hex && trait.color_name) {
      registerName(trait.color_hex, trait.color_name);
    }
    if (trait.slices?.length) {
      trait.slices.forEach((slice) => {
        if (slice.color_hex && slice.color_name) {
          registerName(slice.color_hex, slice.color_name);
        }
      });
    }
  });

  let pixelCounts;
  try {
    pixelCounts = await loadSpritePalettePixels(spriteId);
  } catch (error) {
    console.error(error);
    section.hidden = true;
    preview.innerHTML = "";
    meta.textContent = "Palette unavailable";
    clearPaletteCanvas();
    return;
  }

  const totalPixels = 24 * 24;
  const colours = pixelCounts
    .map(({ hex, count }) => {
      const normalized = hex.toLowerCase();
      const formatted = normalized.toUpperCase();
      const coverage = (count / totalPixels) * 100;
      return {
        hex: formatted,
        name: nameMap.get(normalized) || "",
        coverage,
      };
    })
    .filter((entry) => entry.hex);
  if (!colours.length) {
    section.hidden = true;
    preview.innerHTML = "";
    meta.textContent = "";
    clearPaletteCanvas();
    return;
  }

  colours.sort((a, b) => {
    if ((b.coverage ?? 0) !== (a.coverage ?? 0)) {
      return (b.coverage ?? 0) - (a.coverage ?? 0);
    }
    return a.hex.localeCompare(b.hex);
  });

  section.hidden = false;
  preview.innerHTML = "";
  colours.forEach((colour) => {
    const swatch = document.createElement("div");
    swatch.className = "palette-swatch";
    swatch.style.background = colour.hex;
    swatch.dataset.hex = colour.hex;
    const namePart = colour.name ? `${colour.name}` : "Colour";
    const coveragePart = colour.coverage ? ` — ${colour.coverage.toFixed(2)}%` : "";
    swatch.title = `${namePart} ${colour.hex}${coveragePart}`;
    preview.appendChild(swatch);
  });

  const metaParts = [`${colours.length} colours`];
  const totalCoverage = colours.reduce((acc, entry) => acc + (entry.coverage || 0), 0);
  if (totalCoverage > 0) {
    metaParts.push(`${totalCoverage.toFixed(1)}% coverage`);
  }
  meta.textContent = metaParts.join(" · ");
  drawPaletteCanvas(colours);
}

function drawPaletteCanvas(colours) {
  const canvas = elements.paletteCanvas;
  if (!canvas) {
    return;
  }
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    return;
  }
  const count = colours.length || 1;
  canvas.width = Math.max(count, 1);
  canvas.height = 1;
  ctx.imageSmoothingEnabled = false;
  colours.forEach((colour, index) => {
    ctx.fillStyle = colour.hex;
    ctx.fillRect(index, 0, 1, 1);
  });
}

function clearPaletteCanvas() {
  const canvas = elements.paletteCanvas;
  if (!canvas) {
    return;
  }
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    return;
  }
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function renderTraits() {
  const spriteId = state.selectedSpriteId;
  const allTraits = state.spriteMap.get(spriteId) || [];
  const filterValue = elements.categoryFilter.value;
  let filteredTraits;
  if (!filterValue || filterValue === "All") {
    filteredTraits = allTraits.filter((trait) => trait.category !== "Palette");
  } else {
    filteredTraits = allTraits.filter((trait) => trait.category === filterValue);
    if (filteredTraits.length === 0 && filterValue === "Palette") {
      filteredTraits = allTraits.filter((trait) => trait.category === "Palette");
    }
  }

  filteredTraits.sort((a, b) => {
    const priorityA = getCategoryPriority(a.category);
    const priorityB = getCategoryPriority(b.category);
    if (priorityA !== priorityB) {
      return priorityA - priorityB;
    }
    if (a.category !== b.category) {
      return a.category.localeCompare(b.category);
    }
    if (a.variant_hint !== b.variant_hint) {
      return a.variant_hint.localeCompare(b.variant_hint);
    }
    return (a.color_hex || "").localeCompare(b.color_hex || "");
  });

  const groupedTraits = groupTraitsByVariant(filteredTraits);
  groupedTraits.sort((a, b) => {
    const priorityA = getCategoryPriority(a.category);
    const priorityB = getCategoryPriority(b.category);
    if (priorityA !== priorityB) {
      return priorityA - priorityB;
    }
    if (a.category !== b.category) {
      return a.category.localeCompare(b.category);
    }
    if (a.variant_hint !== b.variant_hint) {
      return a.variant_hint.localeCompare(b.variant_hint);
    }
    return a.variant_hint.localeCompare(b.variant_hint);
  });

  const displayTraits = filterValue === "Palette"
    ? groupedTraits
    : groupedTraits.filter((trait) => trait.category !== "Palette");

  state.currentTraits = displayTraits;
  state.currentRows = [];
  state.currentMasks = [];
  state.selectedTraitIndex = null;
  state.selectedComponentKey = "-1";
  state.currentMaskString = "";
  elements.traitBody.innerHTML = "";
  elements.pixelMaskOutput.textContent = "Select a trait to preview pixel coordinates.";
  elements.copyMaskButton.disabled = true;
  elements.componentSelect.innerHTML = '<option value="-1">Entire trait</option>';
  elements.componentSelect.disabled = true;
  updateAllBadges();

  if (!displayTraits.length) {
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
    updateStats(displayTraits);
    return;
  }

  updateStats(displayTraits);

  displayTraits.forEach((trait, index) => {
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
    if (trait.multiColor && trait.slices.length > 1) {
      const stack = document.createElement("div");
      stack.className = "swatch-stack";
      trait.slices.forEach((slice, sliceIndex) => {
        if (!slice.color_hex) {
          return;
        }
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "swatch-button";
        btn.style.background = slice.color_hex;
        btn.title = `${slice.color_name || "Colour"} (${slice.color_hex}) — ${slice.pixels.length} px`;
        btn.addEventListener("click", (event) => {
          event.stopPropagation();
          selectTraitRow(row, index);
          state.selectedComponentKey = `slice-${sliceIndex}`;
          elements.componentSelect.value = `slice-${sliceIndex}`;
          highlightTrait(trait, state.selectedComponentKey);
        });
        stack.appendChild(btn);
      });
      colourCell.appendChild(stack);
      const colourText = document.createElement("span");
      const uniqueNames = Array.from(new Set(trait.slices.map((slice) => slice.color_name)));
      colourText.textContent = `${trait.slices.length} colours`;
      colourText.title = uniqueNames.join(", ");
      colourCell.appendChild(colourText);
    } else {
      const swatch = document.createElement("span");
      swatch.className = "swatch";
      swatch.style.background = trait.color_hex || "#ffffff";
      colourCell.appendChild(swatch);
      const colourText = document.createElement("span");
      colourText.textContent = trait.color_hex
        ? `${trait.color_name} (${trait.color_hex})`
        : trait.color_name;
      colourCell.appendChild(colourText);
    }
    row.appendChild(colourCell);

    const coverageCell = document.createElement("td");
    coverageCell.textContent = `${trait.coverage_pct.toFixed(2)}%`;
    row.appendChild(coverageCell);

    const notesCell = document.createElement("td");
    const noteParts = [];
    if (trait.notes) {
      noteParts.push(trait.notes);
    }
    if (trait.multiColor && trait.sliceSummary) {
      noteParts.push(`Colours: ${trait.sliceSummary}`);
    }
    notesCell.textContent = noteParts.join(" · ");
    row.appendChild(notesCell);

    const maskSet = trait.pixelSet
      ? new Set(trait.pixelSet)
      : new Set(trait.pixels.map(({ row: r, col: c }) => `${r},${c}`));
    state.currentMasks[index] = maskSet;

    row.addEventListener("mouseenter", () => {
      if (!state.hoverPreview || state.selectedTraitIndex === Number(row.dataset.index)) {
        return;
      }
      highlightTrait(trait, state.selectedComponentKey);
    });

    row.addEventListener("mouseleave", () => {
      if (state.selectedTraitIndex === null) {
        clearHighlight();
      } else {
        const selected = state.currentTraits[state.selectedTraitIndex];
        highlightTrait(selected, state.selectedComponentKey);
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
  state.selectedComponentKey = "-1";
  elements.componentSelect.innerHTML = '<option value="-1">Entire trait</option>';
  elements.componentSelect.disabled = true;

  const trait = state.currentTraits[index];
  const components = computeComponents(trait);
  if (components.length > 1) {
    components.forEach((component, componentIndex) => {
      const option = document.createElement("option");
      option.value = `component-${componentIndex}`;
      option.textContent = `Component ${componentIndex + 1} (${component.length} px)`;
      elements.componentSelect.appendChild(option);
    });
    elements.componentSelect.disabled = false;
  }

  if (trait.slices && trait.slices.length > 1) {
    const separator = document.createElement("option");
    separator.textContent = "Original colours";
    separator.disabled = true;
    separator.value = "";
    elements.componentSelect.appendChild(separator);
    trait.slices.forEach((slice, sliceIndex) => {
      const option = document.createElement("option");
      option.value = `slice-${sliceIndex}`;
      const labelHex = slice.color_hex ? slice.color_hex : "n/a";
      option.textContent = `${slice.color_name || "Colour"} (${labelHex}) — ${slice.pixels.length} px`;
      elements.componentSelect.appendChild(option);
    });
    elements.componentSelect.disabled = false;
  }
  elements.componentSelect.value = "-1";

  highlightTrait(trait, -1);
}

function highlightTrait(trait, componentKey) {
  if (!trait) {
    clearHighlight();
    return;
  }
  if (typeof componentKey === "string" && componentKey.startsWith("slice-")) {
    elements.componentSelect.value = componentKey;
  } else if (typeof componentKey === "string" && componentKey.startsWith("component-")) {
    elements.componentSelect.value = componentKey;
  } else {
    elements.componentSelect.value = "-1";
  }
  const pixels = getPixelsForComponent(trait, componentKey);
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

function getPixelsForComponent(trait, componentKey) {
  if (componentKey === undefined || componentKey === null || componentKey === -1 || componentKey === "-1") {
    return trait.pixels;
  }
  if (typeof componentKey === "string") {
    if (componentKey.startsWith("slice-")) {
      const index = Number(componentKey.split("-")[1]);
      const slice = trait.slices?.[index];
      return slice && slice.pixels ? slice.pixels : trait.pixels;
    }
    if (componentKey.startsWith("component-")) {
      const idx = Number(componentKey.split("-")[1]);
      const components = computeComponents(trait);
      if (!components.length) {
        return trait.pixels;
      }
      return components[idx] || trait.pixels;
    }
    const numeric = Number(componentKey);
    if (!Number.isNaN(numeric) && numeric >= 0) {
      const components = computeComponents(trait);
      if (!components.length) {
        return trait.pixels;
      }
      return components[numeric] || trait.pixels;
    }
    return trait.pixels;
  }
  const components = computeComponents(trait);
  if (!components.length) {
    return trait.pixels;
  }
  return components[componentKey] || trait.pixels;
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
  const uniqueColours = new Set();
  traits.forEach((trait) => {
    if (trait.slices && trait.slices.length) {
      trait.slices.forEach((slice) => {
        if (slice.color_hex) {
          uniqueColours.add(slice.color_hex.toLowerCase());
        }
      });
    } else if (trait.color_hex) {
      uniqueColours.add(trait.color_hex.toLowerCase());
    }
  });
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
