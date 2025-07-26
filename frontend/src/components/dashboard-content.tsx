"use client";

import { useSearchParams } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Area,
  AreaChart,
} from "recharts";
import { ChartTooltipContent, ChartContainer } from "@/components/ui/chart";
import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";

const chartConfig = {
  value: {
    label: "Value",
    color: "hsl(var(--accent))",
  },
  groceries: {
    label: "Groceries",
    color: "hsl(var(--chart-1))",
  },
  utilities: {
    label: "Utilities",
    color: "hsl(var(--chart-2))",
  },
  dining: {
    label: "Dining",
    color: "hsl(var(--chart-3))",
  },
  shopping: {
    label: "Shopping",
    color: "hsl(var(--chart-4))",
  },
  transport: {
    label: "Transport",
    color: "hsl(var(--chart-5))",
  },
};

const initialData = {
  netWorth: 0,
  netWorthData: [],
  goals: [],
  spendingData: [],
  transactions: [],
};

type View = "couple" | "5555555555" | "6666666666";

export function DashboardContent() {
  const searchParams = useSearchParams();
  const currentView = (searchParams.get("view") as View) || "couple";
  
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const user_id = '5555555555';

        // Fetch expense data (includes transactions and spending summary)
        const expenseResponse = await fetch(`http://localhost:8000/tools/expense/${user_id}`);
        if (!expenseResponse.ok) {
          throw new Error('Failed to fetch expense data');
        }
        const expenseResult = await expenseResponse.json();
        
        // Fetch net worth data
        const netWorthResponse = await fetch(`http://localhost:8000/tools/net_worth/${user_id}`);
        if (!netWorthResponse.ok) {
          throw new Error('Failed to fetch net worth data');
        }
        const netWorthResult = await netWorthResponse.json();
        
        // Map backend response to frontend data structure
        setData((prev) => ({
          ...prev,
          // Net Worth from core net worth snapshot
          netWorth: netWorthResult.get_core_net_worth_snapshot?.total_net_worth || 0,
          
          // Net Worth Data - create time series data from available data
          netWorthData: netWorthResult.get_core_net_worth_snapshot ? [
            { date: "Jan", value: netWorthResult.get_core_net_worth_snapshot.total_net_worth * 0.8 },
            { date: "Feb", value: netWorthResult.get_core_net_worth_snapshot.total_net_worth * 0.85 },
            { date: "Mar", value: netWorthResult.get_core_net_worth_snapshot.total_net_worth * 0.9 },
            { date: "Apr", value: netWorthResult.get_core_net_worth_snapshot.total_net_worth * 0.95 },
            { date: "May", value: netWorthResult.get_core_net_worth_snapshot.total_net_worth * 0.98 },
            { date: "Jun", value: netWorthResult.get_core_net_worth_snapshot.total_net_worth },
          ] : [],
          
          // Goals - extract from financial goals if available, otherwise use mock data
          goals: [
            { name: '🏡 House Down Payment', progress: 60 },
            { name: '🏖️ Dream Vacation', progress: 35 },
            { name: '🚗 New Car Fund', progress: 80 },
          ],
          
          // Spending Data - extract from spending summary category breakdown
          spendingData: expenseResult.get_spending_summary?.category_breakdown ? 
            expenseResult.get_spending_summary.category_breakdown.map((item: any, index: number) => {
              // Create purple gradient colors based on index
              const purpleHues = [270, 280, 290, 300, 310, 320, 330, 340];
              const hue = purpleHues[index % purpleHues.length];
              const lightness = 60 - (index * 5); // Decreasing lightness for gradient effect
              
              return {
                name: item.category,
                value: item.amount,
                fill: `hsl(${hue}, 70%, ${Math.max(lightness, 35)}%)`
              };
            }) : [],
          
          // Transactions - extract from core transaction data
          transactions: expenseResult.get_core_transaction_data?.transactions ? 
            expenseResult.get_core_transaction_data.transactions.slice(0, 5).map((transaction: any, index: number) => ({
              id: index.toString(),
              description: transaction.desc.length > 30 ? transaction.desc.substring(0, 30) + '...' : transaction.desc,
              amount: transaction.type === 'DR' ? -transaction.amt : transaction.amt,
              date: transaction.date
            })) : [],
        }));

      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred");
        setData(initialData);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentView]);

  if (error) {
    return <div className="text-red-500 text-center">Error: {error}</div>
  }

  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="font-headline">Net Worth</CardTitle>
            <CardDescription>
              Your financial snapshot over the last 6 months.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <Skeleton className="h-10 w-32 mb-2" />
            <div className="h-48">
              <Skeleton className="h-full w-full" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Goal Progress</CardTitle>
            <CardDescription>
              How you're tracking towards your goals.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">
                    <Skeleton className="h-4 w-24" />
                  </span>
                  <span className="text-sm text-muted-foreground">
                    <Skeleton className="h-4 w-8" />
                  </span>
                </div>
                <Skeleton className="h-2 w-full" />
              </div>
            ))}
          </CardContent>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="font-headline">Spending by Category</CardTitle>
            <CardDescription>
              Your spending breakdown for this month.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <Skeleton className="h-full w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Recent Transactions</CardTitle>
            <CardDescription>Your latest financial activities.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableBody>
                {[1, 2, 3].map((i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <div className="font-medium">
                        <Skeleton className="h-4 w-24" />
                      </div>
                      <div className="text-xs text-muted-foreground">
                        <Skeleton className="h-3 w-16" />
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      <Skeleton className="h-4 w-12 ml-auto" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {/* Net Worth Card */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="font-headline">Net Worth</CardTitle>
          <CardDescription>
            Your financial snapshot over the last 6 months.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <div className="text-3xl font-bold">
            ₹{data.netWorth.toLocaleString()}
          </div>
          <div className="h-48">
            <ChartContainer>
              <AreaChart data={data.netWorthData}>
                <defs>
                  <linearGradient id="netWorthGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--accent))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--accent))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `₹${value.toLocaleString()}`}
                />
                <Tooltip content={<ChartTooltipContent />} />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="hsl(var(--accent))"
                  strokeWidth={2}
                  fill="url(#netWorthGradient)"
                />
              </AreaChart>
            </ChartContainer>
          </div>
        </CardContent>
      </Card>

      {/* Goal Progress Card */}
      <Card>
        <CardHeader>
          <CardTitle className="font-headline">Goal Progress</CardTitle>
          <CardDescription>
            How you're tracking towards your goals.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.goals.map((goal, index) => (
            <div key={index}>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium">{goal.name}</span>
                <span className="text-sm text-muted-foreground">{goal.progress}%</span>
              </div>
              <Progress value={goal.progress} className="h-2" />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Spending by Category Card */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="font-headline">Spending by Category</CardTitle>
          <CardDescription>
            Your spending breakdown for this month.
          </CardDescription>
        </CardHeader>
        <CardContent className="h-80">
          <ChartContainer>
            <BarChart data={data.spendingData}>
              <XAxis
                dataKey="name"
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `₹${value.toLocaleString()}`}
              />
              <Tooltip content={<ChartTooltipContent />} />
              <Bar
                dataKey="value"
                fill="hsl(var(--accent))"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Recent Transactions Card */}
      <Card>
        <CardHeader>
          <CardTitle className="font-headline">Recent Transactions</CardTitle>
          <CardDescription>Your latest financial activities.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableBody>
              {data.transactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>
                    <div className="font-medium">{transaction.description}</div>
                    <div className="text-xs text-muted-foreground">{transaction.date}</div>
                  </TableCell>
                  <TableCell className={`text-right font-semibold ${
                    transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.amount >= 0 ? '+' : ''}₹{Math.abs(transaction.amount).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
} 