// Initialize medium zoom.
// Guardrail: a zoomed picture never grows past MAX_ZOOM px (or the window, minus a margin),
// so large high-resolution images stay sharp without filling the whole screen.
const MAX_ZOOM = 720;
const ZOOM_MARGIN = 24;

// medium-zoom's container = the whole window, with left/right/top/bottom as insets
function zoomContainer() {
  const w = document.documentElement.clientWidth;
  const h = document.documentElement.clientHeight;
  const insetX = Math.max(ZOOM_MARGIN, (w - MAX_ZOOM) / 2);
  const insetY = Math.max(ZOOM_MARGIN, (h - MAX_ZOOM) / 2);
  return { width: w, height: h, left: insetX, right: insetX, top: insetY, bottom: insetY };
}

$(document).ready(function () {
  medium_zoom = mediumZoom("[data-zoomable]", {
    background: getComputedStyle(document.documentElement).getPropertyValue("--global-bg-color") + "ee", // + 'ee' for trasparency.
    container: zoomContainer(),
  });
  window.addEventListener("resize", () => medium_zoom.update({ container: zoomContainer() }));
});
