import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User, CreditCard, LogOut, Settings } from "lucide-react";

export function UserNav() {
  return (
    <div className="flex items-center gap-2">
       <div className="flex -space-x-2 overflow-hidden">
        <Avatar className="inline-block h-9 w-9 rounded-full ring-2 ring-background">
            <AvatarImage src="https://placehold.co/40x40.png" alt="User 1" data-ai-hint="woman face"/>
            <AvatarFallback>S</AvatarFallback>
        </Avatar>
        <Avatar className="inline-block h-9 w-9 rounded-full ring-2 ring-background">
            <AvatarImage src="https://placehold.co/40x40.png" alt="User 2" data-ai-hint="man face"/>
            <AvatarFallback>A</AvatarFallback>
        </Avatar>
       </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full">
            <Avatar className="h-9 w-9">
               <AvatarFallback className="bg-primary text-primary-foreground">AS</AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="end" forceMount>
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium leading-none">Alex & Sarah</p>
              <p className="text-xs leading-none text-muted-foreground">
                alex.sarah@email.com
              </p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem>
              <User className="mr-2" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <CreditCard className="mr-2" />
              <span>Billing</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2" />
              <span>Settings</span>
            </DropdownMenuItem>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <LogOut className="mr-2" />
            <span>Log out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
