import { useEffect, useState } from "react";
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
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Upload, ArrowLeft, Search } from "lucide-react";
import { StatusMessage } from "../src/types";
import { api } from "../src/lib/api";

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<StatusMessage | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [userDocs, setUserDocs] = useState<string[]>([]);
  const [checking, setChecking] = useState(true);
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
  }, [uploadComplete]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && !selectedFile.name.endsWith(".txt")) {
      setStatus({ type: "error", message: "Only .txt files are supported" });
      return;
    }
    setFile(selectedFile || null);
    setStatus(null);
  };

  if (checking) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  const handleUpload = async () => {
    if (!file) {
      setStatus({ type: "error", message: "Please select a file" });
      return;
    }

    setIsUploading(true);
    setStatus({ type: "info", message: "Uploading..." });

    try {
      const response = await api.uploadDocument(file);
      setStatus({
        type: "success",
        message: `${response.message} (Document ID: ${response.doc_id})`,
      });
      setFile(null);
      const fileInput =
        document.querySelector<HTMLInputElement>('input[type="file"]');
      if (fileInput) fileInput.value = "";
      setUploadComplete(true);
    } catch (error) {
      setStatus({
        type: "error",
        message: error instanceof Error ? error.message : "Upload failed",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <Button variant="ghost" onClick={() => navigate("/")} className="mb-4">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Home
      </Button>

      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-xl">Upload Policy Document</CardTitle>
          <CardDescription>
            {uploadComplete
              ? "Document uploaded successfully! What would you like to do next?"
              : "Start by uploading a text document to analyze"}
          </CardDescription>
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
        </CardHeader>

        {!uploadComplete ? (
          <CardContent className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-medium text-blue-800 mb-2">
                Document Requirements:
              </h3>
              <ul className="list-disc list-inside text-blue-700 space-y-1">
                <li>Text (.txt) files only</li>
                <li>Clear, structured text</li>
              </ul>
            </div>

            <div className="grid w-full gap-4">
              <input
                type="file"
                accept=".txt"
                onChange={handleFileChange}
                className="block w-full text-sm text-slate-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />

              <CardFooter className="flex flex-col space-y-3">
                <Button onClick={() => handleUpload()} className="w-full">
                  {isUploading ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Upload className="w-4 h-4 mr-2" />
                  )}
                  {isUploading ? "Uploading..." : "Upload Document"}
                </Button>
                {userDocs.length > 0 ? (
                  <Button
                    onClick={() => navigate("/query")}
                    variant="secondary"
                    className="w-full"
                  >
                    <Search className="w-4 h-4 mr-2" />
                    Continue to Query
                  </Button>
                ) : null}
              </CardFooter>

              {status && (
                <Alert
                  variant={status.type === "error" ? "destructive" : "default"}
                >
                  <AlertDescription>{status.message}</AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        ) : (
          <CardFooter className="flex justify-center align-center space-x-4">
            <Button
              size="lg"
              onClick={() => navigate("/upload")}
              className="w-full max-w-sm"
            >
              {isUploading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Upload className="w-4 h-4 mr-2" />
              )}
              {isUploading ? "Uploading..." : "Upload Document"}
            </Button>
            <Button
              size="lg"
              onClick={() => navigate("/query")}
              className="w-full max-w-sm"
            >
              <Search className="w-4 h-4 mr-2" />
              Query Documents
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
