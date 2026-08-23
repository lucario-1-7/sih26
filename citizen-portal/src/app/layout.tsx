import type { Metadata } from 'next';
import { Inter, JetBrains_Mono, Playfair_Display } from 'next/font/google';
import './globals.css';
import { TopBar } from '@/components/TopBar';
import { Footer } from '@/components/Footer';
import { Toast } from '@/components/Toast';
import { SessionHydrator } from '@/components/SessionHydrator';

const inter = Inter({
  variable: '--font-sans',
  subsets: ['latin'],
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  variable: '--font-mono',
  subsets: ['latin'],
  display: 'swap',
});

const playfair = Playfair_Display({
  variable: '--font-serif',
  subsets: ['latin'],
  style: ['normal', 'italic'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'SocioSolve : solve local, impact global | Government of Jharkhand & MoE',
  description:
    'SocioSolve is a citizen-driven platform that connects local problems with innovative solutions for a better tomorrow. Powered by Ministry of Education, AICTE, and MoE Innovation Cell.',
  keywords: [
    'SocioSolve',
    'Jharkhand Innovation',
    'Citizen Problems',
    'AICTE',
    'Ministry of Education',
    'Higher Education',
    'R&D Solutions',
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} ${playfair.variable} h-full antialiased`}
    >
      <body className="min-h-screen flex flex-col font-sans bg-[#FAF8F5] text-black">
        <SessionHydrator />
        <TopBar />
        <main className="flex-1 w-full">{children}</main>
        <Footer />
        <Toast />
      </body>
    </html>
  );
}
