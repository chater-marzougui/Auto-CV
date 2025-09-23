import { Briefcase } from "lucide-react";
import type { JobApplication } from "@/types/JobApplication";
import { JobCard } from "./job-card";

interface JobApplicationsListProps {
  jobApplications: JobApplication[];
  totalCount: number;
  isLoading: boolean;
}

export const JobApplicationsList = ({
  jobApplications,
  totalCount,
  isLoading,
}: Readonly<JobApplicationsListProps>) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Loading job applications...</p>
        </div>
      </div>
    );
  }

  if (jobApplications.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">
            {totalCount === 0
              ? "No applications yet"
              : "No matching applications"}
          </h3>
          <p className="text-muted-foreground mb-4">
            {totalCount === 0
              ? "Start by analyzing a job description and generating an application"
              : "Try adjusting your search or filter criteria"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {jobApplications.map((application) => (
        <JobCard key={application.id} jobApplication={application} />
      ))}
    </div>
  );
};
