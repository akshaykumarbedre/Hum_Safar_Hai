
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
import { ClientOnly } from "@/components/client-only";


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

// const coupleData = {
//   netWorth: 120530,
//   netWorthData: [
//     { date: "Jan", value: 80000 }, { date: "Feb", value: 85000 },
//     { date: "Mar", value: 95000 }, { date: "Apr", value: 105000 },
//     { date: "May", value: 115000 }, { date: "Jun", value: 120530 },
//   ],
//   goals: [
//     { name: '🏡 House Down Payment', progress: 60 },
//     { name: '🏖️ Dream Vacation', progress: 35 },
//     { name: '🚗 New Car Fund', progress: 80 },
//   ],
//   spendingData: [
//     { name: "Groceries", value: 450.75, fill: "var(--color-groceries)" },
//     { name: "Utilities", value: 220.5, fill: "var(--color-utilities)" },
//     { name: "Dining", value: 350.0, fill: "var(--color-dining)" },
//     { name: "Shopping", value: 500.25, fill: "var(--color-shopping)" },
//     { name: "Transport", value: 150.0, fill: "var(--color-transport)" },
//   ],
//   transactions: [
//     { id: "1", description: "Trader Joe's", amount: -78.54, date: "2024-07-22" },
//     { id: "2", description: "Salary Deposit (Alex)", amount: 3500.0, date: "2024-07-21" },
//     { id: "3", description: "Amazon.com", amount: -124.99, date: "2024-07-20" },
//     { id: "4", description: "PG&E Utility", amount: -150.23, date: "2024-07-19" },
//     { id: "5", description: "Salary Deposit (Sarah)", amount: 3200.0, date: "2024-07-18" },
//   ]
// };

// const alexData = {
//   netWorth: 65200,
//   netWorthData: [
//     { date: "Jan", value: 40000 }, { date: "Feb", value: 42000 },
//     { date: "Mar", value: 48000 }, { date: "Apr", value: 53000 },
//     { date: "May", value: 60000 }, { date: "Jun", value: 65200 },
//   ],
//   goals: [
//     { name: '👨‍💻 New Laptop', progress: 75 },
//     { name: '📷 Photography Gear', progress: 50 },
//   ],
//   spendingData: [
//     { name: "Gadgets", value: 300, fill: "var(--color-shopping)" },
//     { name: "Dining", value: 200, fill: "var(--color-dining)" },
//     { name: "Transport", value: 100, fill: "var(--color-transport)" },
//   ],
//   transactions: [
//     { id: "1", description: "Best Buy", amount: -250.00, date: "2024-07-22" },
//     { id: "2", description: "Salary Deposit", amount: 3500.0, date: "2024-07-21" },
//     { id: "3", description: "Steakhouse Dinner", amount: -110.00, date: "2024-07-18" },
//   ]
// };

// const sarahData = {
//   netWorth: 55330,
//   netWorthData: [
//     { date: "Jan", value: 40000 }, { date: "Feb", value: 43000 },
//     { date: "Mar", value: 47000 }, { date: "Apr", value: 52000 },
//     { date: "May", value: 55000 }, { date: "Jun", value: 55330 },
//   ],
//   goals: [
//     { name: '🎨 Art Supplies', progress: 90 },
//     { name: '🧘‍♀️ Yoga Retreat', progress: 40 },
//   ],
//   spendingData: [
//     { name: "Shopping", value: 250.25, fill: "var(--color-shopping)" },
//     { name: "Groceries", value: 250.75, fill: "var(--color-groceries)" },
//     { name: "Hobbies", value: 150, fill: "var(--color-utilities)" },
//   ],
//   transactions: [
//     { id: "1", description: "Art Store", amount: -95.50, date: "2024-07-22" },
//     { id: "2", description: "Salary Deposit", amount: 3200.0, date: "2024-07-18" },
//     { id: "3", description: "Whole Foods", amount: -130.45, date: "2024-07-17" },
//   ]
// };

