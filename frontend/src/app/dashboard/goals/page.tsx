"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Target, Users, User } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

type Asset = {
  asset_name: string;
  amount: number;
};

type Goal = {
  name: string;
  target_amount: number;
  male_assets: Asset[];
  female_assets: Asset[];
  current_corpus: number;
  male_monthly_contribution: number;
  female_monthly_contribution: number;
  total_monthly_contribution: number;
  pledged: boolean;
};

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchGoals() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("http://localhost:8000/tools/goals", {
          headers: { "accept": "application/json" }
        });
        const data = await res.json();
        console.log("Fetched goals:", data);
        // Transform the API data to match our Goal type
        const apiGoals = Array.isArray(data) ? data : [];
        setGoals(apiGoals);
        setSelectedGoal(apiGoals[0] || null);
      } catch (e) {
        setError("Failed to load goals");
      } finally {
        setLoading(false);
      }
    }
    fetchGoals();
  }, []);

  if (error) {
    return <div className="text-red-500 text-center">{error}</div>;
  }
  if (loading) {
    return (
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Goals</CardTitle>
            <CardDescription>Loading your goals...</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Progress value={0} />
              <div className="h-8 bg-muted rounded" />
              <div className="h-8 bg-muted rounded" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-12">
      <div className="md:col-span-4 lg:col-span-3 space-y-4">
        <h2 className="font-headline text-xl font-semibold">Your Goals</h2>
        {goals.map((goal, index) => (
          <Card
            key={index}
            className={`cursor-pointer transition-all hover:shadow-md ${selectedGoal?.name === goal.name ? 'border-accent ring-2 ring-accent' : ''}`}
            onClick={() => {
                setSelectedGoal(goal);
            }}
          >
            <CardHeader className="flex-row items-center gap-4 space-y-0 pb-2">
              <span className="text-3xl">🎯</span>
              <div className="flex-1">
                <CardTitle className="text-base font-medium">{goal.name}</CardTitle>
                <CardDescription>
                  ₹{goal.current_corpus.toLocaleString()} / ₹{goal.target_amount.toLocaleString()}
                </CardDescription>
              </div>
              {goal.pledged && <Badge variant="secondary">Pledged</Badge>}
            </CardHeader>
            <CardContent>
              <Progress value={(goal.current_corpus / goal.target_amount) * 100} />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="md:col-span-8 lg:col-span-9">
        {selectedGoal && (
          <div className="space-y-6">
            {/* Goal Overview Card */}
            <Card>
              <CardHeader>
                <CardTitle className="font-headline flex items-center gap-2">
                  <Target className="text-accent" />
                  Goal Overview: {selectedGoal.name}
                </CardTitle>
                <CardDescription>
                  Track your progress and view detailed asset allocation for this goal.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-3">
                  <div className="space-y-2 rounded-lg border p-4">
                    <h4 className="font-semibold">Target Amount</h4>
                    <p className="text-2xl font-bold text-accent">₹{selectedGoal.target_amount.toLocaleString()}</p>
                  </div>
                  <div className="space-y-2 rounded-lg border p-4">
                    <h4 className="font-semibold">Current Corpus</h4>
                    <p className="text-2xl font-bold">₹{selectedGoal.current_corpus.toLocaleString()}</p>
                    <div className="w-full">
                      <Progress value={(selectedGoal.current_corpus / selectedGoal.target_amount) * 100} className="h-2" />
                      <p className="text-xs text-muted-foreground mt-1">
                        {((selectedGoal.current_corpus / selectedGoal.target_amount) * 100).toFixed(1)}% complete
                      </p>
                    </div>
                  </div>
                  <div className="space-y-2 rounded-lg border p-4">
                    <h4 className="font-semibold">Monthly Contribution</h4>
                    <p className="text-2xl font-bold">₹{selectedGoal.total_monthly_contribution.toLocaleString()}</p>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <div className="flex justify-between">
                        <span>Male:</span>
                        <span>₹{selectedGoal.male_monthly_contribution.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Female:</span>
                        <span>₹{selectedGoal.female_monthly_contribution.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Assets Tables */}
            <div className="grid gap-6 md:grid-cols-2">
              {/* Male Assets Table */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <User className="h-5 w-5 text-blue-600" />
                    Male Assets
                  </CardTitle>
                  <CardDescription>
                    Total Value: ₹{selectedGoal.male_assets.reduce((sum, asset) => sum + asset.amount, 0).toLocaleString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {selectedGoal.male_assets.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Asset Name</TableHead>
                          <TableHead className="text-right">Amount</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedGoal.male_assets.map((asset, index) => (
                          <TableRow key={index}>
                            <TableCell className="font-medium">{asset.asset_name}</TableCell>
                            <TableCell className="text-right">₹{asset.amount.toLocaleString()}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <div className="text-center py-4 text-muted-foreground">
                      No assets allocated
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Female Assets Table */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <User className="h-5 w-5 text-pink-600" />
                    Female Assets
                  </CardTitle>
                  <CardDescription>
                    Total Value: ₹{selectedGoal.female_assets.reduce((sum, asset) => sum + asset.amount, 0).toLocaleString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {selectedGoal.female_assets.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Asset Name</TableHead>
                          <TableHead className="text-right">Amount</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedGoal.female_assets.map((asset, index) => (
                          <TableRow key={index}>
                            <TableCell className="font-medium">{asset.asset_name}</TableCell>
                            <TableCell className="text-right">₹{asset.amount.toLocaleString()}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <div className="text-center py-4 text-muted-foreground">
                      No assets allocated
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
