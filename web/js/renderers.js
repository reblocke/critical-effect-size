function formatNumber(value, maximumSignificantDigits = 7) {
  if (value === null || value === undefined) {
    return "—";
  }
  return Number(value).toLocaleString("en-US", {
    maximumSignificantDigits,
  });
}

function formatProbability(value) {
  return Number(value).toLocaleString("en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
    style: "percent",
  });
}

function solutionText(solutions) {
  return solutions
    .map(
      (solution) =>
        `${solution.direction}: ${formatNumber(solution.critical_effect_display)} ` +
        `(delta ${formatNumber(solution.critical_delta)}, achieved ` +
        `${formatProbability(solution.achieved_probability)})`,
    )
    .join("; ");
}

function renderReferenceRows(response, table) {
  const body = table.querySelector("tbody");
  body.replaceChildren();
  for (const row of response.reference_effects.critical_rows) {
    const tableRow = document.createElement("tr");
    const values = [
      row.precision === "current"
        ? "Current"
        : `${formatNumber(row.information_multiplier)}x information`,
      formatProbability(row.target_probability),
      row.direction,
      formatNumber(row.critical_effect_display),
      formatNumber(row.critical_delta),
      formatProbability(row.achieved_probability),
    ];
    values.forEach((text, index) => {
      const cell = document.createElement(index === 0 ? "th" : "td");
      if (index === 0) {
        cell.scope = "row";
      }
      cell.textContent = text;
      if (index === 3 && row.note) {
        const note = document.createElement("span");
        note.className = "scenario-note";
        note.textContent = row.note;
        cell.append(note);
      }
      tableRow.append(cell);
    });
    body.append(tableRow);
  }
}

function markerShape(x, color, dash = "solid", width = 2) {
  return {
    line: { color, dash, width },
    type: "line",
    x0: x,
    x1: x,
    xref: "x",
    y0: 0,
    y1: 1,
    yref: "paper",
  };
}

function horizontalShape(y, color, dash = "dot", width = 1) {
  return {
    line: { color, dash, width },
    type: "line",
    x0: 0,
    x1: 1,
    xref: "paper",
    y0: y,
    y1: y,
    yref: "y",
  };
}

const COMPACT_PLOT_MAX_WIDTH = 480;

function availablePlotWidth(plot) {
  const renderedWidth = plot.getBoundingClientRect().width;
  if (renderedWidth > 0) {
    return renderedWidth;
  }
  const container = plot.closest(".results");
  if (!container) {
    return 0;
  }
  const style = globalThis.getComputedStyle(container);
  return Math.max(
    0,
    container.clientWidth -
      Number.parseFloat(style.paddingLeft) -
      Number.parseFloat(style.paddingRight),
  );
}

export function plotUsesCompactLayout(
  plot,
  width = availablePlotWidth(plot),
) {
  return width > 0 && width <= COMPACT_PLOT_MAX_WIDTH;
}

function criticalMarkerTrace(solutions, label, color, textPositions, compact) {
  const samePoint =
    solutions.length > 1 &&
    solutions.every(
      (solution) =>
        solution.critical_effect_display ===
        solutions[0].critical_effect_display,
    );
  const points = samePoint ? [solutions[0]] : solutions;
  return {
    hovertemplate:
      "%{text}<br>Effect: %{x:.6g}<br>Achieved: %{y:.3%}<extra></extra>",
    marker: {
      color,
      line: { color: "#ffffff", width: 1 },
      size: 10,
      symbol: "circle",
    },
    mode: compact ? "markers" : "markers+text",
    name: label,
    showlegend: compact,
    text: points.map((solution) =>
      samePoint ? `${label} (both directions)` : `${label} (${solution.direction})`,
    ),
    textfont: { color, size: 11 },
    textposition: samePoint ? "top center" : textPositions.slice(0, points.length),
    type: "scatter",
    x: points.map((solution) => solution.critical_effect_display),
    y: points.map((solution) => solution.achieved_probability),
  };
}

