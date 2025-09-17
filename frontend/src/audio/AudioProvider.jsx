// audio/AudioProvider.jsx
import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

const BgmContext = createContext(null);
export const useBgm = () => useContext(BgmContext);

const clamp01 = (v) => Math.max(0, Math.min(1, Number.isFinite(v) ? v : 0));

export default function AudioProvider({ children, routeAudioMap, initialVolume = 0.35 }) {
    const location = useLocation();
    const audioRef = useRef(null);
    const [volume, setVolume] = useState(clamp01(initialVolume));
    const [isMuted, setIsMuted] = useState(false);
    const [currentSrc, setCurrentSrc] = useState(null);
    const hasUserInteracted = true; // always true per your spec

    // init audio once
    if (!audioRef.current) {
        const el = new Audio();
        el.preload = "auto";
        el.loop = true;
        el.volume = clamp01(initialVolume);
        audioRef.current = el;
    }

    // resolve track for path (exact or "*")
    const trackFor = useMemo(() => {
        const entries = Object.entries(routeAudioMap || {});
        return (p) => (entries.find(([k]) => k === p)?.[1]) ?? (entries.find(([k]) => k === "*")?.[1]) ?? null;
    }, [routeAudioMap]);

    // play on mount + on route change (no fade)
    useEffect(() => {
        const el = audioRef.current;
        const t = trackFor(location.pathname);
        if (!el) return;
        if (!t) { el.pause(); setCurrentSrc(null); return; }
        if (t.src !== currentSrc) {
            el.src = t.src;
            el.loop = t.loop ?? true;
            el.play().catch(() => { }); // ignore autoplay rejection
            setCurrentSrc(t.src);
        }
    }, [location.pathname, trackFor, currentSrc]);

    // apply volume/mute instantly
    useEffect(() => {
        if (audioRef.current) audioRef.current.volume = isMuted ? 0 : clamp01(volume);
    }, [isMuted, volume]);

    const controls = useMemo(() => ({
        play: () => audioRef.current?.play().catch(() => { }),
        pause: () => audioRef.current?.pause(),
        setVolume: (v) => setVolume(clamp01(v)),
        mute: () => setIsMuted(true),
        unmute: () => setIsMuted(false),
        isMuted, volume, currentSrc, hasUserInteracted,
    }), [isMuted, volume, currentSrc]);

    return <BgmContext.Provider value={controls}>{children}</BgmContext.Provider>;
}