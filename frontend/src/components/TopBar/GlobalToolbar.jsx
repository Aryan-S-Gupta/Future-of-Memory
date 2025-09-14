// frontend/src/components/TopBar/GlobalToolbar.jsx
import React, { useEffect, useState } from "react";
import { useBgm } from "../../audio/AudioProvider";
import "../../styles/GlobalToolbar.css";
import { toggleTheme, getEffectiveTheme, getAttrTheme, onSystemThemeChange } from "../../theme/theme";


/* --- Inline icon set (stroke-based, futuristic, no fonts/emojis) --- */
const Icon = ({ d, viewBox = "0 0 24 24", strokeWidth = 1.8 }) => (
    <svg className="gtb-icon" viewBox={viewBox} aria-hidden="true">
        <path d={d} fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

// Volume (speaker) + waves
const IconVolume = () => (
    <svg className="gtb-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M4 10v4h3l5 4V6l-5 4H4z" fill="currentColor" />
        <path d="M16 8c1.5 1.2 1.5 6.8 0 8M18.5 5.5c3 2.4 3 10.6 0 13" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
);

// Muted (speaker with slash)
const IconVolumeMute = () => (
    <svg className="gtb-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M4 10v4h3l5 4V6l-5 4H4z" fill="currentColor" />
        <path d="M19 5L5 19" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
);

// Play / Pause
const IconPlay = () => <Icon d="M8 5l10 7-10 7z" />;
const IconPause = () => (
    <svg className="gtb-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M8 5h3v14H8zM13 5h3v14h-3z" fill="currentColor" />
    </svg>
);

// “A” size (text) – placeholder
const IconTextSize = () => (
    <svg className="gtb-icon" viewBox="0 0 24 24" aria-hidden="true">
        <text x="4" y="18" fontSize="16" fontFamily="Orbitron, sans-serif" fill="currentColor">A</text>
    </svg>
);

// Theme (sun/moon hybrid) – placeholder
const IconTheme = () => (
    <svg className="gtb-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 3a9 9 0 109 9A7 7 0 0112 3z" fill="none" stroke="currentColor" strokeWidth="1.8" />
    </svg>
);

export default function GlobalToolbar() {
    const { isMuted, volume, play, pause, mute, unmute, setVolume } = useBgm();
    const onToggleMute = () => (isMuted ? unmute() : mute());
    const [effectiveTheme, setEffectiveTheme] = useState(getEffectiveTheme());

    // When user is in AUTO (no data-theme), reflect system changes in the icon:
    useEffect(() => {
        const off = onSystemThemeChange((sys) => {
            if (!getAttrTheme()) setEffectiveTheme(sys);
        });
        return off;
    }, []);

    return (
        <div className="gtb" role="toolbar" aria-label="Global toolbar">
            {/* AUDIO */}
            <div className="gtb-group" aria-label="Audio controls">
                <button
                    type="button"
                    className="gtb-btn"
                    onClick={onToggleMute}
                    aria-pressed={isMuted}
                    aria-label={isMuted ? "Unmute" : "Mute"}
                    title={isMuted ? "Unmute" : "Mute"}
                >
                    {isMuted ? <IconVolumeMute /> : <IconVolume />}
                </button>

                <button
                    type="button"
                    className="gtb-btn"
                    onClick={play}
                    aria-label="Play background music"
                    title="Play"
                >
                    <IconPlay />
                </button>

                <button
                    type="button"
                    className="gtb-btn"
                    onClick={pause}
                    aria-label="Pause background music"
                    title="Pause"
                >
                    <IconPause />
                </button>

                <label className="gtb-slider-label">
                    <span className="sr-only">Volume</span>
                    <input
                        className="gtb-slider"
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={isMuted ? 0 : volume}
                        onChange={(e) => setVolume(parseFloat(e.target.value))}
                        aria-label="Volume"
                    />
                </label>
            </div>

            {/* PLACEHOLDERS (future) */}
            <div className="gtb-group" aria-label="Appearance and accessibility">
                <button
                    type="button"
                    className="gtb-btn gtb-btn-placeholder"
                    aria-label="Text size"
                    title="Text size"
                    disabled
                >
                    <IconTextSize />
                </button>

                <button
                    type="button"
                    className="gtb-btn"
                    aria-label="Toggle theme"
                    title="Toggle theme"
                    onClick={() => setEffectiveTheme(toggleTheme())} // flips what you SEE now; first-click works
                >
                    {effectiveTheme === "dark" ? (
                        // Moon (dark)
                        <svg className="gtb-icon" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z" fill="none" stroke="currentColor" strokeWidth="1.8" />
                        </svg>
                    ) : (
                        // Sun (light)
                        <svg className="gtb-icon" viewBox="0 0 24 24" aria-hidden="true">
                            <circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" strokeWidth="1.8" />
                            <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" strokeWidth="1.8" />
                        </svg>
                    )}
                </button>

            </div>
        </div>
    );
}