export async function renderPlot(response, plot, options = {}) {
  if (!globalThis.Plotly) {
    throw new Error("The plotting library did not load.");
  }
  const curve = response.probability_curve;
  const multiplier = response.precision.information_multiplier;
  const samePrecision =
    response.precision.current_se_working === response.precision.scenario_se_working;
  const compact = options.compact ?? plotUsesCompactLayout(plot);
  const renderMode = options.renderMode ?? "live";
  const renderHeight = options.height ?? (compact ? 700 : 620);
  const renderWidth = options.width ?? null;
  const traces = [
    {
      hovertemplate:
        `${response.meta.effect_label}: %{x:.6g}<br>` +
        "Current probability: %{y:.3%}<extra></extra>",
      line: { color: "#145e6b", width: 3 },
      mode: "lines",
      name: "Current precision",
      type: "scatter",
      x: curve.true_effect_display,
      y: curve.current_selected_claim_probability,
    },
  ];
  if (!samePrecision) {
    traces.push({
      hovertemplate:
        `${response.meta.effect_label}: %{x:.6g}<br>` +
        `${multiplier}x-information probability: %{y:.3%}<extra></extra>`,
      line: { color: "#9b4d00", dash: "dash", width: 3 },
      mode: "lines",
      name: `${formatNumber(multiplier)}x information`,
      type: "scatter",
      x: curve.true_effect_display,
      y: curve.scenario_selected_claim_probability,
    });
  }
  traces.push(
    criticalMarkerTrace(
      curve.markers.current_critical,
      "Exact current",
      "#145e6b",
      ["top right", "top left"],
      compact,
    ),
  );
  if (!samePrecision) {
    traces.push(
      criticalMarkerTrace(
        curve.markers.scenario_critical,
        `Exact ${formatNumber(multiplier)}x info`,
        "#9b4d00",
        ["bottom left", "bottom right"],
        compact,
      ),
    );
  }
  traces.push({
    hovertemplate: "Null: %{x:.6g}<br>Probability: %{y:.3%}<extra></extra>",
    marker: { color: "#17202a", size: 9, symbol: "x" },
    mode: compact ? "markers" : "markers+text",
    name: "Null",
    showlegend: compact,
    text: ["Null"],
    textfont: { color: "#17202a", size: 11 },
    textposition: "top center",
    type: "scatter",
    x: [curve.markers.null_display],
    y: [response.rule.alpha],
  });
  const meaningful = response.reference_effects.meaningful_effect_optional;
  if (meaningful !== null) {
    traces.push({
      hovertemplate:
        "Meaningful scenario: %{x:.6g}<br>Current probability: %{y:.3%}<extra></extra>",
      marker: { color: "#477a1f", size: 9, symbol: "diamond" },
      mode: compact ? "markers" : "markers+text",
      name: "Meaningful scenario",
      showlegend: compact,
      text: ["Meaningful scenario"],
      textfont: { color: "#365f17", size: 11 },
      textposition: "bottom left",
      type: "scatter",
      x: [meaningful.effect_display],
      y: [meaningful.current_selected_claim_probability],
    });
  }

  const shapes = [
    horizontalShape(response.rule.target_probability, "#9b1c31", "dash", 2),
    ...response.reference_effects.probabilities.map((probability) =>
      horizontalShape(probability, "#9aa6aa", "dot", 1),
    ),
  ];
  const annotations = [
    {
      font: { color: "#9b1c31", size: 12 },
      showarrow: false,
      text: `Target ${formatProbability(response.rule.target_probability)}`,
      x: 1,
      xanchor: "right",
      xref: "paper",
      y: response.rule.target_probability,
      yanchor: "bottom",
      yref: "y",
    },
  ];
  const ci = curve.reported_ci_context_optional;
  if (ci) {
    shapes.unshift({
      fillcolor: "rgba(83, 100, 107, 0.14)",
      line: { width: 0 },
      type: "rect",
      x0: ci.lower_display,
      x1: ci.upper_display,
      xref: "x",
      y0: 0,
      y1: 1,
      yref: "paper",
    });
    const ciCenter =
      curve.axis_spacing === "log"
        ? Math.sqrt(ci.lower_display * ci.upper_display)
        : (ci.lower_display + ci.upper_display) / 2;
    annotations.push({
      bgcolor: "rgba(255,255,255,0.78)",
      bordercolor: "#849196",
      borderpad: 3,
      font: { color: "#53646b", size: 11 },
      showarrow: false,
      text: compact ? "Reported 95% CI<br>context" : "Reported 95% CI context",
      x: curve.axis_spacing === "log" ? Math.log10(ciCenter) : ciCenter,
      xref: "x",
      y: 0.99,
      yanchor: "top",
      yref: "paper",
    });
  }

  shapes.push(markerShape(curve.markers.null_display, "#17202a", "solid", 2));
  for (const solution of curve.markers.current_critical) {
    shapes.push(
      markerShape(solution.critical_effect_display, "#145e6b", "solid", 2),
    );
  }
  if (!samePrecision) {
    for (const solution of curve.markers.scenario_critical) {
      shapes.push(
        markerShape(solution.critical_effect_display, "#9b4d00", "dash", 2),
      );
    }
  }
  if (curve.markers.meaningful_effect_display_optional !== null) {
    shapes.push(
      markerShape(
        curve.markers.meaningful_effect_display_optional,
        "#477a1f",
        "dot",
        2,
      ),
    );
  }
  if (curve.markers.observed_estimate_display_optional !== null) {
    shapes.push(
      markerShape(
        curve.markers.observed_estimate_display_optional,
        "#6b4c8a",
        "dashdot",
        2,
      ),
    );
    annotations.push(
      {
        arrowcolor: "#5a3e75",
        arrowhead: 0,
        ax: 0,
        ay: compact ? -42 : 28,
        bgcolor: "rgba(255,255,255,0.82)",
        bordercolor: "#6b4c8a",
        borderpad: 3,
        font: { color: "#5a3e75", size: 11 },
        showarrow: true,
        text: compact ? "Observed estimate<br>(context only)" : "Observed estimate (context only)",
        x:
          curve.axis_spacing === "log"
            ? Math.log10(curve.markers.observed_estimate_display_optional)
            : curve.markers.observed_estimate_display_optional,
        xref: "x",
        y: 0.08,
        yref: "paper",
      },
    );
  }

  const layout = {
    annotations,
    autosize: renderWidth === null,
    height: renderHeight,
    hovermode: "x unified",
    legend: {
      bgcolor: "rgba(255,255,255,0.86)",
      bordercolor: "#bcc8cc",
      borderwidth: 1,
      orientation: "h",
      x: 0.02,
      xanchor: "left",
      y: compact ? 1.03 : 0.98,
      yanchor: compact ? "bottom" : "top",
    },
    margin: compact
      ? { b: 80, l: 58, r: 16, t: 176 }
      : { b: 80, l: 72, r: 28, t: 84 },
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    shapes,
    title: {
      font: compact ? { size: 16 } : undefined,
      text: compact
        ? "Exact selected-claim probability<br>across assumed true effects"
        : "Exact selected-claim probability across assumed true effects",
      x: 0.5,
      y: compact ? 0.98 : undefined,
      yanchor: compact ? "top" : undefined,
      yref: compact ? "container" : undefined,
    },
    xaxis: {
      gridcolor: "#dce3e5",
      range:
        curve.axis_spacing === "log"
          ? [Math.log10(curve.display_min), Math.log10(curve.display_max)]
          : [curve.display_min, curve.display_max],
      type: curve.axis_spacing === "log" ? "log" : "linear",
      title: { text: `${response.meta.effect_label} (assumed true effect)` },
    },
    yaxis: {
      gridcolor: "#dce3e5",
      range: [0, 1],
      tickformat: ".0%",
      title: { text: "Exact selected-claim probability" },
    },
  };
  if (renderWidth !== null) {
    layout.width = renderWidth;
  }
  await globalThis.Plotly.react(
    plot,
    traces,
    layout,
    {
      displaylogo: false,
      displayModeBar: compact ? false : "hover",
      responsive: renderMode === "live",
      scrollZoom: false,
    },
  );
  plot.dataset.compact = String(compact);
  plot.dataset.renderMode = renderMode;
}

