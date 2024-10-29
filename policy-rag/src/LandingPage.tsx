import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Search, Upload } from "lucide-react";
import { api } from "../src/lib/api";

export function LandingPage() {
  const [checking, setChecking] = useState(true);
  const [userDocs, setUserDocs] = useState<string[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const checkDocuments = async () => {
      try {
        const { files } = await api.checkDocuments();
        console.log("fileNames", files);
        setUserDocs(files);
      } catch (error) {
        console.error("Failed to check documents", error);
      } finally {
        setChecking(false);
      }
    };

    checkDocuments();
  }, []);

  if (checking) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <Card className="max-w-2xl mx-auto mt-16">
        <CardHeader>
          <CardTitle className="text-2xl">Policy Document Analyzer</CardTitle>
          <CardDescription>
            Analyze and query policy documents using natural language processing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-600">
            This application helps you analyze policy documents and extract
            relevant information using natural language queries. Upload your
            documents and start exploring their contents with powerful search
            capabilities.
          </p>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-800 mb-2">Features:</h3>
            <ul className="list-disc list-inside text-blue-700 space-y-1">
              <li>Upload and process policy documents</li>
              <li>Search using natural language queries</li>
              <li>View relevant context and topics</li>
              <li>Track document sources and relevance</li>
            </ul>
          </div>

          {userDocs.length > 0 && (
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-medium text-green-800 mb-2">
                Your Documents:
              </h3>
              <ul className="list-disc list-inside text-green-700 space-y-1">
                {userDocs.map((doc) => (
                  <li key={doc}>{doc}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-center align-center space-x-4">
          <Button
            size="lg"
            onClick={() => navigate("/upload")}
            className="w-full max-w-sm"
          >
            <Upload className="w-5 h-5 mr-2" />
            {userDocs.length > 0
              ? "Upload Another Document"
              : "Upload Your First Document"}
          </Button>

          {userDocs.length > 0 && (
            <Button
              size="lg"
              onClick={() => navigate("/query")}
              className="w-full max-w-sm"
            >
              <Search className="w-5 h-5 mr-2" />
              Query Documents
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
