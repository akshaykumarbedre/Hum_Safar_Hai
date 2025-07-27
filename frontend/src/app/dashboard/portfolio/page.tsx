
"use client";

import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart";
import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";

// Initial data structure
const initialPortfolioData = {
  totalInvestment: 0,
  currentValue: 0,
  overallGain: 0,
  overallGainPercentage: 0,
  assetAllocation: [] as { name: string; value: number; color: string }[],
  holdings: [] as { name: string; type: string; quantity?: number; units?: number; avgPrice?: number; avgNav?: number; currentValue: number }[],
  stockHoldings: [] as { issuer_name: string; isin: string; units: number; last_price: number; total_value: number; formatted_value: string; formatted_price: string }[],
  mutualFundHoldings: [] as any[],
  etfHoldings: [] as { isin: string; isinDescription: string; units: number; nav: { units: string; nanos: number }; lastNavDate: string; currentValue: number }[],
  portfolioSummary: {
    total_stock_value: 0,
    total_mutual_fund_current: 0,
    total_portfolio_value: 0,
    stock_count: 0,
    mutual_fund_count: 0,
    formatted_total_portfolio: "₹0",
    formatted_stock_value: "₹0",
    formatted_mf_current: "₹0"
  },
  portfolioPerformance: {
    total_invested: 0,
    current_value: 0,
    absolute_gain: 0,
    overall_xirr: 0
  }
};

type View = "couple" | "1212121212" | "2222222222";

const chartConfig = {
  value: { label: "Value" },
  "Cash & Bank": { label: "Cash & Bank", color: "hsl(var(--chart-1))" },
  "EPF": { label: "EPF", color: "hsl(var(--chart-2))" },
  "Indian Stocks": { label: "Indian Stocks", color: "hsl(var(--chart-3))" },
  "Mutual Funds": { label: "Mutual Funds", color: "hsl(var(--chart-4))" },
  "US Stocks": { label: "US Stocks", color: "hsl(var(--chart-5))" },
  "ETFs": { label: "ETFs", color: "hsl(var(--chart-6))" },
};

