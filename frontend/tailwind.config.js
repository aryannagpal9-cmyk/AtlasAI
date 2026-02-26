/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                atlas: {
                    bg: '#f8fafc',
                    sidebar: '#ffffff',
                    border: '#e2e8f0',
                    accent: '#3b82f6',
                    text: '#1e293b',
                    muted: '#64748b'
                }
            },
            backgroundImage: {
                'gradient-glass': 'none',
            }
        },
    },
    plugins: [],
}
