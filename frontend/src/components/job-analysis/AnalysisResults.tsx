import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";


interface JobDescriptionResult {
  title: string;
  company: string;
  required_technologies: string[];
  experience_level: string;
  soft_skills: string[];
  analysis_summary: string;
  full_description: string;
  requirements: string;
}

// Analysis Results Component
export function AnalysisResults({
  analysisResult,
}: {
  readonly analysisResult: Readonly<JobDescriptionResult | null>;
}) {
  if (!analysisResult) return null;

  const job_analysis_result = analysisResult;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Analysis Results</CardTitle>
        <CardDescription>
          Key insights from the job description analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div>
              <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-2">
                Required Technologies
              </h4>
              <div className="flex flex-wrap gap-2">
                {job_analysis_result.required_technologies.map(
                  (tech, index) => (
                    <Badge key={index} variant="secondary">
                      {tech}
                    </Badge>
                  )
                )}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-2">
                Experience Level
              </h4>
              <Badge variant="outline" className="font-medium">
                {job_analysis_result.experience_level}
              </Badge>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-2">
              Soft Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {job_analysis_result.soft_skills.map((skill, index) => (
                <Badge key={index} variant="outline">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        <div>
          <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-2">
            Analysis Summary
          </h4>
          <p className="text-sm text-foreground leading-relaxed">
            {job_analysis_result.analysis_summary}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}