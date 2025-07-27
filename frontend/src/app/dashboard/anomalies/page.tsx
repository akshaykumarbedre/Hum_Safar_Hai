"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, DollarSign, Copy, CheckCircle } from "lucide-react";

// User data based on the financial intelligence data
const availableUsers = [
  { id: "1111111111", name: "Basic Saver" },
  { id: "2222222222", name: "Wealthy Investor" },
  { id: "3333333333", name: "Moderate Investor" },
  { id: "4444444444", name: "Multi-bank User" },
  { id: "5555555555", name: "Standard User" },
  { id: "6666666666", name: "Investment Expert" },
  { id: "7777777777", name: "High Debt User" },
  { id: "8888888888", name: "SIP Investor" },
  { id: "9999999999", name: "Conservative User" },
  { id: "1010101010", name: "Gold Investor" },
];

// Helper: Load JSON from API endpoint
async function fetchAnomalyData(userId: string) {
  const res = await fetch(`http://localhost:8000/tools/financial_audit/${userId}`, {
    headers: { "accept": "application/json" }
  });
  if (!res.ok) {
    throw new Error("Failed to fetch anomaly data");
  }
  const data = await res.json();
  console.log("data in fetch anomaly", data);
  return data;
}

// Helper: Detect anomalies in transactions
interface Transaction {
    date?: string;
    desc?: string;
    amt?: number;
    type?: string;
    [key: string]: any;
}

type AnomalyType = "Missing Fields" | "High Value" | "Duplicate Transaction";

interface TransactionAnomaly extends Transaction {
    anomaly: AnomalyType;
}

function detectTransactionAnomalies(transactions: Transaction[]): TransactionAnomaly[] {
    const anomalies: TransactionAnomaly[] = [];
    const seen = new Set<string>();
    for (const tx of transactions) {
        if (!tx.date || !tx.desc || !tx.amt) {
            anomalies.push({ ...tx, anomaly: "Missing Fields" });
            continue;
        }
        if (tx.amt > 100000) {
            anomalies.push({ ...tx, anomaly: "High Value" });
        }
        const key = `${tx.date}-${tx.desc}-${tx.amt}`;
        if (seen.has(key)) {
            anomalies.push({ ...tx, anomaly: "Duplicate Transaction" });
        }
        seen.add(key);
    }
    return anomalies;
}

const getAnomalyIcon = (anomalyType: AnomalyType) => {
  switch (anomalyType) {
    case "High Value":
      return <DollarSign className="h-4 w-4" />;
    case "Duplicate Transaction":
      return <Copy className="h-4 w-4" />;
    case "Missing Fields":
      return <AlertTriangle className="h-4 w-4" />;
    default:
      return <AlertTriangle className="h-4 w-4" />;
  }
};

const getAnomalyBadge = (anomalyType: AnomalyType) => {
  switch (anomalyType) {
    case "High Value":
      return <Badge variant="destructive" className="flex items-center gap-1">
        <DollarSign className="h-3 w-3" />
        High Value
      </Badge>;
    case "Duplicate Transaction":
      return <Badge variant="outline" className="flex items-center gap-1">
        <Copy className="h-3 w-3" />
        Duplicate
      </Badge>;
    case "Missing Fields":
      return <Badge variant="outline" className="flex items-center gap-1">
        <AlertTriangle className="h-3 w-3" />
        Missing Data
      </Badge>;
    default:
      return <Badge variant="outline">Unknown</Badge>;
  }
};

export default function AnomalyDashboard() {
  const [loading, setLoading] = useState(true);
  const [anomalies, setAnomalies] = useState([]);
  const [error, setError] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState("5555555555");

  const selectedUser = availableUsers.find(user => user.id === selectedUserId);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchAnomalyData(selectedUserId);
        const txs = data.run_full_financial_audit?.detected_anomalies || [];
        const detected = detectTransactionAnomalies(txs); 
        const detected_anomalies = detected.map(tx => ({
          ...tx,
          date: tx.anomaly_code || "-",
          desc: tx.anomaly_title || "-",
          amt: tx.description ? `${tx.description.toLocaleString()}` : "-",
          type: tx.recommendation || "-",
        }));
        console.log("Detected anomalies:", detected_anomalies);
        setAnomalies(detected_anomalies);
      } catch (e) {
        setError("Failed to load anomaly data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selectedUserId]);

  if (error) {
    return <div className="text-red-500 text-center">{error}</div>;
  }

  if (loading) {
    return (
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Anomaly Detection</CardTitle>
            <CardDescription>Review detected anomalies in your financial data.</CardDescription>
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-40 mb-4" />
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="font-headline flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Anomaly Detection
              </CardTitle>
              <CardDescription>Review detected anomalies for {selectedUser?.name}</CardDescription>
            </div>
            <Select value={selectedUserId} onValueChange={setSelectedUserId}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {availableUsers.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-2">
              {anomalies.length === 0 ? (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span className="text-lg font-semibold">No Anomalies Detected</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-orange-600">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="text-lg font-semibold">
                    {anomalies.length} Anomal{anomalies.length === 1 ? 'y' : 'ies'} Found
                  </span>
                </div>
              )}
            </div>
            {anomalies.length > 0 && (
              <div className="flex gap-2">
                <Badge variant="destructive" className="text-xs">
                  {anomalies.filter(a => a.anomaly === "High Value").length} High Value
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {anomalies.filter(a => a.anomaly === "Duplicate Transaction").length} Duplicates
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {anomalies.filter(a => a.anomaly === "Missing Fields").length} Missing Data
                </Badge>
              </div>
            )}
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Recommendation</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {anomalies.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8">
                    <div className="flex flex-col items-center gap-2 text-muted-foreground">
                      <CheckCircle className="h-8 w-8 text-green-500" />
                      <span>No anomalies detected in financial data</span>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                anomalies.map((tx, idx) => (
                  <TableRow key={idx} className="hover:bg-muted/50">
                    <TableCell>
                      {getAnomalyBadge(tx.anomaly)}
                    </TableCell>
                    <TableCell className="font-medium">{tx.desc || "-"}</TableCell>
                    <TableCell className="max-w-xs truncate">{tx.amt || "-"}</TableCell>
                    <TableCell className="max-w-sm">
                      <div className="text-sm text-muted-foreground">
                        {tx.type || "No recommendation available"}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