// const allData = {
//     couple: coupleData,
//     alex: alexData,
//     sarah: sarahData,
// };

const initialData = {
  netWorth: 0,
  netWorthData: [] as { date: string; value: number }[],
  goals: [] as { name: string; progress: number }[],
  spendingData: [] as { name: string; value: number; fill: string }[],
  transactions: [] as { id: string; description: string; amount: number; date: string }[],
};

const allData = {
  couple: {
    netWorth: 120530,
    netWorthData: [
      { date: "Jan", value: 80000 }, { date: "Feb", value: 85000 },
      { date: "Mar", value: 95000 }, { date: "Apr", value: 105000 },
      { date: "May", value: 115000 }, { date: "Jun", value: 120530 },
    ],
    goals: [
      { name: '🏡 House Down Payment', progress: 60 },
      { name: '🏖️ Dream Vacation', progress: 35 },
      { name: '🚗 New Car Fund', progress: 80 },
    ],
    spendingData: [
      { name: "Groceries", value: 450.75, fill: "var(--color-groceries)" },
      { name: "Utilities", value: 220.5, fill: "var(--color-utilities)" },
      { name: "Dining", value: 350.0, fill: "var(--color-dining)" },
      { name: "Shopping", value: 500.25, fill: "var(--color-shopping)" },
      { name: "Transport", value: 150.0, fill: "var(--color-transport)" },
    ],
    transactions: [
      { id: "1", description: "Trader Joe's", amount: -78.54, date: "2024-07-22" },
      { id: "2", description: "Salary Deposit (Alex)", amount: 3500.0, date: "2024-07-21" },
      { id: "3", description: "Amazon.com", amount: -124.99, date: "2024-07-20" },
      { id: "4", description: "PG&E Utility", amount: -150.23, date: "2024-07-19" },
      { id: "5", description: "Salary Deposit (Sarah)", amount: 3200.0, date: "2024-07-18" },
    ]
  },
  "5555555555": {
    netWorth: 65200,
    netWorthData: [
      { date: "Jan", value: 40000 }, { date: "Feb", value: 42000 },
      { date: "Mar", value: 48000 }, { date: "Apr", value: 53000 },
      { date: "May", value: 60000 }, { date: "Jun", value: 65200 },
    ],
    goals: [
      { name: '👨‍💻 New Laptop', progress: 75 },
      { name: '📷 Photography Gear', progress: 50 },
    ],
    spendingData: [
      { name: "Gadgets", value: 300, fill: "var(--color-shopping)" },
      { name: "Dining", value: 200, fill: "var(--color-dining)" },
      { name: "Transport", value: 100, fill: "var(--color-transport)" },
    ],
    transactions: [
      { id: "1", description: "Best Buy", amount: -250.00, date: "2024-07-22" },
      { id: "2", description: "Salary Deposit", amount: 3500.0, date: "2024-07-21" },
      { id: "3", description: "Steakhouse Dinner", amount: -110.00, date: "2024-07-18" },
    ]
  },
  "6666666666": {
    netWorth: 55330,
    netWorthData: [
      { date: "Jan", value: 40000 }, { date: "Feb", value: 43000 },
      { date: "Mar", value: 47000 }, { date: "Apr", value: 52000 },
      { date: "May", value: 55000 }, { date: "Jun", value: 55330 },
    ],
    goals: [
      { name: '🎨 Art Supplies', progress: 90 },
      { name: '🧘‍♀️ Yoga Retreat', progress: 40 },
    ],
    spendingData: [
      { name: "Shopping", value: 250.25, fill: "var(--color-shopping)" },
      { name: "Groceries", value: 250.75, fill: "var(--color-groceries)" },
      { name: "Hobbies", value: 150, fill: "var(--color-utilities)" },
    ],
    transactions: [
      { id: "1", description: "Art Store", amount: -95.50, date: "2024-07-22" },
      { id: "2", description: "Salary Deposit", amount: 3200.0, date: "2024-07-18" },
      { id: "3", description: "Whole Foods", amount: -130.45, date: "2024-07-17" },
    ]
  }
};

