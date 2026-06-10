import React from 'react';

export const metadata = {
  title: 'VidyaSahayak AI Kiosk',
  description: 'AI Avatar Kiosk for PES University',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, backgroundColor: '#060810' }}>
        {children}
      </body>
    </html>
  );
}
