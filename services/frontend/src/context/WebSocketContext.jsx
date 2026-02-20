
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


export function useWebSocket() {
    const context = useContext(WebSocketContext);
    if (context === undefined) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
}
