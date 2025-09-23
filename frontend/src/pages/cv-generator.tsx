import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2, FileText, Download, Github } from "lucide-react";
import type { Project } from "@/types/project";
import { toast } from "sonner";
import { config } from "@/config";
import LocalHeader from "@/components/header";

export function CVGenerator() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.projects}`
      );
      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects || []);
      }
    } catch (error) {
      console.error("Failed to load projects:", error);
      toast.error("Failed to load projects");
    } finally {
      setIsLoading(false);
    }
  };

  const handleProjectSelection = (project: Project, checked: boolean) => {
    if (checked) {
      if (selectedProjects.length < 8) {
        setSelectedProjects([...selectedProjects, project]);
      } else {
        toast.error("You can select at most 8 projects for your CV");
      }
    } else {
      setSelectedProjects(
        selectedProjects.filter((p) => p.name !== project.name)
      );
    }
  };

  const generateCV = async () => {
    if (selectedProjects.length === 0) {
      toast.error("Please select at least one project");
      return;
    }

    setIsGenerating(true);
    try {
      const reqBody = {
        matched_projects: selectedProjects.map((project) => ({
          project,
          similarity_score: 1.0, // Since manually selected, we consider them 100% relevant
        })),
      };

      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.generateCV}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(reqBody),
        }
      );

      if (!response.ok) throw new Error("Failed to generate application");

      const result = await response.json();
      setDownloadUrl(result.download_url);

      toast.success("CV Generated Successfully", {
        description: "Your CV has been generated and is ready for download",
      });
    } catch (error) {
      toast.error("Failed to generate CV", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-border p-6">
        <LocalHeader
          title="CV Generator"
          description="
            Create a professional CV by selecting your best projects and entering
            your personal information"
        />

        <div className="flex gap-4">
          <Button
            onClick={generateCV}
            disabled={isGenerating || selectedProjects.length === 0}
            className="flex-1 cursor-pointer"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating CV...
              </>
            ) : (
              <>
                <FileText className="mr-2 h-4 w-4" />
                Generate CV
              </>
            )}
          </Button>

          {downloadUrl && (
            <Button asChild variant="secondary" size="lg">
              <a
                href={`${config.api.baseUrl}${downloadUrl}`}
                target="_blank"
                rel="noreferrer"
              >
                <Download className="mr-2 h-4 w-4" />
                Download CV
              </a>
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Github className="h-5 w-5" />
              Select Projects
            </CardTitle>
            <CardDescription>
              Choose up to 8 projects to showcase in your CV (
              {selectedProjects.length}/8 selected)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {projects.length === 0 ? (
              <div className="text-center py-8">
                <Github className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  No projects found. Please scrape your GitHub repositories
                  first.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {projects.map((project, index) => {
                  const isSelected = selectedProjects.some(
                    (p) => p.name === project.name
                  );

                  return (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={(checked: boolean) =>
                          handleProjectSelection(project, checked)
                        }
                        disabled={!isSelected && selectedProjects.length >= 8}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-foreground">
                            {project.name}
                          </h4>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {project.language}
                            </Badge>
                            <Badge variant="secondary" className="text-xs">
                              ⭐ {project.stars}
                            </Badge>
                          </div>
                        </div>

                        {project.three_liner && (
                          <p className="text-sm text-muted-foreground mb-2">
                            {project.three_liner}
                          </p>
                        )}

                        {project.technologies &&
                          project.technologies.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {project.technologies
                                .slice(0, 8)
                                .map((tech, techIndex) => (
                                  <Badge
                                    key={techIndex}
                                    variant="outline"
                                    className="text-xs"
                                  >
                                    {tech}
                                  </Badge>
                                ))}
                              {project.technologies.length > 8 && (
                                <Badge variant="outline" className="text-xs">
                                  +{project.technologies.length - 8} more
                                </Badge>
                              )}
                            </div>
                          )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
