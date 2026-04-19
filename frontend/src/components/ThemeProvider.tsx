'use client'

import * as React from 'react'

interface ThemeProviderProps {
  children: React.ReactNode
}

export function ThemeProvider({
  children,
  ...props
}: ThemeProviderProps) {
  React.useEffect(() => {
    // Загружаем тему из настроек или используем тёмную тему по умолчанию
    const loadTheme = () => {
      try {
        const savedSettings = localStorage.getItem('gameSettings');
        let theme = 'dark';
        
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings);
          theme = parsed.theme || 'dark';
        }
        
        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');
        root.classList.add(theme);
      } catch (error) {
        console.error('Ошибка загрузки темы:', error);
        const root = window.document.documentElement;
        root.classList.add('dark');
      }
    };

    loadTheme();
  }, [])

  return (
    <div {...props}>
      {children}
    </div>
  )
}

// Оставляем useTheme для обратной совместимости
export const useTheme = () => {
  const [theme, setThemeState] = React.useState<'light' | 'dark'>('dark');

  React.useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('gameSettings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        setThemeState(parsed.theme || 'dark');
      }
    } catch (error) {
      console.error('Ошибка загрузки темы:', error);
    }
  }, []);

  const setTheme = (newTheme: 'light' | 'dark') => {
    setThemeState(newTheme);
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(newTheme);
  };

  return {
    theme,
    setTheme,
  }
}

