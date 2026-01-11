export default {
    darkMode: ["class"],
    content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Nunito', 'sans-serif'], // Keeping Nunito for friendly professionalism
                heading: ['Nunito', 'sans-serif'],
            },
            colors: {
                background: "#ffffff",
                foreground: "#111827", // Gray 900

                // Minimalist Professional Palette
                primary: {
                    DEFAULT: "#2ce080", // Blinkist Green
                    hover: "#24c16b",
                    light: "#e2fbf1", // Light Green Background
                    foreground: "#003e29", // Dark Green Text
                },
                secondary: {
                    DEFAULT: "#f3f4f6", // Gray 100
                    hover: "#e5e7eb", // Gray 200
                    foreground: "#1f2937", // Gray 800
                },
                accent: {
                    DEFAULT: "#000000",
                    foreground: "#ffffff",
                },

                muted: "#f9fafb",
                "muted-foreground": "#6b7280", // Gray 500
                border: "#e5e7eb", // Gray 200
                input: "#f3f4f6",
                ring: "#2ce080",
            },
            borderRadius: {
                lg: "0.75rem", // 12px
                md: "0.5rem", // 8px
                sm: "0.25rem", // 4px
                xl: "1rem", // 16px
                '2xl': "1.5rem", // 24px
                full: "9999px",
            },
            boxShadow: {
                'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.05)',
                'glow': '0 0 15px rgba(44, 224, 128, 0.3)',
            }
        },
    },
    plugins: [require("tailwindcss-animate"), require("@tailwindcss/typography")],
};
