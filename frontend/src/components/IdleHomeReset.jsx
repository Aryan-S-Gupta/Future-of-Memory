import { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useIdle from "../components/useIdle.js";

/**
 * IdleHomeReset
 * --------------------
 * A lightweight utility component that automatically returns the user
 * to the home screen ("/") after a period of inactivity.
 *
 * Usage:
 *   Place this near the top level of <App /> so it runs globally.
 *   Example: <IdleHomeReset idleMs={90000} />
 *
 * - Tracks the user's last visited route.
 * - Uses a shared `useIdle` hook to detect inactivity.
 * - Automatically navigates back to home if idle time exceeds `idleMs`.
 */
export default function IdleHomeReset({ idleMs = 90000 }) {
    const { pathname } = useLocation(); // current route path
    const navigate = useNavigate(); // react-router navigation hook
    const lastPathRef = useRef(pathname); // store last known path across renders

    // Update the reference whenever the route changes
    useEffect(() => {
        lastPathRef.current = pathname;
    }, [pathname]);

    // Trigger home reset after user inactivity
    useIdle({
        idleMs,
        onIdle: () => {
            // Only redirect if not already on home route
            if (lastPathRef.current !== "/") {
                navigate("/", { replace: true }); // go home without adding history entry
            }
        },
    });

    // This component renders nothing — it only runs behaviorally in the background
    return null;
}