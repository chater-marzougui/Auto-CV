import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Loader2,
  Github,
  Star,
  GitFork,
  RefreshCw,
  Activity,
  AlertTriangle,
  MoreVertical,
  EyeOff,
  Eye,
  Download
} from "lucide-react";
import { config } from "@/config";
import { toast } from "sonner";
import { ProgressCard } from "./progress-card";

interface Project {
  name: string;
  url: string;
  description: string;
  three_liner: string;
  detailed_paragraph: string;
  technologies: string[];
  bad_readme: boolean;
  no_readme: boolean;
  stars: number;
  forks: number;
  language: string;
  created_at: string;
  updated_at: string;
  hidden_from_search?: boolean;
}

export default function ProjectManagement() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [githubUsername, setGithubUsername] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [currentClientId, setCurrentClientId] = useState<string | null>(null);
  const [updatingProjects, setUpdatingProjects] = useState<Set<string>>(new Set());
  const [togglingVisibility, setTogglingVisibility] = useState<Set<string>>(new Set());

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

  const getReadmeStatus = (project: Project) => {
    if (project.no_readme)
      return {
        icon: <AlertTriangle className="h-5 w-5" />, // No README: warning triangle
        variant: "destructive" as const,
        text: "No README",
      };
    if (project.bad_readme)
      return {
        icon: <AlertTriangle className="h-5 w-5" />, // Bad README: warning triangle
        variant: "default" as const,
        text: "Bad README",
      };
    return null;
  };

  const scrapeGithub = async () => {
    if (!githubUsername.trim()) {
      toast.error("Please enter a GitHub username");
      return;
    }

    setIsScraping(true);
    setShowProgress(true);

    try {
      // Start the scraping process
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.scrapeGithub}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ github_username: githubUsername }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to scrape GitHub");
      }

      const result = await response.json();
      setCurrentClientId(result.client_id);

      toast.success(`GitHub scraping initiated for ${githubUsername}`, {
        description: "Check the progress panel for real-time updates",
      });
    } catch (error) {
      toast.error("Failed to scrape GitHub repositories", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
      setShowProgress(false);
    } finally {
      setIsScraping(false);
    }
  };

  const refreshEmbeddings = async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.refreshEmbeddings}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to refresh embeddings");
      }

      toast.success("Embeddings refreshed successfully");
    } catch (error) {
      toast.error("Failed to refresh embeddings", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleProgressClose = () => {
    setShowProgress(false);
  };

  const onCompleteScraping = async () => {
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
      toast.error("Failed to load projects", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
    }
  }

  const toggleProjectVisibility = async (projectName: string, currentlyHidden: boolean) => {
    setTogglingVisibility(prev => new Set(prev.add(projectName)));
    
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.toggleProjectVisibility.replace('{projectName}', projectName)}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ hidden_from_search: !currentlyHidden }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update project visibility");
      }

      // Update the project in local state
      setProjects(prev => prev.map(p => 
        p.name === projectName 
          ? { ...p, hidden_from_search: !currentlyHidden }
          : p
      ));

      toast.success(
        `Project ${!currentlyHidden ? 'hidden from' : 'restored to'} similarity search`,
        {
          description: `${projectName} has been ${!currentlyHidden ? 'hidden' : 'restored'}`,
        }
      );
    } catch (error) {
      toast.error("Failed to update project visibility", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setTogglingVisibility(prev => {
        const next = new Set(prev);
        next.delete(projectName);
        return next;
      });
    }
  };

  const updateSingleProject = async (projectName: string) => {
    setUpdatingProjects(prev => new Set(prev.add(projectName)));
    
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.updateProject.replace('{projectName}', projectName)}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start project update");
      }

      toast.success(`Project update started for ${projectName}`, {
        description: "The project will be re-scraped and updated in the background",
      });

      // Reload projects after a short delay to show updated data
      setTimeout(() => {
        loadProjects();
      }, 2000);
    } catch (error) {
      toast.error("Failed to start project update", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setUpdatingProjects(prev => {
        const next = new Set(prev);
        next.delete(projectName);
        return next;
      });
    }
  };

  if (isLoading && projects.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  const websocketUrl = currentClientId
    ? `ws://localhost:5000/ws/${currentClientId}`
    : null;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-heading text-2xl font-bold text-foreground">
              Project Management
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage your GitHub repositories and project embeddings
            </p>
          </div>

          {/* Progress Toggle */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowProgress(!showProgress)}
            className="flex items-center gap-2"
            disabled={!currentClientId}
          >
            <Activity className="h-4 w-4" />
            {showProgress ? "Hide Progress" : "Show Progress"}
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        {/* GitHub Scraping */}
        <Card>
          <CardHeader>
            <CardTitle>GitHub Integration</CardTitle>
            <CardDescription>
              Scrape repositories from your GitHub profile and track progress in
              real-time
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Enter GitHub username"
                value={githubUsername}
                onChange={(e) => setGithubUsername(e.target.value)}
                className="flex-1"
                disabled={isScraping}
              />
              <Button
                onClick={scrapeGithub}
                disabled={isScraping || !githubUsername.trim()}
              >
                {isScraping ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Github className="mr-2 h-4 w-4" />
                    Scrape Repos
                  </>
                )}
              </Button>
            </div>

            {isScraping && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Initiating GitHub scraping... The progress panel will show
                detailed updates.
              </div>
            )}

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={refreshEmbeddings}
                disabled={isRefreshing || projects.length === 0}
                className="cursor-pointer"
              >
                {isRefreshing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Refreshing...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh Embeddings
                  </>
                )}
              </Button>

              <Button
                variant="outline"
                onClick={loadProjects}
                disabled={isLoading}
                className="cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  "Reload Projects"
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Projects Grid */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-heading text-xl font-semibold">
              Your Projects ({projects.length})
            </h2>
          </div>

          {projects.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Github className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="font-medium text-lg mb-2">No Projects Found</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Enter your GitHub username above to scrape your repositories
                  and see real-time progress
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((project, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex flex-col">
                        <CardTitle className="text-lg font-medium truncate">
                          {project.name}
                        </CardTitle>
                        {project.hidden_from_search && (
                          <Badge variant="outline" className="text-xs mt-1 w-fit">
                            <EyeOff className="h-3 w-3 mr-1" />
                            Hidden from search
                          </Badge>
                        )}
                      </div>
                      <div className="flex gap-1 ml-2 shrink-0">
                        {getReadmeStatus(project) ? (
                          <Badge variant={getReadmeStatus(project)!.variant} className="text-xs p-2">
                            {getReadmeStatus(project)!.icon}
                          </Badge>
                        ) : (
                          <Badge variant="outline">
                            {project.language || "Unknown"}
                          </Badge>
                        )}
                        
                        {/* Dropdown Menu */}
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="h-8 w-8 p-0"
                              disabled={updatingProjects.has(project.name) || togglingVisibility.has(project.name)}
                            >
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => toggleProjectVisibility(project.name, project.hidden_from_search || false)}
                              disabled={togglingVisibility.has(project.name)}
                            >
                              {togglingVisibility.has(project.name) ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              ) : project.hidden_from_search ? (
                                <Eye className="mr-2 h-4 w-4" />
                              ) : (
                                <EyeOff className="mr-2 h-4 w-4" />
                              )}
                              {project.hidden_from_search ? 'Show in search' : 'Hide from search'}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              onClick={() => updateSingleProject(project.name)}
                              disabled={updatingProjects.has(project.name)}
                            >
                              {updatingProjects.has(project.name) ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              ) : (
                                <Download className="mr-2 h-4 w-4" />
                              )}
                              Update project
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    <CardDescription className="line-clamp-2">
                      {project.three_liner ||
                        project.description ||
                        "No description available"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4" />
                        {project.stars}
                      </div>
                      <div className="flex items-center gap-1">
                        <GitFork className="h-4 w-4" />
                        {project.forks}
                      </div>
                    </div>

                    {project.technologies &&
                      project.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 items-center">
                          {project.technologies
                            .slice(0, 3)
                            .map((tech, techIndex) => (
                              <Badge
                                key={techIndex}
                                variant="secondary"
                                className="text-xs"
                              >
                                {tech}
                              </Badge>
                            ))}
                          {project.technologies.length > 3 && (
                            <div className="relative group">
                              <Badge
                                variant="secondary"
                                className="text-xs cursor-pointer select-none"
                              >
                                +{project.technologies.length - 3}
                              </Badge>
                              <div className="absolute left-0 z-10 mt-1 hidden group-hover:flex flex-col bg-popover border border-border rounded shadow-lg p-2 min-w-max">
                                {project.technologies
                                  .slice(3)
                                  .map((tech, idx) => (
                                    <span
                                      key={idx}
                                      className="text-xs px-2 py-1 rounded hover:bg-muted"
                                    >
                                      {tech}
                                    </span>
                                  ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                    <Button
                      asChild
                      variant="outline"
                      size="sm"
                      className="w-full bg-transparent text-blue-400 hover:text-blue-500"
                    >
                      <a
                        href={project.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Github className="mr-2 h-4 w-4" />
                        View on GitHub
                      </a>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Progress Card - Fixed positioned overlay */}
      {websocketUrl && (
        <ProgressCard
          isVisible={showProgress}
          onClose={handleProgressClose}
          websocketUrl={websocketUrl}
          onComplete={onCompleteScraping}
        />
      )}
    </div>
  );
}
