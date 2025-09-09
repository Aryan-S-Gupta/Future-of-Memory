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
    const audioRef = useRef(null); // Single Audio Player (save reference - don't replace)

    // Track current loudness (volume), muted state, and which track is playing
    const [volume, setVolume] = useState(clamp01(initialVolume));
    const [isMuted, setIsMuted] = useState(false);
    const [currentSrc, setCurrentSrc] = useState(null);

    // Flag - if user interacted (true for autoplay) - can be changed
    const hasUserInteracted = true;

    // Setup <audio> element - first RUN
    if (!audioRef.current) {
        const el = new Audio(); //Audio Player
        el.preload = "auto"; //Avoid delayer
        el.loop = true;
        el.volume = clamp01(initialVolume); //use volume set
        audioRef.current = el; //Save reference
    }

    // Decide what music to play for the current route
    const trackFor = useMemo(() => { //cache - optimize
        const entries = Object.entries(routeAudioMap || {});
        return (p) => 
            // Check for exact path
            (entries.find(([k]) => k === p)?.[1]) ??
            // Globally - fallback
            (entries.find(([k]) => k === "*")?.[1]) ??
            // Don't play
            null;
    }, [routeAudioMap]);

    // Whenever the page changes, check if we need to change the track
    useEffect(() => { //Perform sideeffect after rendering
        const el = audioRef.current;
        const t = trackFor(location.pathname);
        if (!el) return;

        // No track - pause and clear the current song
        if (!t) {
            el.pause();
            setCurrentSrc(null);
            return;
        }

        // Different track on page
        if (t.src !== currentSrc) {
            el.src = t.src; //change source
            el.loop = t.loop ?? true; //check loop setting, else default to true
            el.play().catch(() => { }); // ignore autoplay rejection
            setCurrentSrc(t.src); // save reference for current song playing
        }
    }, [location.pathname, trackFor, currentSrc]);

    // Keep the actual audio element volume in sync with state
    useEffect(() => {
        if (audioRef.current) {
            // Apply volume / mute instantly
            audioRef.current.volume = isMuted ? 0 : clamp01(volume);
        }
    }, [isMuted, volume]);

    // Common control for all pages
    const controls = useMemo(() => ({
        play: () => audioRef.current?.play().catch(() => { }), // Manually start music
        pause: () => audioRef.current?.pause(), // Manually pause music
        setVolume: (v) => setVolume(clamp01(v)), // Change loudness (0 = silent, 1 = max)
        mute: () => setIsMuted(true), // Instantly mute
        unmute: () => setIsMuted(false), // Instantly unmute
        isMuted,// Current mute state (true/false)
        volume, // Current volume (number between 0–1)
        currentSrc, // File currently playing
        hasUserInteracted, // Always true here, left for consistency
    }), [isMuted, volume, currentSrc]);

    // Give access to these controls to the rest of the app (wrapper)
    return <BgmContext.Provider value={controls}>{children}</BgmContext.Provider>;
}