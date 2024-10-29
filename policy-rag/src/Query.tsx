import { useState, useRef } from "react";
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
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { PolicyResult } from "./types";
import { api } from "../src/lib/api";
import MarkdownContent from "./lib/MarkdownContent";

export function QueryPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PolicyResult[]>([]);
  const [streamedResponse, setStreamedResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const responseRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setStreamedResponse("");

    try {
      const data = await api.queryDocuments(query);
      setResults(data.responses);

      // Handle streaming response
      await api.summarizeFindings(data.responses, query, {
        onToken: (token) => {
          setStreamedResponse((prev) => prev + token);
          // Auto-scroll to bottom as new content arrives
          if (responseRef.current) {
            responseRef.current.scrollTop = responseRef.current.scrollHeight;
          }
        },
        onComplete: (fullResponse) => {
          setStreamedResponse(fullResponse);
        },
        onError: (error) => {
          setError(error.message);
        },
      });
    } catch (error) {
      setError(error instanceof Error ? error.message : "Search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <div className="flex justify-between  mx-auto">
        <Button variant="ghost" onClick={() => navigate("/")} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Button>

        <Button
          variant="outline"
          onClick={() => navigate("/upload")}
          className="mb-4"
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload Document
        </Button>
      </div>

      <div className="w-full max-w-4xl mx-auto space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Policy Analysis System</CardTitle>
            <CardDescription>
              Analyze policy documents using natural language queries
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
              <Button onClick={handleSearch} disabled={loading}>
                {loading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Search className="w-4 h-4 mr-2" />
                )}
                Analyze
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

        <div className="grid grid-cols-1 gap-6">
          {streamedResponse && <MarkdownContent content={streamedResponse} />}

          {results.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="text-sm text-slate-600 mb-4">
                Source Documents
              </div>
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div key={index} className="p-4 bg-slate-50 rounded-lg">
                    <div className="text-sm text-slate-500 mb-2">
                      Source: {result.source} (Score: {result.score.toFixed(2)})
                    </div>
                    <div className="text-sm text-slate-700">
                      {result.statement}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
