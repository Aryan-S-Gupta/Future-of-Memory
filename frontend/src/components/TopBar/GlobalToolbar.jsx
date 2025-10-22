import React, { useEffect, useState, useMemo } from "react";
import { useBgm } from "../../audio/AudioProvider";
import "../../styles/GlobalToolbar.css";
import { toggleTheme, getEffectiveTheme, getAttrTheme, onSystemThemeChange } from "../../theme/theme";

// Icons (inline SVGs)
const IconVolume = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="lucide lucide-volume-2">
        <path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z" />
        <path d="M16 9a5 5 0 0 1 0 6" />
        <path d="M19.364 18.364a9 9 0 0 0 0-12.728" />
    </svg>
);
const IconVolumeMute = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="lucide lucide-volume-x">
        <path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z" />
        <line x1="22" x2="16" y1="9" y2="15" />
        <line x1="16" x2="22" y1="9" y2="15" />
    </svg>
);
const IconPlay = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="lucide lucide-circle-play">
        <path d="M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z" />
        <circle cx="12" cy="12" r="10" />
    </svg>
);
const IconPause = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="lucide lucide-circle-pause">
        <circle cx="12" cy="12" r="10" />
        <line x1="10" x2="10" y1="15" y2="9" />
        <line x1="14" x2="14" y1="15" y2="9" />
    </svg>
);
const IconTextSize = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="lucide lucide-a-large-small">
        <path d="m15 16 2.536-7.328a1.02 1.02 0 0 1 1.928 0L22 16" />
        <path d="M15.697 14h5.606" />
        <path d="m2 16 4.039-9.69a.5.5 0 0 1 .923 0L11 16" />
        <path d="M3.304 13h6.392" />
    </svg>
);
const IconMoon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="lucide lucide-moon-star">
        <path d="M18 5h4" /><path d="M20 3v4" />
        <path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401" />
    </svg>
);
const IconSun = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="lucide lucide-sun">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2" /><path d="M12 20v2" />
        <path d="m4.93 4.93 1.41 1.41" />
        <path d="m17.66 17.66 1.41 1.41" />
        <path d="M2 12h2" /><path d="M20 12h2" />
        <path d="m6.34 17.66-1.41 1.41" />
        <path d="m19.07 4.93-1.41 1.41" />
    </svg>
);
const IconHamburger = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
        xmlns="http://www.w3.org/2000/svg" stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round">
        <line x1="4" y1="6.5" x2="20" y2="6.5" />
        <line x1="4" y1="12" x2="20" y2="12" />
        <line x1="4" y1="17.5" x2="20" y2="17.5" />
    </svg>
);
const IconClose = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
        xmlns="http://www.w3.org/2000/svg" stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
);

/* Constants: Text zoom persistence + limits */
const TEXT_ZOOM_KEY = "textZoom";
const ZMIN = 0.85, ZMAX = 1.35, ZSTEP = 0.05, ZDEFAULT = 1;


/**
 * GlobalToolbar component
 *
 * Renders a horizontal toolbar with audio and appearance controls.
 * Audio: mute toggle, play/pause, volume slider
 * Appearance: text size (A− / reset / A+), theme toggle
 */
