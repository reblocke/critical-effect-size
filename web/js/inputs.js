const RATIO_EFFECTS = new Set([
  "odds_ratio",
  "risk_ratio",
  "hazard_ratio",
  "incidence_rate_ratio",
  "ratio_of_means",
]);

function parseFiniteNumber(form, name, label) {
  const control = form.elements.namedItem(name);
  const value = control.value.trim();
  if (value === "") {
    control.setAttribute("aria-invalid", "true");
    return { error: { controlId: control.id, message: `${label} is required.` } };
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    control.setAttribute("aria-invalid", "true");
    return {
      error: { controlId: control.id, message: `${label} must be a finite number.` },
    };
  }
  return { value: parsed };
}

function parseOptionalFiniteNumber(form, name, label) {
  const control = form.elements.namedItem(name);
  const value = control.value.trim();
  if (value === "") {
    return { value: null };
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    control.setAttribute("aria-invalid", "true");
    return {
      error: { controlId: control.id, message: `${label} must be a finite number.` },
    };
  }
  return { value: parsed };
}

function setValue(form, name, value) {
  form.elements.namedItem(name).value = value;
}

export function applyEffectDefaults(form) {
  const ratio = RATIO_EFFECTS.has(form.elements.namedItem("effect_type").value);
  if (ratio) {
    setValue(form, "null_value", "1");
    setValue(form, "observed_estimate", "1.5");
    setValue(form, "ci_lower", "1.1");
    setValue(form, "ci_upper", "2.05");
    setValue(form, "standard_error", "0.16");
    setValue(form, "meaningful_effect", "1.5");
  } else {
    setValue(form, "null_value", "0");
    setValue(form, "observed_estimate", "0.4");
    setValue(form, "ci_lower", "0.1");
    setValue(form, "ci_upper", "0.7");
    setValue(form, "standard_error", "0.15");
    setValue(form, "meaningful_effect", "0.5");
  }
  setValue(form, "display_min", "");
  setValue(form, "display_max", "");
}

export function updateControlState(form) {
  const direct = form.elements.namedItem("precision_mode").value === "direct_se";
  const ciFields = document.querySelector("#ci-fields");
  const seFields = document.querySelector("#se-fields");
  ciFields.hidden = direct;
  seFields.hidden = !direct;
  for (const control of ciFields.querySelectorAll("input")) {
    control.disabled = direct;
  }
  for (const control of seFields.querySelectorAll("input")) {
    control.disabled = !direct;
  }
  const ratio = RATIO_EFFECTS.has(form.elements.namedItem("effect_type").value);
  document.querySelector("#se-scale-note").textContent = ratio
    ? "Ratio-measure SE must be entered on the log scale."
    : "Additive-measure SE must be entered on the identity scale.";
}

export function readRequest(form) {
  const precisionMode = form.elements.namedItem("precision_mode").value;
  const direct = precisionMode === "direct_se";
  const observed = parseOptionalFiniteNumber(
    form,
    "observed_estimate",
    "Observed estimate",
  );
  const lower = direct
    ? { value: null }
    : parseFiniteNumber(form, "ci_lower", "Lower 95% confidence limit");
  const upper = direct
    ? { value: null }
    : parseFiniteNumber(form, "ci_upper", "Upper 95% confidence limit");
  const standardError = direct
    ? parseFiniteNumber(form, "standard_error", "Working-scale standard error")
    : { value: null };
  const nullValue = parseFiniteNumber(form, "null_value", "Null value");
  const alpha = parseFiniteNumber(form, "alpha", "Alpha");
  const target = parseFiniteNumber(
    form,
    "target_probability",
    "Target selected-claim probability",
  );
  const meaningful = parseOptionalFiniteNumber(
    form,
    "meaningful_effect",
    "Meaningful effect",
  );
  const multiplier = parseFiniteNumber(
    form,
    "information_multiplier",
    "Information multiplier",
  );
  const displayMin = parseOptionalFiniteNumber(form, "display_min", "Display minimum");
  const displayMax = parseOptionalFiniteNumber(form, "display_max", "Display maximum");
  const errors = [
    observed.error,
    lower.error,
    upper.error,
    standardError.error,
    nullValue.error,
    alpha.error,
    target.error,
    meaningful.error,
    multiplier.error,
    displayMin.error,
    displayMax.error,
  ].filter(Boolean);
  if (errors.length > 0) {
    return { errors, request: null };
  }
  if ((displayMin.value === null) !== (displayMax.value === null)) {
    const missing = displayMin.value === null ? "display_min" : "display_max";
    const control = form.elements.namedItem(missing);
    control.setAttribute("aria-invalid", "true");
    return {
      errors: [
        {
          controlId: control.id,
          message: "Display minimum and maximum must be supplied together.",
        },
      ],
      request: null,
    };
  }
  return {
    errors: [],
    request: {
      precision_mode: precisionMode,
      effect_type: form.elements.namedItem("effect_type").value,
      observed_estimate: observed.value,
      ci_lower: lower.value,
      ci_upper: upper.value,
      standard_error: standardError.value,
      null_value: nullValue.value,
      alpha: alpha.value,
      selection_rule: form.elements.namedItem("selection_rule").value,
      target_probability: target.value,
      meaningful_effect: meaningful.value,
      information_multiplier: multiplier.value,
      display_min: displayMin.value,
      display_max: displayMax.value,
    },
  };
}
