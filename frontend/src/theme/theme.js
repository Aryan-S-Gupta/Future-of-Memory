// frontend/src/theme/theme.js
const KEY = "theme"; // 'light' | 'dark' | null
const isTheme = (v) => v === "light" || v === "dark";
const root = () => document.documentElement;
const mq = () => window.matchMedia?.("(prefers-color-scheme: dark)");

/* ----- system / effective ----- */
export const getSystemTheme = () =>
    mq()?.matches ? "dark" : "light";

export const getAttrTheme = () =>
    root().getAttribute("data-theme"); // 'light' | 'dark' | null

export const getEffectiveTheme = () =>
    getAttrTheme() || getSystemTheme();

/* ----- storage ----- */
export const getStoredTheme = () => {
    try {
        const v = localStorage.getItem(KEY);
        return isTheme(v) ? v : null;
    } catch {
        return null;
    }
};

export const setStoredTheme = (v /* 'light' | 'dark' | null */) => {
    try {
        isTheme(v) ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY);
    } catch { }
};

/* ----- apply/remove attribute (explicit theme) ----- */
export const applyTheme = (v /* 'light' | 'dark' | null */) => {
    isTheme(v) ? root().setAttribute("data-theme", v)
        : root().removeAttribute("data-theme"); // AUTO
};

/* ----- actions ----- */
export const toggleTheme = () => {
    const next = getEffectiveTheme() === "dark" ? "light" : "dark";
    applyTheme(next);
    setStoredTheme(next);
    return next; // 'light' | 'dark'
};

export const cycleTheme = () => {
    const attr = getAttrTheme(); // explicit
    const next = attr === null ? "dark" : attr === "dark" ? "light" : null;
    applyTheme(next);
    setStoredTheme(next);
    return {
        explicit: next,                       // 'light' | 'dark' | null
        effective: next || getSystemTheme(),  // what you see now
        mode: next || "auto",
    };
};

/* ----- startup restore (optional) ----- */
export const applyStoredThemeOnLoad = () => applyTheme(getStoredTheme());

/* ----- subscribe to system changes (for AUTO UI) ----- */
export const onSystemThemeChange = (cb /* (dark|light) => void */) => {
    const m = mq();
    if (!m) return () => { };
    const handler = () => cb(m.matches ? "dark" : "light");

    // modern + legacy
    m.addEventListener?.("change", handler) || m.addListener?.(handler);

    return () => m.removeEventListener?.("change", handler) || m.removeListener?.(handler);
};