const STORAGE_KEY = "theme"; // 'light' | 'dark'

export function getStoredTheme() {
  try { return localStorage.getItem(STORAGE_KEY) || null; } catch { return null; }
}
export function storeTheme(value) {
  try {
    if (!value) localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, value);
  } catch {}
}

/** Read explicit attr only (may be null) */
export function getAttrTheme() {
  return document.documentElement.getAttribute("data-theme"); // 'light' | 'dark' | null
}

/** System preference (for auto mode) */
export function getSystemTheme() {
  if (!window.matchMedia) return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/** What the user is *actually seeing* right now */
export function getEffectiveTheme() {
  const attr = getAttrTheme();
  return attr || getSystemTheme(); // if no attr → auto→system
}

/** Apply/remove explicit theme */
export function applyTheme(theme /* 'light' | 'dark' | null */) {
  const root = document.documentElement;
  if (!theme) root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", theme);
}

/**
 * Toggle to the opposite of what the user currently sees.
 * If first click and in auto-dark, it will switch to light (and persist).
 */
export function toggleThemeSmart() {
  const currentEffective = getEffectiveTheme(); // 'light' | 'dark'
  const next = currentEffective === "dark" ? "light" : "dark";
  applyTheme(next);
  storeTheme(next);
  return next;
}

/** Optional: clear explicit theme → return to auto (system) */
export function clearThemePreference() {
  storeTheme(null);
  applyTheme(null);
}