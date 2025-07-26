import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldCheck } from "lucide-react";

export default function InsurancePage() {
  return (
    <div className="flex items-center justify-center h-full">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <div className="mx-auto bg-primary rounded-full h-16 w-16 flex items-center justify-center">
            <ShieldCheck className="h-8 w-8 text-primary-foreground" />
          </div>
          <CardTitle className="font-headline mt-4">Insurance Dashboard</CardTitle>
          <CardDescription>Coming Soon!</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This is where you'll manage your insurance policies and coverage details to ensure you're protected.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
