import { useEffect, useRef, useState } from "react";

/**
 * useIdle
 * ---------------------
 * Custom React hook for detecting user inactivity.
 *
 * Features:
 * - Triggers `onIdle()` after a specified idle duration (`idleMs`).
 * - Triggers `onActive()` once activity resumes.
 * - Returns a boolean `isIdle` to indicate the current state.
 *
 * Useful for:
 * - Auto-dismissing modals
 * - Showing screensavers
 * - Resetting apps to a home screen after inactivity
 */
export default function useIdle({ idleMs = 60000, onIdle, onActive } = {}) {
    const [isIdle, setIsIdle] = useState(false); // track idle state
    const timerRef = useRef(null); // reference to inactivity timer

    // Keep the latest callback references without reattaching listeners
    const onIdleRef = useRef(onIdle);
    const onActiveRef = useRef(onActive);
    useEffect(() => { onIdleRef.current = onIdle; }, [onIdle]);
    useEffect(() => { onActiveRef.current = onActive; }, [onActive]);

    useEffect(() => {
        const ac = new AbortController(); // cleanup helper for all listeners
        const { signal } = ac;

        /**
         * Starts (or restarts) the inactivity timer.
         * Once `idleMs` has passed with no events, mark as idle.
         */
        const startTimer = () => {
            clearTimeout(timerRef.current);
            timerRef.current = setTimeout(() => {
                setIsIdle(true);
                onIdleRef.current && onIdleRef.current();
            }, idleMs);
        };

        /**
         * Resets the idle timer whenever user activity is detected.
         * If the user was idle, marks as active again.
         */
        const reset = () => {
            clearTimeout(timerRef.current);
            if (isIdle) {
                setIsIdle(false);
                onActiveRef.current && onActiveRef.current();
            }
            startTimer();
        };

        /**
         * Handles visibility change — if the tab regains focus,
         * reset the idle timer to prevent false idle triggers.
         */
        const onVisibility = () => {
            if (!document.hidden) reset();
        };

        // User activity events that should reset the idle timer
        const events = ["pointermove", "pointerdown", "keydown", "wheel", "touchstart"];
        events.forEach(e =>
            window.addEventListener(e, reset, { passive: true, signal })
        );
        document.addEventListener("visibilitychange", onVisibility, { signal });

        // Start initial timer on mount
        startTimer();

        // Cleanup all listeners and timers when unmounted
        return () => {
            ac.abort();
            clearTimeout(timerRef.current);
        };
    }, [idleMs, isIdle]);

    // Expose current idle state to parent components
    return isIdle;
}