export async function renderResult(response, elements) {
  const current = response.critical_effect.current;
  const scenario = response.critical_effect.scenario;
  elements.conditioning.textContent = response.meta.conditioning_statement;
  elements.summary.textContent =
    `At current SE ${formatNumber(current.standard_error_working)}, the exact ` +
    `${formatProbability(response.rule.target_probability)} critical effect(s) are ` +
    `${solutionText(current.solutions)}.`;
  elements.precision.textContent =
    `Current working-scale SE: ${formatNumber(response.precision.current_se_working)}. ` +
    `Scenario SE: ${formatNumber(response.precision.scenario_se_working)} at ` +
    `${formatNumber(response.precision.information_multiplier)}x information. ` +
    response.precision.source_note;
  elements.rule.textContent =
    `${response.rule.label}; alpha ${formatNumber(response.rule.alpha)}; target ` +
    `${formatProbability(response.rule.target_probability)}. ${response.rule.explanation}`;
  elements.currentCritical.textContent = solutionText(current.solutions);
  elements.scenarioCritical.textContent = solutionText(scenario.solutions);

  if (response.legacy_benchmark_optional === null) {
    elements.legacySection.hidden = true;
    elements.legacy.textContent = "";
  } else {
    const legacy = response.legacy_benchmark_optional;
    elements.legacySection.hidden = false;
    elements.legacy.textContent =
      `${legacy.applicability} Current working-scale distance ` +
      `${formatNumber(legacy.current.working_distance_from_null)}; exact current distance ` +
      `${formatNumber(current.solutions[0].working_distance_from_null)}. ` +
      legacy.not_exact_note;
  }

  const meaningful = response.reference_effects.meaningful_effect_optional;
  if (meaningful === null) {
    elements.meaningfulSection.hidden = true;
    elements.meaningful.textContent = "";
  } else {
    elements.meaningfulSection.hidden = false;
    elements.meaningful.textContent =
      `At ${formatNumber(meaningful.effect_display)}, exact selected-claim probability is ` +
      `${formatProbability(meaningful.current_selected_claim_probability)} with current ` +
      `precision and ${formatProbability(meaningful.scenario_selected_claim_probability)} ` +
      `under the information scenario. ${meaningful.note}`;
  }

  renderReferenceRows(response, elements.table);
  elements.warnings.replaceChildren();
  for (const warning of response.warnings) {
    const item = document.createElement("li");
    item.textContent = warning;
    elements.warnings.append(item);
  }
  elements.caption.textContent = response.meta.caption;
  await renderPlot(response, elements.plot);
}
