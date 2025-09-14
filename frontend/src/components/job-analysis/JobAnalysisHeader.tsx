
import { Button } from "@/components/ui/button";
import { Loader2, FileText, Mail, Download } from "lucide-react";

interface Links {
    cv_download_url?: string;
    cover_letter_download_url?: string;
}

interface JobAnalysisHeaderProps {
  analysisResult: Links | null;
  isGenerating: boolean;
  onGenerate: () => void;
  selectedProjectsCount: number;
}

// Header Component
export function JobAnalysisHeader({
  analysisResult,
  isGenerating,
  onGenerate,
  selectedProjectsCount,
}: Readonly<JobAnalysisHeaderProps>) {
  const hasDownloads =
    analysisResult?.cv_download_url ||
    analysisResult?.cover_letter_download_url;

  return (
    <div className="border-b border-border p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-foreground">
            Job Analysis
          </h1>
          <p className="text-muted-foreground mt-1">
            Paste a job description to analyze requirements and generate
            tailored applications
          </p>
        </div>

        <div className="flex items-center gap-3">
          {analysisResult && (
            <Button
              onClick={onGenerate}
              disabled={isGenerating || selectedProjectsCount === 0}
              variant="default"
              className="cursor-pointer"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="mr-2 h-4 w-4" />
                  Generate Application
                </>
              )}
            </Button>
          )}

          {hasDownloads && (
            <div className="flex gap-2">
              {analysisResult.cv_download_url && (
                <Button asChild size="sm" variant="outline">
                  <a
                    href={analysisResult.cv_download_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    CV
                  </a>
                </Button>
              )}
              {analysisResult.cover_letter_download_url && (
                <Button asChild size="sm" variant="outline">
                  <a
                    href={analysisResult.cover_letter_download_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Mail className="mr-2 h-4 w-4" />
                    Cover Letter
                  </a>
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
