"use client";

import { useState } from "react";
import { config } from "@/config";
import { toast } from "sonner";
import { AnalysisResults } from "@/components/job-analysis/AnalysisResults";
import { JobAnalysisHeader } from "@/components/job-analysis/JobAnalysisHeader";
import { ProjectSelection } from "@/components/job-analysis/ProjectSelection";
import type { MatchedProject } from "@/types/project";
import { JobDescriptionInput } from "@/components/job-analysis/JobDescriptionInput";
import { ProgressCard } from "@/components/progress-card";
interface JobAnalysisResult {
  job_analysis_result: JobDescriptionResult;
  matched_projects: Array<{
    name: string;
    similarity_score: number;
  }>;
  cv_download_url?: string;
  cover_letter_download_url?: string;
}

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

interface GenerateApplicationRequest {
  job_description: JobDescriptionResult;
  personal_info_id: string | number | null;
  selected_projects?: MatchedProject[];
  top_k?: number;
  client_id?: string;
}

export function JobAnalysis() {
  const [jobDescription, setJobDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const userId = localStorage.getItem("user_id") || null;
  const [analysisResult, setAnalysisResult] =
    useState<JobAnalysisResult | null>(null);
  const [matchedProjects, setMatchedProjects] = useState<MatchedProject[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<MatchedProject[]>(
    []
  );
  const [showProgress, setShowProgress] = useState(false);
  const clientId = `job-analysis-${userId || "guest"}}`;

  const analyzeJob = async () => {
    if (!jobDescription.trim()) {
      toast.error("Please enter a job description");
      return;
    }

    setIsAnalyzing(true);
    setShowProgress(true);
    
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.analyzeJob}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            description: jobDescription,
            client_id: clientId,
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to analyze job");

      const analysis = await response.json();

      // Also get matching projects
      const matchResponse = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.matchProjects}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_description: analysis,
            client_id: clientId,
          }),
        }
      );

      let matchedProjectsData = [];
      if (matchResponse.ok) {
        matchedProjectsData = await matchResponse.json();
        setMatchedProjects(matchedProjectsData);
        setSelectedProjects([]); // Reset selection when new projects are loaded
      }

      setAnalysisResult({
        job_analysis_result: analysis,
        matched_projects: matchedProjectsData.map((mp: MatchedProject) => ({
          name: mp.project.name,
          similarity_score: mp.similarity_score,
        })),
      });

      toast.success("Analysis Complete", {
        description: "Job description analyzed successfully",
      });
    } catch (error) {
      toast.error("Failed to analyze job description", {
        description: error instanceof Error ? `: ${error.message}` : "",
      });
    } finally {
      setShowProgress(false);
      setIsAnalyzing(false);
    }
  };

  const handleProjectSelection = (
    project: MatchedProject,
    checked: boolean
  ) => {
    if (checked) {
      if (selectedProjects.length < 4) {
        setSelectedProjects([...selectedProjects, project]);
      } else {
        toast.error("You can select at most 4 projects");
      }
    } else {
      setSelectedProjects(
        selectedProjects.filter((p) => p.project.name !== project.project.name)
      );
    }
  };

  const generateApplication = async () => {
    if (!userId) {
      toast.error(
        "User ID not found. Please fill in your personal information."
      );
      return;
    }

    if (selectedProjects.length === 0) {
      toast.error("Please select at least one project");
      return;
    }

    if (!analysisResult) {
      toast.error("Please analyze a job description first");
      return;
    }

    setIsGenerating(true);
    setShowProgress(true);
    
    try {
      const requestBody: GenerateApplicationRequest = {
        personal_info_id: userId,
        job_description: analysisResult.job_analysis_result,
        client_id: clientId,
      };

      // If projects are selected, pass them instead of using top_k
      if (selectedProjects.length > 0) {
        requestBody.selected_projects = selectedProjects;
      } else {
        requestBody.top_k = 4;
      }

      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.generateApplication}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) throw new Error("Failed to generate application");

      const result = await response.json();

      setAnalysisResult((prev) =>
        prev
          ? {
              ...prev,
              cv_download_url: result.cv.download_url,
              cover_letter_download_url: result.cover_letter.download_url,
            }
          : null
      );

      toast.success("Application Generated", {
        description: "CV and cover letter generated successfully",
      });
    } catch (error) {
      toast("Failed to generate application", {
        description: error instanceof Error ? `: ${error.message}` : "",
      });
    } finally {
      setShowProgress(false);
      setIsGenerating(false);
    }
  };

  const handleProgressClose = () => {
    setShowProgress(false);
  };

  return (
    <div className="flex flex-col h-full">
      <JobAnalysisHeader
        analysisResult={analysisResult}
        isGenerating={isGenerating}
        onGenerate={generateApplication}
        selectedProjectsCount={selectedProjects.length}
        showProgress={showProgress}
        onToggleProgress={() => setShowProgress(!showProgress)}
        hasActiveClient={!!clientId}
      />

      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <JobDescriptionInput
          jobDescription={jobDescription}
          setJobDescription={setJobDescription}
          isAnalyzing={isAnalyzing}
          onAnalyze={analyzeJob}
        />

        <AnalysisResults analysisResult={analysisResult?.job_analysis_result || null} />

        <ProjectSelection
          matchedProjects={matchedProjects}
          selectedProjects={selectedProjects}
          onProjectSelection={handleProjectSelection}
        />
      </div>

      {/* Progress Card - Fixed positioned overlay */}
      {userId && (
        <ProgressCard
          isVisible={showProgress}
          title="Job Analysis Progress"
          onClose={handleProgressClose}
          websocketUrl={`ws://localhost:5000/ws/${clientId}`}
        />
      )}
    </div>
  );
}