// medium-zoom on [data-zoomable] pictures (loaded after medium-zoom from the CDN).
// Guardrail: a zoomed picture never grows past MAX_ZOOM px (or the window, minus a margin),
// so large high-resolution images stay sharp without filling the whole screen.
// The overlay colour is set in theme/research.css (follows light/dark mode).
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

const zoom = mediumZoom("[data-zoomable]", { container: zoomContainer() });
window.addEventListener("resize", () => zoom.update({ container: zoomContainer() }));
