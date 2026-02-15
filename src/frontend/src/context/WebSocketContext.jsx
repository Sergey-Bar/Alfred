
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Provides a global React context for real-time WebSocket events from the backend. Handles connection, reconnection, and event parsing for governance workflows.
// Why: Centralizes real-time logic for push-mode UI updates and admin notifications.
// Root Cause: Scattered WebSocket logic leads to missed events and reconnection bugs.
// Context: All real-time features should use this provider and hook. Future: consider multiplexing or event bus for more event types.
// Model Suitability: For React context and WebSocket patterns, GPT-4.1 is sufficient.
import { createContext, useContext, useEffect, useRef } from 'react';
import { useToast } from './ToastContext';
import { useUser } from './UserContext';

const WebSocketContext = createContext(null);

/**
 * Real-time Event Orchestrator
 * 
 * [ARCHITECTURAL ROLE]
 * This provider establishes a persistent WebSocket connection to the Alfred 
 * backend for real-time signaling. It enables "Push-Mode" UI updates for 
 * high-priority events like governance approvals and quota warnings.
 */
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: WebSocketProvider manages connection lifecycle, reconnection, and event handling for real-time admin and governance events.
// Why: Ensures reliable delivery of push notifications and workflow events.
// Root Cause: Manual WebSocket management is error-prone and hard to scale.
// Context: Wrap the app in this provider to enable real-time features everywhere.
export function WebSocketProvider({ children }) {
    const { user } = useUser();
    const { info } = useToast();
    const socketRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);

    useEffect(() => {
        // Only establish connection for authenticated users
        if (!user) {
            if (socketRef.current) {
                socketRef.current.close();
            }
            return;
        }

        const connect = () => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            // In development (Vite), we might need to point to the backend port explicitly
            // if proxying isn't handling WebSockets correctly.
            const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
            const wsUrl = `${protocol}//${host}/ws/events/${user.id}`;

            console.log(`[WebSocket] Connecting to ${wsUrl}`);
            const socket = new WebSocket(wsUrl);
            socketRef.current = socket;

            socket.onopen = () => {
                console.log('[WebSocket] Connection established.');
                if (reconnectTimeoutRef.current) {
                    clearTimeout(reconnectTimeoutRef.current);
                }
            };

            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    // Governance Workflow Logic
                    if (data.type === 'new_approval_request') {
                        // Admins get high-visibility toasts for incoming requests
                        if (user.role === 'admin') {
                            info(
                                'Pending Approval',
                                `${data.user_name} has requested ${data.amount} credits. Justification: "${data.reason}"`
                            );
                        }
                    }
                } catch (err) {
                    console.error('[WebSocket] Failed to parse event signal:', err);
                }
            };

            socket.onclose = (e) => {
                if (e.wasClean) {
                    console.log('[WebSocket] Connection closed gracefully.');
                } else {
                    console.warn('[WebSocket] Connection lost. Attempting recovery in 5s...');
                    reconnectTimeoutRef.current = setTimeout(connect, 5000);
                }
            };

            socket.onerror = (err) => {
                console.error('[WebSocket] Transport error:', err);
                socket.close();
            };
        };

        connect();

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [user, info]);

    return (
        <WebSocketContext.Provider value={{ connected: !!socketRef.current }}>
            {children}
        </WebSocketContext.Provider>
    );
}


// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Custom hook for accessing WebSocket context and connection state.
// Why: Simplifies real-time state access in components.
// Root Cause: Direct context usage is verbose and error-prone.
// Context: Use in any component needing real-time status or events.
export function useWebSocket() {
    const context = useContext(WebSocketContext);
    if (context === undefined) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
}
