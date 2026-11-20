import type { Metadata, Viewport } from "next";
import { Figtree, Syne } from "next/font/google";
import "./globals.css";

const syne = Syne({
  variable: "--font-syne",
  subsets: ["latin"],
  weight: ["600", "700", "800"],
});

const figtree = Figtree({
  variable: "--font-figtree",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Eleva Chamados",
  description:
    "Anote chamados por áudio no campo. O escritório recebe o texto pronto para emitir a nota do cliente.",
  applicationName: "Eleva Chamados",
};

export const viewport: Viewport = {
  themeColor: "#c45c16",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={`${syne.variable} ${figtree.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
