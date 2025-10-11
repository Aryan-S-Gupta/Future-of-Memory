// audio/AudioProvider.jsx
import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

const BgmContext = createContext(null); //Global State management
export const useBgm = () => useContext(BgmContext); // Access control & state, inside children component (Hook) - optional

// Example: const { mute, unmute, setVolume, play, pause } = useBgm(); - for user buttons in future

const clamp01 = (v) => Math.max(0, Math.min(1, Number.isFinite(v) ? v : 0)); //check validity (Not hardcode)

// Provides Context - single <audio> element and manage bgm based on route
export default function AudioProvider({ children, routeAudioMap, initialVolume = 0.35 }) {
    const location = useLocation(); // See route changes
    const audioRefs = useRef([]);

    // Track current loudness (volume), muted state, and which track is playing
    const [volume, setVolume] = useState(clamp01(initialVolume));
    const [isMuted, setIsMuted] = useState(false);
    const [currentSrc, setCurrentSrc] = useState(null);

    // NEW: simple “is audio playing?” state (kept minimal)
    const [isPlaying, setIsPlaying] = useState(false);

    // Flag - if user interacted (true for autoplay) - can be changed
    const hasUserInteracted = true;

    // Multi-track: don’t pre-create a single <audio>.
    // Ensure the ref is an array; actual players are created in the route effect.
    if (!audioRefs.current) {
        audioRefs.current = [];
    }

    // Decide what music to play for the current route
    const trackFor = useMemo(() => {
        const entries = Object.entries(routeAudioMap || {});
        return (p) => {
            const exact = entries.find(([k]) => k === p)?.[1];
            if (exact) return exact;
            const pref = entries.find(([k]) => k.endsWith("*") && p.startsWith(k.slice(0, -1)))?.[1];
            if (pref) return pref;
            return entries.find(([k]) => k === "*")?.[1] ?? null;
        };
    }, [routeAudioMap]);

    // Whenever the page changes, check if we need to change the track
    useEffect(() => {
        const tracks = trackFor(location.pathname);

        // stop & clear old
        audioRefs.current.forEach((a) => {
            try { a.pause(); } catch { }
        });
        audioRefs.current = [];

        if (!tracks) {
            setCurrentSrc(null);
            return;
        }

        const list = Array.isArray(tracks) ? tracks : [tracks];
        const defaultGain = list.length > 1 ? 1 / list.length : 1; // e.g., 0.5 + 0.5

        list.forEach((t, idx) => {
            const a = new Audio();
            a.preload = "auto";
            a.loop = t.loop ?? true;
            a.src = t.src;
            // store per-track gain on the element
            a._gain = Number.isFinite(t.gain) ? t.gain : defaultGain;
            // apply initial volume (master * gain, respecting mute)
            a.volume = isMuted ? 0 : clamp01(volume * a._gain);
            // basic play/pause listeners update isPlaying
            const update = () => setIsPlaying(audioRefs.current.some(el => !el.paused && !el.ended));
            a.addEventListener("play", update);
            a.addEventListener("pause", update);
            a.addEventListener("ended", update);
            a.play().catch(() => { });
            audioRefs.current.push(a);
        });

        // keep a simple currentSrc for debugging/consumers (first track)
        const first = list[0];
        setCurrentSrc(first?.src ?? null);
    }, [location.pathname, trackFor/* keep dependencies minimal */, /* remove currentSrc here */]);

    // Keep the actual audio element volume in sync with state
    useEffect(() => {
        audioRefs.current.forEach((a) => {
            const g = Number.isFinite(a._gain) ? a._gain : 1;
            a.volume = isMuted ? 0 : clamp01(volume * g);
        });
    }, [isMuted, volume]);

    // Common control for all pages
    const controls = useMemo(() => ({
        // Manually start music
        play: () => {
            const ps = audioRefs.current.map(a => a.play().catch(() => { }));
            // NEW: dispatch a tiny event so screens can “replay narration” on Play press
            try { window.dispatchEvent(new CustomEvent("bgm-play")); } catch { }
            return Promise.allSettled(ps);
        },
        // Manually pause music
        pause: () => audioRefs.current.forEach(a => a.pause()),
        // Change loudness (0 = silent, 1 = max)
        setVolume: (v) => setVolume(clamp01(v)),
        // Instantly mute/unmute
        mute: () => setIsMuted(true),
        unmute: () => {
            setIsMuted(false);
            // ensure background resumes if any track got paused
            audioRefs.current.forEach(a => {
                if (a && a.paused) {
                    a.play().catch(() => { });
                }
            });
        },

        isMuted,// Current mute state (true/false)
        volume, // Current volume (number between 0–1)
        currentSrc, // File currently playing
        hasUserInteracted, // Always true here, left for consistency
        // NEW: expose playing state
        isPlaying,
    }), [isMuted, volume, currentSrc, isPlaying]);

    // Give access to these controls to the rest of the app (wrapper)
    return <BgmContext.Provider value={controls}>{children}</BgmContext.Provider>;
}