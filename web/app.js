import { clearFieldErrors, setStatus, showErrors } from "./js/accessibility.js";
import { APP_TITLE } from "./js/config.js";
import {
  copyText,
  exportCsv,
  exportDashboardPng,
  exportFigurePng,
} from "./js/exports.js";
import {
  applyEffectDefaults,
  readRequest,
  updateControlState,
} from "./js/inputs.js";
import { renderResult } from "./js/renderers.js";
import { WorkerRuntime } from "./js/runtime.js";

const form = document.querySelector("#applet-form");
const errorSummary = document.querySelector("#error-summary");
const status = document.querySelector("#runtime-status");
const retryButton = document.querySelector("#retry-worker");
const calculateButton = document.querySelector("#calculate");
const result = document.querySelector("#result");
const summary = document.querySelector("#result-summary");
const table = document.querySelector("#reference-table");
const plot = document.querySelector("#plot");
const exportButtons = [...document.querySelectorAll("[data-export]")];
const copyButtons = [...document.querySelectorAll("[data-copy]")];
const emptyState = document.querySelector(".empty-state");
const runtime = new WorkerRuntime();
let currentResponse = null;
let calculationGeneration = 0;
let calculationInFlight = false;
let runtimeGeneration = 0;
let runtimeReady = false;

function resultElements() {
  return {
    caption: document.querySelector("#figure-caption"),
    conditioning: document.querySelector("#conditioning-result"),
    currentCritical: document.querySelector("#current-critical-summary"),
    legacy: document.querySelector("#legacy-summary"),
    legacySection: document.querySelector("#legacy-section"),
    meaningful: document.querySelector("#meaningful-summary"),
    meaningfulSection: document.querySelector("#meaningful-section"),
    plot,
    precision: document.querySelector("#precision-summary"),
    rule: document.querySelector("#rule-summary"),
    scenarioCritical: document.querySelector("#scenario-critical-summary"),
    summary,
    table,
    warnings: document.querySelector("#warnings-list"),
  };
}

function setExportAvailability(enabled) {
  for (const button of [...exportButtons, ...copyButtons]) {
    button.disabled = !enabled;
  }
}

function clearResultState() {
  currentResponse = null;
  result.hidden = true;
  emptyState.hidden = false;
  setExportAvailability(false);
}

async function startRuntime() {
  const generation = ++runtimeGeneration;
  calculationGeneration += 1;
  calculationInFlight = false;
  runtimeReady = false;
  clearResultState();
  calculateButton.disabled = true;
  retryButton.hidden = true;
  setStatus(status, "Loading the local Python runtime…", "loading");
  try {
    const ready = await runtime.restart();
    if (generation !== runtimeGeneration) {
      return;
    }
    document.querySelector("#runtime-versions").textContent = ready.packages
      .map((entry) => `${entry.distribution} ${entry.version}`)
      .join(" · ");
    const externalPackages = ready.packages.slice(1);
    document.querySelector("#core-version").textContent =
      `Core: ${externalPackages
        .map((entry) => `${entry.distribution} ${entry.version}`)
        .join(" · ")}`;
    runtimeReady = true;
    calculateButton.disabled = false;
    setStatus(status, "Ready. Calculations stay in this browser.", "ready");
  } catch {
    if (generation !== runtimeGeneration) {
      return;
    }
    retryButton.hidden = false;
    setStatus(status, "The calculation worker could not start.", "error");
  }
}

form.addEventListener("change", (event) => {
  if (event.target.name === "effect_type") {
    applyEffectDefaults(form);
  }
  if (["effect_type", "precision_mode"].includes(event.target.name)) {
    updateControlState(form);
  }
});

form.addEventListener("input", () => {
  if (currentResponse !== null || calculationInFlight) {
    calculationGeneration += 1;
    clearResultState();
    if (runtimeReady) {
      setStatus(status, "Inputs changed. Calculate to update the result.", "ready");
    }
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const generation = ++calculationGeneration;
  clearResultState();
  clearFieldErrors(form);
  const { errors, request } = readRequest(form);
  showErrors(errorSummary, errors);
  if (errors.length > 0) {
    setStatus(status, "Check the highlighted inputs.", "error");
    return;
  }

  calculationInFlight = true;
  calculateButton.disabled = true;
  setStatus(status, "Calculating exact selected-claim probability…", "loading");
  try {
    const response = await runtime.calculate(request);
    if (generation !== calculationGeneration) {
      return;
    }
    await renderResult(response, resultElements());
    if (generation !== calculationGeneration) {
      return;
    }
    emptyState.hidden = true;
    result.hidden = false;
    currentResponse = response;
    setExportAvailability(true);
    setStatus(status, "Calculation complete.", "ready");
  } catch (error) {
    if (generation !== calculationGeneration) {
      return;
    }
    clearResultState();
    showErrors(errorSummary, [
      {
        controlId: null,
        message:
          error.code === "validation_error"
            ? error.message
            : "Calculation failed safely. Restart the worker and try again.",
      },
    ]);
    if (error.code !== "validation_error") {
      retryButton.hidden = false;
    }
    setStatus(status, "Calculation failed.", "error");
  } finally {
    calculationInFlight = false;
    calculateButton.disabled = !runtimeReady;
    if (generation !== calculationGeneration && runtimeReady) {
      setStatus(status, "Inputs changed. Calculate to update the result.", "ready");
    }
  }
});

form.addEventListener("reset", () => {
  calculationGeneration += 1;
  clearResultState();
  clearFieldErrors(form);
  showErrors(errorSummary, []);
  requestAnimationFrame(() => {
    updateControlState(form);
    calculateButton.disabled = calculationInFlight || !runtimeReady;
    setStatus(
      status,
      calculationInFlight
        ? "Reset complete. Discarding the in-flight result…"
        : "Ready. Calculations stay in this browser.",
      calculationInFlight ? "loading" : "ready",
    );
  });
});

retryButton.addEventListener("click", startRuntime);

document.querySelector("#export-csv").addEventListener("click", () => {
  if (currentResponse) {
    exportCsv(currentResponse, APP_TITLE);
  }
});
document.querySelector("#export-figure").addEventListener("click", async () => {
  if (currentResponse) {
    await exportFigurePng(plot, APP_TITLE);
  }
});
document.querySelector("#export-dashboard").addEventListener("click", async () => {
  if (!currentResponse) {
    return;
  }
  const dashboardSummary =
    `${currentResponse.meta.conditioning_statement} ` +
    `${currentResponse.rule.label}; alpha ${currentResponse.rule.alpha}; target ` +
    `${currentResponse.rule.target_probability}; ` +
    `${currentResponse.precision.information_multiplier}x information scenario. ` +
    "Not observed evidence or a sample-size calculation.";
  await exportDashboardPng(plot, dashboardSummary, APP_TITLE);
});
document.querySelector("#copy-caption").addEventListener("click", async () => {
  if (currentResponse) {
    await copyText(currentResponse.meta.caption);
    setStatus(status, "Caption copied.", "ready");
  }
});

updateControlState(form);
setExportAvailability(false);
startRuntime();
