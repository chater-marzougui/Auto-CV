"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2, Send, FileText, Mail } from "lucide-react";
import { config } from "@/config";
import { toast } from "sonner";

interface JobAnalysisResult {
  required_technologies: string[];
  experience_level: string;
  analysis_summary: string;
  matched_projects: Array<{
    name: string;
    similarity_score: number;
  }>;
  cv_download_url?: string;
  cover_letter_download_url?: string;
}

interface MatchedProject {
  project: {
    name: string;
    description: string;
    url: string;
    technologies: string[];
  };
  similarity_score: number;
}

interface GenerateApplicationRequest {
  job_description: string;
  personal_info: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    address: string;
    city: string;
    postal_code: string;
    title: string;
    summary: string;
    skills: Record<string, string[]>;
    experience: unknown[];
    education: unknown[];
  };
  selected_projects?: MatchedProject[];
  top_k?: number;
}

export function JobAnalysis() {
  const [jobDescription, setJobDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [analysisResult, setAnalysisResult] =
    useState<JobAnalysisResult | null>(null);
  const [matchedProjects, setMatchedProjects] = useState<MatchedProject[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<MatchedProject[]>([]);

  const analyzeJob = async () => {
    if (!jobDescription.trim()) {
      toast.error("Please enter a job description");
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.analyzeJob}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: "Job Position",
            company: "Company",
            description: jobDescription,
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
          body: JSON.stringify({ job_description: jobDescription }),
        }
      );

      let matchedProjectsData = [];
      if (matchResponse.ok) {
        matchedProjectsData = await matchResponse.json();
        setMatchedProjects(matchedProjectsData);
        setSelectedProjects([]); // Reset selection when new projects are loaded
      }

      setAnalysisResult({
        ...analysis,
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
      setIsAnalyzing(false);
    }
  };

  const handleProjectSelection = (project: MatchedProject, checked: boolean) => {
    if (checked) {
      if (selectedProjects.length < 4) {
        setSelectedProjects([...selectedProjects, project]);
      } else {
        toast.error("You can select at most 4 projects");
      }
    } else {
      setSelectedProjects(selectedProjects.filter(p => p.project.name !== project.project.name));
    }
  };

  const generateApplication = async () => {
    if (selectedProjects.length === 0) {
      toast.error("Please select at least one project");
      return;
    }

    setIsGenerating(true);
    try {
      const requestBody: GenerateApplicationRequest = {
        job_description: jobDescription,
        personal_info: {
          first_name: "John",
          last_name: "Doe",
          email: "john.doe@example.com",
          phone: "+1-555-0123",
          address: "123 Tech Street",
          city: "San Francisco",
          postal_code: "94105",
          title: "Software Developer",
          summary:
            "Experienced software developer with expertise in modern web technologies.",
          skills: {
            "Programming Languages": ["Python", "JavaScript", "TypeScript"],
            "Web Frameworks": ["React", "FastAPI", "Next.js"],
            Databases: ["PostgreSQL", "MongoDB"],
            Tools: ["Docker", "Git", "AWS"],
          },
          experience: [],
          education: [],
        },
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
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border p-6">
        <h1 className="font-heading text-2xl font-bold text-foreground">
          Job Analysis
        </h1>
        <p className="text-muted-foreground mt-1">
          Paste a job description to analyze requirements and generate tailored
          applications
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        {/* Input Section */}
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
            <div className="flex gap-2">
              <Button
                onClick={analyzeJob}
                disabled={isAnalyzing || !jobDescription.trim()}
                className="flex-1"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Analyze Job
                  </>
                )}
              </Button>
              {analysisResult && (
                <Button
                  onClick={generateApplication}
                  disabled={isGenerating || selectedProjects.length === 0}
                  variant="secondary"
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
            </div>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {analysisResult && (
          <div className="space-y-4">
            {/* Job Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Analysis Results</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Required Technologies</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.required_technologies.map((tech, index) => (
                      <Badge key={index} variant="secondary">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Experience Level</h4>
                  <Badge variant="outline">
                    {analysisResult.experience_level}
                  </Badge>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Summary</h4>
                  <p className="text-sm text-muted-foreground">
                    {analysisResult.analysis_summary}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Matched Projects */}
            {matchedProjects.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Matched Projects</CardTitle>
                  <CardDescription>
                    Select up to 4 projects that best match this job ({selectedProjects.length}/4 selected)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {matchedProjects.map((matchedProject, index) => {
                      const isSelected = selectedProjects.some(
                        p => p.project.name === matchedProject.project.name
                      );
                      
                      return (
                        <div
                          key={index}
                          className="flex items-center space-x-3 p-3 border border-border rounded-lg"
                        >
                          <Checkbox
                            checked={isSelected}
                            onCheckedChange={(checked: boolean) => 
                              handleProjectSelection(matchedProject, checked)
                            }
                            disabled={!isSelected && selectedProjects.length >= 4}
                          />
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">{matchedProject.project.name}</span>
                              <Badge variant="secondary">
                                {(matchedProject.similarity_score * 100).toFixed(1)}% match
                              </Badge>
                            </div>
                            {matchedProject.project.description && (
                              <p className="text-sm text-muted-foreground mt-1">
                                {matchedProject.project.description}
                              </p>
                            )}
                            {matchedProject.project.technologies && matchedProject.project.technologies.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {matchedProject.project.technologies.slice(0, 5).map((tech, techIndex) => (
                                  <Badge key={techIndex} variant="outline" className="text-xs">
                                    {tech}
                                  </Badge>
                                ))}
                                {matchedProject.project.technologies.length > 5 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{matchedProject.project.technologies.length - 5} more
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Download Section */}
            {(analysisResult.cv_download_url ||
              analysisResult.cover_letter_download_url) && (
              <Card>
                <CardHeader>
                  <CardTitle>Generated Documents</CardTitle>
                  <CardDescription>
                    Download your tailored CV and cover letter
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4">
                    {analysisResult.cv_download_url && (
                      <Button asChild>
                        <a
                          href={`${config.api.baseUrl}${analysisResult.cv_download_url}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          <FileText className="mr-2 h-4 w-4" />
                          Download CV
                        </a>
                      </Button>
                    )}
                    {analysisResult.cover_letter_download_url && (
                      <Button asChild variant="secondary">
                        <a
                          href={`${config.api.baseUrl}${analysisResult.cover_letter_download_url}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          <Mail className="mr-2 h-4 w-4" />
                          Download Cover Letter
                        </a>
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