export default function GlobalToolbar() {
    const { isMuted, volume, play, pause, mute, unmute, setVolume } = useBgm();
    // Track theme (dark/light/auto)
    const [effectiveTheme, setEffectiveTheme] = useState(getEffectiveTheme());
    /** Toggle between muted/unmuted state */
    const onToggleMute = () => {
        if (isMuted) {         // going to UNMUTE
            unmute();
            window.dispatchEvent(new Event("tts-enable"));
        } else {
            mute();
        }
    };

    // text zoom
    const initialZoom = useMemo(() => {
        const saved = parseFloat(localStorage.getItem(TEXT_ZOOM_KEY) || String(ZDEFAULT));
        return Number.isFinite(saved) ? Math.min(ZMAX, Math.max(ZMIN, saved)) : ZDEFAULT;
    }, []);
    const [textZoom, setTextZoom] = useState(initialZoom);

    const [open, setOpen] = useState(false);
    const toggleOpen = () => setOpen(o => !o);

    //Apply and persist zoom level.
    const applyZoom = (z) => {
        const clamped = Math.min(ZMAX, Math.max(ZMIN, z));
        setTextZoom(clamped);
        document.documentElement.style.setProperty("--text-zoom", String(clamped));
        localStorage.setItem(TEXT_ZOOM_KEY, String(clamped));
    };

    // Initialize zoom once on mount
    useEffect(() => { applyZoom(initialZoom); /* on mount */ }, [initialZoom]);

    // Sync theme with system changes (only if AUTO is active)
    useEffect(() => {
        const off = onSystemThemeChange((sys) => { if (!getAttrTheme()) setEffectiveTheme(sys); });
        return off;
    }, []);

    useEffect(() => {
        if (!open) return;
        const onKey = (e) => { if (e.key === "Escape") setOpen(false); };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [open]);

    // Render
    return (
        <div className={`gtb-shell ${open ? "is-open" : "is-collapsed"}`} data-open={open ? "true" : "false"}>
            {/* Square hamburger trigger (no duplicate content) */}
            <button
                type="button"
                className="gtb-ham"
                aria-label={open ? "Close menu" : "Open menu"}
                aria-expanded={open}
                aria-controls="gtb-panel"
                onClick={toggleOpen}
            >
                <span className="gtb-ham-ico">{open ? <IconClose /> : <IconHamburger />}</span>
            </button>

            {/* Sliding panel with your existing toolbar content */}
            <div id="gtb-panel" className="gtb" role="toolbar" aria-label="Global toolbar">
                {/* AUDIO CONTROLS */}
                <div className="gtb-group" aria-label="Audio">
                    {/* Mute/unmute toggle */}
                    <button type="button" className="gtb-btn" onClick={onToggleMute}
                        aria-pressed={isMuted} aria-label={isMuted ? "Unmute" : "Mute"} title={isMuted ? "Unmute" : "Mute"}>
                        {isMuted ? <IconVolumeMute /> : <IconVolume />}
                    </button>

                    {/* Play / Pause buttons */}
                    <div className="gtb-seg">
                        <button type="button" className="gtb-btn" onClick={play} aria-label="Play" title="Play"><IconPlay /></button>
                        <button type="button" className="gtb-btn" onClick={pause} aria-label="Pause" title="Pause"><IconPause /></button>
                    </div>

                    {/* Volume slider */}
                    <label className="gtb-slider-label" aria-label="Volume">
                        <input
                            className="gtb-slider"
                            type="range"
                            min="0"
                            max="1"
                            step="0.01"
                            value={isMuted ? 0 : volume}
                            onChange={(e) => setVolume(parseFloat(e.target.value))}
                        />
                    </label>
                </div>

                {/* APPEARANCE CONTROLS */}
                <div className="gtb-group" aria-label="Appearance">
                    {/* Text size controls */}
                    <div className="gtb-textsize" aria-label="Text size">
                        <button type="button" className="gtb-btn" title="Smaller text" aria-label="Smaller text"
                            onClick={() => applyZoom(textZoom - ZSTEP)}>A−</button>

                        <button type="button" className="gtb-btn" title="Reset text size" aria-label="Reset text size"
                            onClick={() => applyZoom(ZDEFAULT)}><IconTextSize /></button>

                        <button type="button" className="gtb-btn" title="Larger text" aria-label="Larger text"
                            onClick={() => applyZoom(textZoom + ZSTEP)}>A+</button>
                    </div>

                    {/* Theme toggle (light/dark) */}
                    <button type="button" className="gtb-btn" aria-label="Toggle theme" title="Toggle theme"
                        onClick={() => setEffectiveTheme(toggleTheme())}>
                        {effectiveTheme === "dark" ? <IconMoon /> : <IconSun />}
                    </button>
                </div>
            </div>
        </div>
    );
}