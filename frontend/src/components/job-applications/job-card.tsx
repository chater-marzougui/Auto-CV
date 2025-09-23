import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Calendar, FileText, Mail, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { JobApplication } from "@/types/JobApplication";

const JobDescription: React.FC<{ description: string }> = ({ description }) => (
  <div>
    <p className="text-sm text-muted-foreground line-clamp-2">
      {description.substring(0, 200)}
      {description.length > 200 && "..."}
    </p>
  </div>
);

const RenderJobDescription: React.FC<{ jobApplication: JobApplication }> = ({
  jobApplication,
}) => {
  if (jobApplication.job_description) {
    return <JobDescription description={jobApplication.job_description} />;
  } else if (jobApplication.job_requirements) {
    return <JobDescription description={jobApplication.job_requirements} />;
  }
  return null;
};

export const JobCard: React.FC<{ jobApplication: JobApplication }> = ({
  jobApplication,
}) => {
  const getStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "applied":
        return "default";
      case "interview":
        return "secondary";
      case "accepted":
        return "default";
      case "rejected":
        return "destructive";
      default:
        return "outline";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "applied":
        return "text-blue-600";
      case "interview":
        return "text-yellow-600";
      case "accepted":
        return "text-green-600";
      case "rejected":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <Card key={jobApplication.id} className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">
              {jobApplication.job_title}
            </CardTitle>
            <CardDescription className="flex items-center gap-2 mt-1">
              <span>{jobApplication.company_name}</span>
              <Badge
                variant={getStatusBadgeVariant(jobApplication.status)}
                className={getStatusColor(jobApplication.status)}
              >
                {jobApplication.status}
              </Badge>
            </CardDescription>
          </div>
          <div className="text-sm text-muted-foreground text-right">
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {new Date(jobApplication.application_date).toLocaleDateString()}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Job Description Preview */}
          <RenderJobDescription jobApplication={jobApplication} />
          {/* Download Links */}
          <div className="flex flex-wrap gap-2">
            {jobApplication.cv_download_url && (
              <Button variant="outline" size="sm" asChild>
                <a
                  href={jobApplication.cv_download_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2"
                >
                  <FileText className="h-4 w-4" />
                  CV
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
            )}
            {jobApplication.cover_letter_download_url && (
              <Button variant="outline" size="sm" asChild>
                <a
                  href={jobApplication.cover_letter_download_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2"
                >
                  <Mail className="h-4 w-4" />
                  Cover Letter
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
            )}
          </div>

          {/* Notes */}
          {jobApplication.notes && (
            <div>
              <p className="text-sm">
                <span className="font-medium">Notes: </span>
                {jobApplication.notes}
              </p>
            </div>
          )}

          {/* Matched Projects Count */}
          {jobApplication.matched_projects &&
            jobApplication.matched_projects.length > 0 && (
              <div className="text-sm text-muted-foreground">
                {jobApplication.matched_projects.length} project(s) matched
              </div>
            )}
        </div>
      </CardContent>
    </Card>
  );
};
