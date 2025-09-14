// frontend/src/theme/theme.js
const KEY = "theme"; // 'light' | 'dark' | null
const isTheme = (v) => v === "light" || v === "dark";
const root = document.documentElement;
const mqd = window.matchMedia?.("(prefers-color-scheme: dark)");

const getSystem = () => (mqd?.matches ? "dark" : "light");
export const getAttrTheme = () => root.getAttribute("data-theme");              // 'light' | 'dark' | null
export const getEffectiveTheme = () => getAttrTheme() || getSystem();           // what’s visible now

const applyAttr = (v) => (isTheme(v) ? root.setAttribute("data-theme", v)
    : root.removeAttribute("data-theme"));    // null => AUTO

const readStore = () => {
    try { const v = localStorage.getItem(KEY); return isTheme(v) ? v : null; } catch { return null; }
};
const writeStore = (v) => { try { isTheme(v) ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY); } catch { } };

export const setTheme = (v /* 'light'|'dark'|null */) => { applyAttr(v); writeStore(v); return v ?? "auto"; };

export const toggleTheme = () => {
    const next = getEffectiveTheme() === "dark" ? "light" : "dark";
    applyAttr(next); writeStore(next); return next;
};

export const cycleTheme = () => {
    const a = getAttrTheme();
    const next = a === null ? "dark" : a === "dark" ? "light" : null;
    applyAttr(next); writeStore(next);
    return { explicit: next, effective: next || getSystem(), mode: next || "auto" };
};

export const initTheme = () => applyAttr(readStore()); // call once on load if you want to restore

export const onSystemThemeChange = (cb /* ( 'dark'|'light' ) => void */) => {
    if (!mqd) return () => { };
    const h = () => cb(mqd.matches ? "dark" : "light");
    mqd.addEventListener?.("change", h) || mqd.addListener?.(h);
    return () => mqd.removeEventListener?.("change", h) || mqd.removeListener?.(h);
};