import React from 'react';
import './globals.css';

export const metadata = {
  title: 'VidyaSahayak AI Kiosk',
  description: 'AI Avatar Kiosk for PES University',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased selection:bg-primary selection:text-primary-foreground">
        {children}
      </body>
    </html>
  );
}
