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
import { Loader2, Github, RefreshCw, Activity } from "lucide-react";
import { config } from "@/config";
import { toast } from "sonner";
import { ProgressCard } from "../components/progress-card";
import { RepoCard } from "../components/repo-card";
import { useProjectEdit } from "@/hooks/use-project-edit";
import type { Project } from "@/types/project";

export default function ProjectManagement() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [githubUsername, setGithubUsername] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [currentClientId, setCurrentClientId] = useState<string | null>(null);
  const [updatingProjects, setUpdatingProjects] = useState<Set<string>>(
    new Set()
  );
  const [togglingVisibility, setTogglingVisibility] = useState<Set<string>>(
    new Set()
  );

  // Edit functionality
  const {
    editingProject,
    editState,
    isUpdating: isEditUpdating,
    startEdit,
    cancelEdit,
    updateEditState,
    saveEdit,
  } = useProjectEdit();

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
  };

  const toggleProjectVisibility = async (
    projectName: string,
    currentlyHidden: boolean
  ) => {
    setTogglingVisibility((prev) => new Set(prev.add(projectName)));

    try {
      const response = await fetch(
        `${
          config.api.baseUrl
        }${config.api.endpoints.toggleProjectVisibility.replace(
          "{projectName}",
          projectName
        )}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ hidden_from_search: !currentlyHidden }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Failed to update project visibility"
        );
      }

      // Update the project in local state
      setProjects((prev) =>
        prev.map((p) =>
          p.name === projectName
            ? { ...p, hidden_from_search: !currentlyHidden }
            : p
        )
      );

      toast.success(
        `Project ${
          !currentlyHidden ? "hidden from" : "restored to"
        } similarity search`,
        {
          description: `${projectName} has been ${
            !currentlyHidden ? "hidden" : "restored"
          }`,
        }
      );
    } catch (error) {
      toast.error("Failed to update project visibility", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setTogglingVisibility((prev) => {
        const next = new Set(prev);
        next.delete(projectName);
        return next;
      });
    }
  };

  const handleSaveEdit = async (projectName: string): Promise<boolean> => {
    const success = await saveEdit(projectName);
    if (success) {
      // Reload projects to show updated content
      await loadProjects();
    }
    return success;
  };

  const updateSingleProject = async (projectName: string) => {
    setUpdatingProjects((prev) => new Set(prev.add(projectName)));

    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.updateProject.replace(
          "{projectName}",
          projectName
        )}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start project update");
      }

      toast.success(`Project update started for ${projectName}`, {
        description:
          "The project will be re-scraped and updated in the background",
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
      setUpdatingProjects((prev) => {
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
        <div className="space-y-4 w-full">
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
            <div className="flex flex-wrap gap-4 items-center justify-center">
              {projects.map((project, index) => (
                <RepoCard
                  key={index}
                  index={index}
                  project={project}
                  isUpdating={updatingProjects.has(project.name)}
                  isTogglingVisibility={togglingVisibility.has(project.name)}
                  toggleProjectVisibility={toggleProjectVisibility}
                  updateSingleProject={updateSingleProject}
                  isEditing={editingProject === project.name}
                  editState={editState}
                  isEditUpdating={isEditUpdating}
                  onStartEdit={startEdit}
                  onCancelEdit={cancelEdit}
                  onSaveEdit={handleSaveEdit}
                  onUpdateEditState={updateEditState}
                />
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
