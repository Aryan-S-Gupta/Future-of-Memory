const STORAGE_KEY = "theme"; // 'light' | 'dark'

export function getStoredTheme() {
  try { return localStorage.getItem(STORAGE_KEY); } catch { return null; }
}
export function storeTheme(value) {
  try { localStorage.setItem(STORAGE_KEY, value); } catch {}
}

export function getSystemTheme() {
  if (typeof window === "undefined" || !window.matchMedia) return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/** Apply a theme to <html data-theme="..."> */
export function applyTheme(theme) {
  const root = document.documentElement;
  if (!theme) { root.removeAttribute("data-theme"); return; } // falls back to tokens + @media auto
  root.setAttribute("data-theme", theme);
}

/** Initialize at app start: use stored theme or system preference */
export function initTheme() {
  const stored = getStoredTheme();
  const theme = stored || null; // if null → no data-theme → your @media dark kicks in
  applyTheme(theme);
}

/** Toggle between 'light' and 'dark' explicitly */
export function toggleTheme() {
  const root = document.documentElement;
  const current = root.getAttribute("data-theme"); // 'light' | 'dark' | null
  const next = current === "dark" ? "light" : "dark";
  applyTheme(next);
  storeTheme(next);
  return next;
}

/** Optional: follow system if user clears preference */
export function clearThemePreference() {
  storeTheme("");
  applyTheme(null); // removes data-theme
}