const HoldingsTable = ({ holdings, type }: { holdings: any[], type: 'Stock' | 'Mutual Fund' | 'ETF' }) => {
    const isStock = type === 'Stock';
    const isETF = type === 'ETF';
    
    return (
        <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>{isStock ? 'Quantity' : 'Units'}</TableHead>
                <TableHead className="text-right">{isStock ? 'Current Price' : isETF ? 'NAV' : 'NAV'}</TableHead>
                <TableHead className="text-right">Current Value</TableHead>
                {isETF && <TableHead className="text-right">Last NAV Date</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {holdings.map((holding, index) => {
                let displayName, units, price, value;
                
                if (isStock) {
                  displayName = holding.issuer_name;
                  units = holding.units;
                  price = holding.formatted_price;
                  value = holding.formatted_value;
                } else if (isETF) {
                  displayName = holding.isinDescription;
                  units = holding.units;
                  price = holding.nav ? `₹${parseFloat(holding.nav.units) + (holding.nav.nanos / 1000000000)}` : '₹0';
                  value = `₹${holding.currentValue.toLocaleString()}`;
                } else {
                  // Mutual Fund
                  displayName = holding.scheme_name || holding.name;
                  units = holding.units || 0;
                  price = `₹${holding.nav || 0}`;
                  value = `₹${holding.current_value || 0}`;
                }

                return (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      {displayName}
                      {isStock && <div className="text-xs text-muted-foreground">ISIN: {holding.isin}</div>}
                      {isETF && <div className="text-xs text-muted-foreground">ISIN: {holding.isin}</div>}
                    </TableCell>
                    <TableCell>{units}</TableCell>
                    <TableCell className="text-right">{price}</TableCell>
                    <TableCell className="text-right font-semibold">{value}</TableCell>
                    {isETF && (
                      <TableCell className="text-right text-xs text-muted-foreground">
                        {holding.lastNavDate ? new Date(holding.lastNavDate).toLocaleDateString() : 'N/A'}
                      </TableCell>
                    )}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
    )
}

// Add a dedicated StockHoldingsTable component
const StockHoldingsTable = ({ holdings }: { holdings: any[] }) => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Name</TableHead>
        <TableHead>ISIN</TableHead>
        <TableHead>Quantity</TableHead>
        <TableHead className="text-right">Current Price</TableHead>
        <TableHead className="text-right">Current Value</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {holdings.map((holding, idx) => (
        <TableRow key={idx}>
          <TableCell className="font-medium">{holding.issuer_name}</TableCell>
          <TableCell>{holding.isin}</TableCell>
          <TableCell>{holding.units}</TableCell>
          <TableCell className="text-right">{holding.formatted_price}</TableCell>
          <TableCell className="text-right font-semibold">{holding.formatted_value}</TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);

export default function PortfolioPage() {
  const searchParams = useSearchParams();
  const currentView = (searchParams.get("view") as View) || "couple";
  
  const [portfolioData, setPortfolioData] = useState(initialPortfolioData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPortfolioData = async () => {
      setLoading(true);
      setError(null);
      try {
        const user_id = currentView; // Using the same user ID as dashboard

        // Fetch investment portfolio data
        const response = await fetch(`http://localhost:8000/tools/net_worth/${user_id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch portfolio data');
        }
        const result = await response.json();
        
        console.log("Portfolio Data:", result);
        
        // Extract portfolio data from the response
        const get_processed_investment_portfolio = result.get_processed_investment_portfolio;
        const portfolioDiversification = result.get_portfolio_diversification;
        const performanceSummary = result.get_portfolio_performance_summary;
        
        console.log("Investment Portfolio:", get_processed_investment_portfolio);
        console.log("Stock Holdings:", get_processed_investment_portfolio?.stock_holdings);
        console.log("Mutual Fund Holdings:", get_processed_investment_portfolio?.mutual_fund_holdings);
        
        // Extract ETF holdings from the raw net worth data
        let etfHoldings: any[] = [];
        if (result.accounts) {
          Object.values(result.accounts).forEach((account: any) => {
            if (account.etfSummary?.holdingsInfo) {
              etfHoldings = account.etfSummary.holdingsInfo.map((holding: any) => ({
                isin: holding.isin,
                isinDescription: holding.isinDescription,
                units: holding.units || holding.totalNumberUnits,
                nav: holding.nav,
                lastNavDate: holding.lastNavDate,
                currentValue: holding.nav ? (parseFloat(holding.nav.units) + (holding.nav.nanos / 1000000000)) * (holding.units || holding.totalNumberUnits) : 0
              }));
            }
          });
        }
        
        // Calculate overall gain and percentage using portfolio diversification data
        const currentValue = portfolioDiversification?.total_portfolio_value || 0;
        const totalInvested = performanceSummary?.total_invested || 0;
        const overallGain = currentValue - totalInvested;
        const overallGainPercentage = totalInvested > 0 ? (overallGain / totalInvested) * 100 : 0;
        
        // Create asset allocation data from portfolio diversification
        const assetAllocation = portfolioDiversification?.asset_allocation?.map((item: any) => ({
          name: item.category,
          value: item.amount,
          percentage: item.percentage,
          formatted_amount: item.formatted_amount,
          color: getAssetColor(item.category)
        })) || [];
        
        // Helper function to assign colors based on asset category
        function getAssetColor(category: string): string {
          const colorMap: { [key: string]: string } = {
            'Cash & Bank': 'hsl(var(--chart-1))',
            'EPF': 'hsl(var(--chart-2))',
            'Indian Stocks': 'hsl(var(--chart-3))',
            'Mutual Funds': 'hsl(var(--chart-4))',
            'US Stocks': 'hsl(var(--chart-5))',
            'ETFs': 'hsl(var(--chart-6))'
          };
          return colorMap[category] || 'hsl(var(--chart-1))';
        }
        
        // Create SIP data (mock data for now since it's not in the API response)
        // const sips = [
        //   { name: "Nifty 50 Index Fund", amount: 5000, nextDueDate: "2024-08-05" },
        //   { name: "Parag Parikh Flexi Cap", amount: 3000, nextDueDate: "2024-08-10" },
        // ];
        
        // Calculate portfolio summary values from actual holdings data
        const stockValue = assetAllocation
          .filter((item: any) => item.name === 'Indian Stocks')
          .reduce((sum: number, item: any) => sum + item.value, 0);
        
        const mfValue = assetAllocation
          .filter((item: any) => item.name === 'Mutual Funds')
          .reduce((sum: number, item: any) => sum + item.value, 0);
        
        const etfValue = etfHoldings.reduce((sum: number, etf: any) => sum + etf.currentValue, 0);
        
        // Use actual counts from the API data
        const stockCount = get_processed_investment_portfolio?.stock_holdings?.length || 0;
        const mfCount = get_processed_investment_portfolio?.mutual_fund_holdings?.length || 0;
        
        setPortfolioData({
          totalInvestment: totalInvested,
          currentValue: currentValue, // Use the API's total_portfolio_value from portfolio diversification
          overallGain: overallGain,
          overallGainPercentage: overallGainPercentage,
          assetAllocation: assetAllocation,
          holdings: [], // We'll use separate stockHoldings, mutualFundHoldings, and etfHoldings
          stockHoldings: get_processed_investment_portfolio?.stock_holdings || [],
          mutualFundHoldings: get_processed_investment_portfolio?.mutual_fund_holdings || [],
          etfHoldings: etfHoldings,
          portfolioSummary: {
            total_stock_value: stockValue,
            total_mutual_fund_current: mfValue,
            total_portfolio_value: currentValue,
            stock_count: stockCount,
            mutual_fund_count: mfCount,
            formatted_total_portfolio: `₹${currentValue.toLocaleString()}`,
            formatted_stock_value: `₹${stockValue.toLocaleString()}`,
            formatted_mf_current: `₹${mfValue.toLocaleString()}`
          },
          portfolioPerformance: performanceSummary || {
            total_invested: 0,
            current_value: 0,
            absolute_gain: 0,
            overall_xirr: 0
          }
        });

      } catch (err: any) {
        setError(err.message || "An unknown error occurred");
        setPortfolioData(initialPortfolioData);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolioData();
  }, [currentView]);

  // const totalSipAmount = portfolioData.sips.reduce((acc, sip) => acc + sip.amount, 0);

  if (error) {
    return <div className="text-red-500 text-center">Error: {error}</div>
  }

  if (loading) {
    return (
      <div className="grid gap-6">
        {/* Portfolio Overview Cards Skeleton */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">Portfolio Overview</CardTitle>
              <CardDescription>A snapshot of your total investments.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-10 w-32" />
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-20" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">Asset Allocation</CardTitle>
              <CardDescription>How your investments are diversified.</CardDescription>
            </CardHeader>
            <CardContent>
              <Skeleton className="h-48 w-full" />
            </CardContent>
          </Card>
        </div>
        
        {/* Portfolio Summary Skeleton */}
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Portfolio Summary</CardTitle>
            <CardDescription>Detailed breakdown of your investment portfolio.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-3 w-16" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        {/* Holdings Tables Skeleton */}
        <div className="grid gap-6">
          {/* Stock Holdings Skeleton */}
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">Stock Holdings</CardTitle>
              <CardDescription>Your current stock portfolio.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex justify-between items-center">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          
          {/* Mutual Fund Holdings Skeleton */}
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">Mutual Fund Holdings</CardTitle>
              <CardDescription>Your mutual fund investments.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex justify-between items-center">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      {/* Portfolio Overview Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Portfolio Overview</CardTitle>
            <CardDescription>A snapshot of your total investments.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-4xl font-bold tracking-tighter">₹{portfolioData.currentValue.toLocaleString()}</div>
            <div className="flex items-center gap-2 text-sm">
              <span className={`flex items-center gap-1 ${portfolioData.overallGain > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {portfolioData.overallGain > 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                ₹{portfolioData.overallGain.toLocaleString()} ({portfolioData.overallGainPercentage.toFixed(2)}%)
              </span>
              <span className="text-muted-foreground">Overall Gain</span>
            </div>
            <div className="text-sm text-muted-foreground">
              Total Investment: ₹{portfolioData.totalInvestment.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Asset Allocation</CardTitle>
            <CardDescription>How your investments are diversified.</CardDescription>
          </CardHeader>
          <CardContent>
            {portfolioData.assetAllocation.length > 0 ? (
            <ChartContainer config={chartConfig} className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Tooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
                  <Pie
                    data={portfolioData.assetAllocation}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    strokeWidth={5}
                  >
                    {portfolioData.assetAllocation.map((entry) => (
                      <Cell key={`cell-${entry.name}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No asset allocation data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Portfolio Summary Section */}
      <Card>
        <CardHeader>
          <CardTitle className="font-headline">Portfolio Summary</CardTitle>
          <CardDescription>Detailed breakdown of your investment portfolio.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">Total Portfolio Value</div>
              <div className="text-2xl font-bold">{portfolioData.portfolioSummary.formatted_total_portfolio}</div>
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">Stock Value</div>
              <div className="text-2xl font-bold">{portfolioData.portfolioSummary.formatted_stock_value}</div>
              <div className="text-xs text-muted-foreground">{portfolioData.portfolioSummary.stock_count} stocks</div>
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">Mutual Fund Value</div>
              <div className="text-2xl font-bold">{portfolioData.portfolioSummary.formatted_mf_current}</div>
              <div className="text-xs text-muted-foreground">{portfolioData.portfolioSummary.mutual_fund_count} funds</div>
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">ETF Value</div>
              <div className="text-2xl font-bold">₹{portfolioData.etfHoldings.reduce((sum, etf) => sum + etf.currentValue, 0).toLocaleString()}</div>
              <div className="text-xs text-muted-foreground">{portfolioData.etfHoldings.length} ETFs</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Holdings Tables Section */}
      <div className="grid gap-6">
        {/* Stock Holdings Table */}
        {portfolioData.stockHoldings.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">Stock Holdings</CardTitle>
              <CardDescription>Your current stock portfolio from get_processed_investment_portfolio.</CardDescription>
            </CardHeader>
            <CardContent>
              <StockHoldingsTable holdings={portfolioData.stockHoldings} />
            </CardContent>
          </Card>
        )}
        
        {/* Mutual Fund Holdings Table */}
        {portfolioData.mutualFundHoldings.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">Mutual Fund Holdings</CardTitle>
              <CardDescription>Your mutual fund investments from get_processed_investment_portfolio.</CardDescription>
            </CardHeader>
            <CardContent>
              <HoldingsTable holdings={portfolioData.mutualFundHoldings} type="Mutual Fund" />
            </CardContent>
          </Card>
        )}
        
        {/* ETF Holdings Table */}
        {portfolioData.etfHoldings.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">ETF Holdings</CardTitle>
              <CardDescription>Your exchange-traded funds.</CardDescription>
            </CardHeader>
            <CardContent>
              <HoldingsTable holdings={portfolioData.etfHoldings} type="ETF" />
            </CardContent>
          </Card>
        )}

        {/* No Holdings Message */}
        {portfolioData.stockHoldings.length === 0 && portfolioData.mutualFundHoldings.length === 0 && portfolioData.etfHoldings.length === 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">No Holdings Found</CardTitle>
              <CardDescription>No stock, mutual fund, or ETF holdings available.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground py-8">
                No investment holdings found in your portfolio.
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
