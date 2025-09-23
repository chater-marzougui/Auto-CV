import { Button } from "@/components/ui/button";
import { Loader2, FileText, Mail, Download, Activity } from "lucide-react";
import { config } from "@/config";
import LocalHeader from "../header";

interface Links {
  cv_download_url?: string;
  cover_letter_download_url?: string;
}

interface JobAnalysisHeaderProps {
  analysisResult: Links | null;
  isGenerating: boolean;
  onGenerate: () => void;
  selectedProjectsCount: number;
  showProgress: boolean;
  onToggleProgress: () => void;
  hasActiveClient: boolean;
}

// Header Component
export function JobAnalysisHeader({
  analysisResult,
  isGenerating,
  onGenerate,
  selectedProjectsCount,
  showProgress,
  onToggleProgress,
  hasActiveClient,
}: Readonly<JobAnalysisHeaderProps>) {
  const baseUrl = config.api.baseUrl;
  const hasDownloads =
    analysisResult?.cv_download_url ||
    analysisResult?.cover_letter_download_url;

  return (
    <div className="border-b border-border p-6">
      <div className="flex items-center justify-between">
        <LocalHeader
          title="Job Analysis"
          description="
            Paste a job description to analyze requirements and generate
            tailored applications"
        />

        <div className="flex flex-wrap items-center gap-3">
          {/* Progress Toggle */}
          <Button
            variant="outline"
            size="sm"
            onClick={onToggleProgress}
            className="flex items-center gap-2 cursor-pointer"
            disabled={!hasActiveClient}
          >
            <Activity className="h-4 w-4" />
            {showProgress ? "Hide Progress" : "Show Progress"}
          </Button>

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
                    href={`${baseUrl}${analysisResult.cv_download_url}`}
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
                    href={`${baseUrl}${analysisResult.cover_letter_download_url}`}
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
