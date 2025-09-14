import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function InstructionsCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>How to Use</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm text-muted-foreground">
        <p>1. Fill in your personal information, skills, experience, and education</p>
        <p>2. Go to the Job Analysis tab and paste a job description</p>
        <p>3. Click "Analyze Job" to see matching projects</p>
        <p>
          4. Click "Generate Application" to create your tailored CV and
          cover letter
        </p>
        <p>
          5. Download the generated documents from the Job Analysis page
        </p>
      </CardContent>
    </Card>
  );
}