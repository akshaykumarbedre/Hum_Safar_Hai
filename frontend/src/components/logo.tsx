import { PiggyBank } from "lucide-react";

export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/20">
        <PiggyBank className="h-6 w-6 text-accent" />
      </div>
      <h1 className="font-headline text-2xl font-bold text-foreground">
        CoupleFi
      </h1>
    </div>
  );
}
