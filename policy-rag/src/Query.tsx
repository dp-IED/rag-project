import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, Search, Upload, ArrowLeft } from "lucide-react";
import { PolicyResult } from "./types";
import { api } from "../src/lib/api";

export function QueryPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PolicyResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await api.queryDocuments(query);
      setResults(data.responses);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <Button variant="ghost" onClick={() => navigate("/")} className="mb-4">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Home
      </Button>

      <div className="w-full max-w-4xl mx-auto space-y-4">
        <div className="flex justify-end">
          <Button onClick={() => navigate("/upload")} variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            Upload More Documents
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Policy Query System</CardTitle>
            <CardDescription>
              Search through policy documents using natural language queries
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2">
              <Input
                placeholder="Enter your query..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="flex-1"
              />
              <Button
                onClick={handleSearch}
                disabled={loading || !query.trim()}
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Search className="w-4 h-4 mr-2" />
                )}
                Search
              </Button>
            </div>
          </CardContent>
        </Card>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {results.map((result, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="text-lg">Source: {result.source}</CardTitle>
              <CardDescription>
                Relevance Score: {result.score.toFixed(2)}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Statement</h4>
                <p className="text-sm text-slate-600">{result.statement}</p>
              </div>
              {result.context.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Context</h4>
                  <div className="bg-slate-50 p-3 rounded-md text-sm text-slate-600">
                    {result.context.map((ctx, i) => (
                      <p
                        key={i}
                        className={
                          ctx === result.statement ? "font-medium" : ""
                        }
                      >
                        {ctx}
                      </p>
                    ))}
                  </div>
                </div>
              )}
              {result.topics.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {result.topics.map((topic, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
