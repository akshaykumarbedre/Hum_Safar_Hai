
"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Target, TrendingUp } from "lucide-react";
import { LineChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Line } from "recharts";
import { ChartTooltipContent, ChartContainer } from "@/components/ui/chart";

type Goal = {
  id: string;
  name: string;
  emoji: string;
  targetAmount: number;
  currentAmount: number;
  monthlyContribution: number;
};

const initialGoals: Goal[] = [
  {
    id: "1",
    name: "House Down Payment",
    emoji: "🏡",
    targetAmount: 100000,
    currentAmount: 60000,
    monthlyContribution: 1500,
  },
  {
    id: "2",
    name: "Dream Vacation to Japan",
    emoji: "🗾",
    targetAmount: 15000,
    currentAmount: 5250,
    monthlyContribution: 400,
  },
  {
    id: "3",
    name: "New Car Fund",
    emoji: "🚗",
    targetAmount: 30000,
    currentAmount: 24000,
    monthlyContribution: 500,
  },
];

type SimulationDataPoint = {
    month: number;
    value: number;
};

export default function GoalsPage() {
  const [goals, setGoals] = useState(initialGoals);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(goals[0]);
  const [annualReturn, setAnnualReturn] = useState(7);
  const [simulationData, setSimulationData] = useState<SimulationDataPoint[]>([]);

  const runSimulation = () => {
      if (!selectedGoal) return;
      const data: SimulationDataPoint[] = [];
      let currentValue = selectedGoal.currentAmount;
      const monthlyReturn = annualReturn / 100 / 12;

      for (let i = 0; i <= 60; i++) { // Simulate for 5 years
          data.push({ month: i, value: Math.round(currentValue) });
          currentValue += selectedGoal.monthlyContribution;
          currentValue *= (1 + monthlyReturn);
          if (currentValue >= selectedGoal.targetAmount) {
            data.push({ month: i + 1, value: selectedGoal.targetAmount });
            break;
          }
      }
      setSimulationData(data);
  };

  return (
    <div className="grid gap-6 md:grid-cols-12">
      <div className="md:col-span-4 lg:col-span-3 space-y-4">
        <h2 className="font-headline text-xl font-semibold">Your Goals</h2>
        {goals.map((goal) => (
          <Card
            key={goal.id}
            className={`cursor-pointer transition-all hover:shadow-md ${selectedGoal?.id === goal.id ? 'border-accent ring-2 ring-accent' : ''}`}
            onClick={() => {
                setSelectedGoal(goal);
                setSimulationData([]);
            }}
          >
            <CardHeader className="flex-row items-center gap-4 space-y-0 pb-2">
              <span className="text-3xl">{goal.emoji}</span>
              <div className="flex-1">
                <CardTitle className="text-base font-medium">{goal.name}</CardTitle>
                <CardDescription>
                  ${goal.currentAmount.toLocaleString()} / ${goal.targetAmount.toLocaleString()}
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <Progress value={(goal.currentAmount / goal.targetAmount) * 100} />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="md:col-span-8 lg:col-span-9">
        {selectedGoal && (
          <Card>
            <CardHeader>
              <CardTitle className="font-headline flex items-center gap-2">
                <TrendingUp className="text-accent" />
                Goal Simulation: {selectedGoal.name}
              </CardTitle>
              <CardDescription>
                Project your goal's completion based on your contributions and market returns.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="annualReturn">Estimated Annual Return (%)</Label>
                  <Input
                    id="annualReturn"
                    type="number"
                    value={annualReturn}
                    onChange={(e) => setAnnualReturn(Number(e.target.value))}
                  />
                </div>
                <Button onClick={runSimulation} className="w-full bg-accent hover:bg-accent/90 text-accent-foreground">
                    Run Simulation
                </Button>
                <div className="space-y-2 rounded-lg border p-4">
                    <h4 className="font-semibold">Goal Details</h4>
                    <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Target Amount</span>
                        <span>${selectedGoal.targetAmount.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Current Amount</span>
                        <span>${selectedGoal.currentAmount.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Monthly Contribution</span>
                        <span>${selectedGoal.monthlyContribution.toLocaleString()}</span>
                    </div>
                </div>
              </div>
              <div>
                {simulationData.length > 0 ? (
                    <div className="h-80">
                         <p className="text-center text-sm text-muted-foreground mb-2">Projected Growth Over Time</p>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={simulationData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                <XAxis dataKey="month" label={{ value: 'Months', position: 'insideBottom', offset: -5 }}/>
                                <YAxis tickFormatter={(value) => `$${Number(value) / 1000}k`} />
                                <Tooltip content={<ChartTooltipContent indicator="dot" />} />
                                <Line type="monotone" dataKey="value" stroke="hsl(var(--accent))" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                ) : (
                    <div className="h-80 flex flex-col items-center justify-center rounded-lg border border-dashed text-center">
                        <Target className="h-12 w-12 text-muted-foreground" />
                        <h3 className="mt-4 text-lg font-semibold">Run a simulation</h3>
                        <p className="mt-1 text-sm text-muted-foreground">
                            See how long it will take to reach your goal.
                        </p>
                    </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
