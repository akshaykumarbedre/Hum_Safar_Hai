"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

// Helper: Load JSON from API endpoint
async function fetchAnomalyData() {
  const res = await fetch("http://localhost:8000/tools/financial_audit/5555555555", {
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

export default function AnomalyDashboard() {
  const [loading, setLoading] = useState(true);
  const [anomalies, setAnomalies] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchAnomalyData();
        const txs = data.run_full_financial_audit?.detected_anomalies || [];
        const detected = detectTransactionAnomalies(txs); 
        const detected_anomalies = detected.map(tx => ({          ...tx,
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
  }, []);

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
          <CardTitle className="font-headline">Anomaly Detection</CardTitle>
          <CardDescription>Review detected anomalies in your financial data.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <span className="text-lg font-semibold">Total Anomalies: {anomalies.length}</span>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Anomaly</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Recommendation</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {anomalies.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">No anomalies detected.</TableCell>
                </TableRow>
              ) : (
                anomalies.map((tx, idx) => (
                  <TableRow key={idx} className={tx.anomaly === "High Value" ? "bg-red-50" : tx.anomaly === "Missing Fields" ? "bg-yellow-50" : ""}>
                    <TableCell>{tx.date || "-"}</TableCell>
                    <TableCell>{tx.desc || "-"}</TableCell>
                    <TableCell>{tx.amt?.toLocaleString() || "-"}</TableCell>
                    <TableCell>{tx.type || "-"}</TableCell>
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
