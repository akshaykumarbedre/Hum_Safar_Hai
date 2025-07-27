"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { UserNav } from "@/components/user-nav";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Users, User } from "lucide-react";

type DashboardHeaderProps = {
  title: string;
};

export function DashboardHeader({ title }: DashboardHeaderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const currentView = searchParams.get("view") || "couple"; // Changed default to "couple"

  const handleViewChange = (newView: string) => {
    const params = new URLSearchParams(searchParams);
    params.set("view", newView);
    router.push(`${pathname}?${params.toString()}`);
  };

  const showFilter = ["/dashboard", "/dashboard/portfolio"].includes(pathname);

  return (
    <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background/80 px-4 backdrop-blur-sm md:px-6">
      <div className="flex items-center gap-2 md:hidden">
        <SidebarTrigger />
      </div>
      <h1 className="flex-1 font-headline text-2xl font-bold tracking-tight">
        {title}
      </h1>
      <div className="flex items-center gap-4">
        {showFilter && (
           <Select value={currentView} onValueChange={handleViewChange}>
             <SelectTrigger className="w-[180px] h-9 hidden md:flex">
                <SelectValue placeholder="Select a view" />
             </SelectTrigger>
             <SelectContent>
                 
                 <SelectItem value="1212121212">
                    <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        <span>Rohan's View</span>
                    </div>
                 </SelectItem>
                 <SelectItem value="2222222222">
                    <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        <span>Priya's View</span>
                    </div>
                </SelectItem>
                <SelectItem value="couple">
                    <div className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        <span>Couple View</span>
                    </div>
                 </SelectItem>
             </SelectContent>
           </Select>
        )}
        <UserNav />
      </div>
    </header>
  );
}
