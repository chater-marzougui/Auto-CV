
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Send } from "lucide-react";
// Job Description Input Component
interface JobDescriptionInputProps {
  jobDescription: string;
  setJobDescription: (value: string) => void;
  isAnalyzing: boolean;
  onAnalyze: () => void;
}

export function JobDescriptionInput({
  jobDescription,
  setJobDescription,
  isAnalyzing,
  onAnalyze,
}: Readonly<JobDescriptionInputProps>) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Description</CardTitle>
        <CardDescription>
          Paste the job description you want to apply for
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          placeholder="Paste the job description here..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          className="min-h-[200px]"
        />
        <Button
          onClick={onAnalyze}
          disabled={isAnalyzing || !jobDescription.trim()}
          className="cursor-pointer w-full"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analyzing Job Description...
            </>
          ) : (
            <>
              <Send className="mr-2 h-4 w-4" />
              Analyze Job Description
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}