type View = "couple" | "5555555555" | "6666666666";


export default function DashboardPage() {
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
        // const user_id = currentView;
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
        
        console.log("Net Worth Data:", netWorthResult.get_core_net_worth_snapshot?.total_net_worth);
        console.log("Spending Summary Data:", expenseResult.get_spending_summary);
        console.log("Category Breakdown:", expenseResult.get_spending_summary?.category_breakdown);
        console.log("Transaction Data:", expenseResult.get_core_transaction_data);
        console.log("Transactions:", expenseResult.get_core_transaction_data?.transactions);
        
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
          
          // Investment Portfolio Data
          // stockHoldings: netWorthResult.get_processed_investment_portfolio?.stock_holdings || [],
          // mutualFundHoldings: netWorthResult.get_processed_investment_portfolio?.mutual_fund_holdings || [],
          // portfolioSummary: netWorthResult.get_processed_investment_portfolio?.portfolio_summary || {
          //   total_stock_value: 0,
          //   total_mutual_fund_current: 0,
          //   total_portfolio_value: 0,
          //   stock_count: 0,
          //   mutual_fund_count: 0,
          //   formatted_total_portfolio: "₹0",
          //   formatted_stock_value: "₹0",
          //   formatted_mf_current: "₹0"
          // },
          // portfolioPerformance: netWorthResult.get_portfolio_performance_summary || {
          //   total_invested: 0,
          //   current_value: 0,
          //   absolute_gain: 0,
          //   overall_xirr: 0
          // }
        }));

        // Using mock data for now
        // setData(allData[currentView]);

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
    <ClientOnly>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="font-headline">Net Worth</CardTitle>
            <CardDescription>
              Your financial snapshot over the last 6 months.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <p className="text-4xl font-bold tracking-tighter">
              ${(data.netWorth || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <div className="h-48">
              <ChartContainer config={chartConfig} className="h-full w-full">
                <AreaChart
                  data={data.netWorthData}
                  margin={{ top: 5, right: 10, left: -20, bottom: 0 }}
                  accessibilityLayer
                >
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="5%"
                        stopColor="var(--color-value)"
                        stopOpacity={0.8}
                      />
                      <stop
                        offset="95%"
                        stopColor="var(--color-value)"
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `$${Number(value) / 1000}k`}
                  />
                  <Tooltip
                    cursor={false}
                    content={<ChartTooltipContent indicator="dot" />}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="var(--color-value)"
                    fillOpacity={1}
                    fill="url(#colorValue)"
                  />
                </AreaChart>
              </ChartContainer>
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
            {data.goals.map(goal => (
              <div key={goal.name}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">{goal.name}</span>
                  <span className="text-sm text-muted-foreground">{goal.progress}%</span>
                </div>
                <Progress value={goal.progress} />
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
            <ChartContainer config={chartConfig} className="h-full w-full">
              <BarChart
                data={data.spendingData}
                layout="vertical"
                margin={{ left: 10, right: 10, top: 20, bottom: 20 }}
              >
                <XAxis type="number" hide />
                <YAxis
                  dataKey="name"
                  type="category"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={15}
                  width={100}
                />
                <Tooltip
                  cursor={{ fill: "hsl(var(--muted))" }}
                  content={<ChartTooltipContent />}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ChartContainer>
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
                {data.transactions.map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell>
                      <div className="font-medium">{transaction.description}</div>
                      <div className="text-xs text-muted-foreground">
                        {transaction.date}
                      </div>
                    </TableCell>
                    <TableCell
                      className={`text-right font-semibold ${
                        transaction.amount > 0
                          ? "text-green-600"
                          : "text-foreground"
                      }`}
                    >
                      {transaction.amount < 0
                        ? `-$${Math.abs(transaction.amount).toFixed(2)}`
                        : `+$${transaction.amount.toFixed(2)}`}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </ClientOnly>
  );
}
