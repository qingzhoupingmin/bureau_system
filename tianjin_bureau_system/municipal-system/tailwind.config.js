/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    // 必须使用extend属性，不要删除extend，避免直接覆盖默认配置
    extend: {
      colors: {
        // 市政工程管理系统配色方案
        // 使用场景说明：
        // - primary: 主色，用于主要按钮背景 (如bg-primary-100)
        // - secondary: 次要色，用于次要按钮背景 (如bg-secondary-100)
        // - accent: 强调色，用于高亮、提示等（可选，如：text-accent-500）
        // - foreground: 深色，用于主要文本 (如text-foreground)
        // - muted-foreground: 中等色，用于次要文本 (如text-muted-foreground)
        // - border: 用于边框 (如border-border)
        // - muted: 浅色，用于背景 (如bg-muted)

        // 蓝色系 - 稳重、专业、政府风格
        primary: {
          50: '#e6f0ff',
          100: '#cce0ff',
          200: '#99c2ff',
          300: '#66a3ff',
          400: '#3385ff',
          500: '#0066ff',
          600: '#0052cc',
          700: '#003d99',
          800: '#002966',
          900: '#001433',
        },
        // 青绿色系 - 环保、城市发展
        secondary: {
          50: '#e6f7f5',
          100: '#ccefeb',
          200: '#99dfd7',
          300: '#66cec3',
          400: '#33beaf',
          500: '#00ad9b',
          600: '#008b7c',
          700: '#00695d',
          800: '#00473e',
          900: '#00251f',
        },
        // 橙色系 - 强调、提示
        accent: {
          50: '#fff4e6',
          100: '#ffe9cc',
          200: '#ffd399',
          300: '#ffbd66',
          400: '#ffa733',
          500: '#ff9100',
          600: '#cc7400',
          700: '#995700',
          800: '#663a00',
          900: '#331d00',
        },
        foreground: '#1a1a2e',
        'muted-foreground': '#64748b',
        border: '#e2e8f0',
        muted: '#f8fafc',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Cal Sans', 'Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'scale-in': 'scaleIn 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
