
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Target,
  LineChart,
  Settings,
  MessageCircle,
} from "lucide-react";

import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarInset,
} from "@/components/ui/sidebar";
import { Logo } from "@/components/logo";
import { cn } from "@/lib/utils";
import { DashboardHeader } from "@/components/dashboard-header";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/dashboard/goals", icon: Target, label: "Goals" },
  { href: "/dashboard/portfolio", icon: LineChart, label: "Portfolio" },
  { href: "/dashboard/chat", icon: MessageCircle, label: "Talk with your money" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  const getPageTitle = () => {
    if (pathname === '/dashboard') return 'Dashboard';
    const currentItem = navItems.find(item => pathname.startsWith(item.href) && item.href !== '/dashboard');
    return currentItem ? currentItem.label : 'Dashboard';
  }

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <Logo />
        </SidebarHeader>
        <SidebarContent>
          <SidebarMenu>
            {navItems.map((item) => (
              <SidebarMenuItem key={item.href}>
                <Link href={item.href}>
                  <SidebarMenuButton
                    isActive={pathname === item.href}
                    tooltip={item.label}
                  >
                    <item.icon />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </Link>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarContent>
        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <Link href="#">
                <SidebarMenuButton tooltip="Settings">
                  <Settings />
                  <span>Settings</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
      <SidebarInset>
        <DashboardHeader title={getPageTitle()} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
            {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
