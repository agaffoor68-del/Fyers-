import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/topbar";

export const metadata = {
  title: "Grok AI Trading Platform",
  description: "Institutional-grade Algo Trading Platform with Grok AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full dark">
      <body className="h-full flex flex-col overflow-hidden">
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <TopBar />
            <main className="flex-1 overflow-y-auto p-6 bg-background min-h-0">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
