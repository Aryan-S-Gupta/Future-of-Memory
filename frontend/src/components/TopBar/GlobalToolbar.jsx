// frontend/src/components/TopBar/GlobalToolbar.jsx
import React, { useEffect, useState } from "react";
import { useBgm } from "../../audio/AudioProvider";
import "../../styles/GlobalToolbar.css";
import { toggleTheme, getEffectiveTheme, getAttrTheme, onSystemThemeChange } from "../../theme/theme";

// Volume (speaker) + waves
const IconVolume = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-volume2-icon lucide-volume-2"><path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z" /><path d="M16 9a5 5 0 0 1 0 6" /><path d="M19.364 18.364a9 9 0 0 0 0-12.728" /></svg>
);

// Muted (speaker with slash)
const IconVolumeMute = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-volume-x-icon lucide-volume-x"><path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z" /><line x1="22" x2="16" y1="9" y2="15" /><line x1="16" x2="22" y1="9" y2="15" /></svg>
);

// Play / Pause
const IconPlay = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-play-icon lucide-circle-play"><path d="M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z" /><circle cx="12" cy="12" r="10" /></svg>
);
const IconPause = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-pause-icon lucide-circle-pause"><circle cx="12" cy="12" r="10" /><line x1="10" x2="10" y1="15" y2="9" /><line x1="14" x2="14" y1="15" y2="9" /></svg>
);

// “A” size (text) – placeholder
const IconTextSize = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-alarge-small-icon lucide-a-large-small"><path d="m15 16 2.536-7.328a1.02 1.02 1 0 1 1.928 0L22 16" /><path d="M15.697 14h5.606" /><path d="m2 16 4.039-9.69a.5.5 0 0 1 .923 0L11 16" /><path d="M3.304 13h6.392" /></svg>
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
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-moon-star-icon lucide-moon-star"><path d="M18 5h4" /><path d="M20 3v4" /><path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401" /></svg>
                    ) : (
                        // Sun (light)
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sun-icon lucide-sun"><circle cx="12" cy="12" r="4" /><path d="M12 2v2" /><path d="M12 20v2" /><path d="m4.93 4.93 1.41 1.41" /><path d="m17.66 17.66 1.41 1.41" /><path d="M2 12h2" /><path d="M20 12h2" /><path d="m6.34 17.66-1.41 1.41" /><path d="m19.07 4.93-1.41 1.41" /></svg>
                    )}
                </button>

            </div>
        </div>
    );
}