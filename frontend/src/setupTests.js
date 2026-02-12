import '@testing-library/jest-dom';
// Polyfill / mock browser storage for Vitest jsdom environment
if (typeof global.window !== 'undefined' && !global.window.localStorage) {
    const storage = (() => {
        let store = {}
        return {
            getItem(key) {
                return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null
            },
            setItem(key, value) {
                store[key] = String(value)
            },
            removeItem(key) {
                delete store[key]
            },
            clear() {
                store = {}
            }
        }
    })()
    Object.defineProperty(global.window, 'localStorage', { value: storage })
    Object.defineProperty(global, 'localStorage', { value: storage })
}

