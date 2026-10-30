"use client";

import Link from "next/link";
import { useState } from "react";
import {
  LayoutDashboard,
  BarChart3,
  Zap,
  Bot,
  Brain,
  Activity,
  MessageSquare,
  Settings,
  ChevronLeft,
  Menu,
  Terminal,
  HardHat,
} from "lucide-react";
import { useRouter } from "next/navigation";

const navigation = [
  { name: "Dashboard", icon: LayoutDashboard, href: "/" },
  { name: "Live Terminal", icon: Terminal, href: "/terminal" },
  { name: "Strategy Lab", icon: HardHat, href: "/strategies" },
  { name: "Grok AI", icon: Bot, href: "/grok" },
  { name: "Grok Brain (Memory)", icon: Brain, href: "/brain" },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const router = useRouter();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-dark-900 border-r border-border flex flex-col shadow-lg transition-all duration-300">
      <div className="flex items-center justify-between h-16 px-4 bg-dark-800 border-b border-border">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-neon-green to-neon-blue flex items-center justify-center">
            <span className="text-white font-bold text-xs">G</span>
          </div>
          <span className={collapsed ? "hidden" : "font-bold text-lg tracking-tighter"}>
            Grok AI
          </span>
        </Link>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 hover:bg-accent rounded transition-colors"
        >
          <Menu className={collapsed ? undefined : "hidden"} />
          <ChevronLeft className={collapsed ? undefined : "hidden"} />
        </button>
      </div>

      <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = router.pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-3 rounded-lg transition-colors ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className={collapsed ? "hidden" : "font-medium text-sm"}>
                {item.name}
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border bg-dark-800">
        <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-accent cursor-pointer transition-colors mb-4">
          <Settings className="w-5 h-5 text-muted-foreground" />
          <span className={collapsed ? "hidden" : "text-xs font-medium text-muted-foreground"}>
            Settings
          </span>
        </div>
        <div className="flex items-center gap-3 p-2 rounded-lg bg-accent/10 border border-accent/20">
          <Zap className="w-5 h-5 text-neon-green animate-pulse" />
          <div className={collapsed ? "hidden" : "flex-1 min-w-0"}>
            <div className="text-xs font-semibold text-neon-green">System Live</div>
            <div className="text-[10px] text-muted-foreground">Backend: Connected</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
