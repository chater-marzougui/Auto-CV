import React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { TagInput } from "@/components/ui/tag-input";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Eye,
  EyeOff,
  MoreVertical,
  Loader2,
  Download,
  Star,
  GitFork,
  Github,
  AlertTriangle,
  Edit3,
  Check,
  X,
} from "lucide-react";

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

type RepoCardProps = {
  index: number;
  project: Project;
  isUpdating: boolean;
  isTogglingVisibility: boolean;
  toggleProjectVisibility: (name: string, hidden: boolean) => void;
  updateSingleProject: (name: string) => void;
  // Edit functionality props
  isEditing: boolean;
  editState: {
    three_liner: string;
    technologies: string[];
  };
  isEditUpdating: boolean;
  onStartEdit: (project: Project) => void;
  onCancelEdit: () => void;
  onSaveEdit: (projectName: string) => Promise<boolean>;
  onUpdateEditState: (
    field: "three_liner" | "technologies",
    value: string | string[]
  ) => void;
};
const formatTitle = (title: string) => {
  // Words to keep unchanged if length < 3 or are all uppercase (like AI, ML)
  return title
    .replace(/-/g, " ")
    .split(" ")
    .map((word) => {
      if (word.length < 3 || /^[A-Z]+$/.test(word)) {
        return word;
      }
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
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

export const RepoCard: React.FC<RepoCardProps> = ({
  project,
  index,
  isUpdating,
  isTogglingVisibility,
  toggleProjectVisibility,
  updateSingleProject,
  // Edit functionality
  isEditing,
  editState,
  isEditUpdating,
  onStartEdit,
  onCancelEdit,
  onSaveEdit,
  onUpdateEditState,
}) => {
  const handleSaveEdit = async () => {
    await onSaveEdit(project.name);
    // The parent component will handle reloading projects if successful
  };

  return (
    <Card
      key={index}
      className="hover:shadow-md transition-shadow flex flex-col justify-between w-[30%] min-w-3xs min-h-100"
    >
      <CardHeader className="pb-3 w-full">
        <div className="flex items-start justify-between w-full">
          {/* left side - Fixed truncation issue here */}
          <div className="flex flex-col min-w-0 flex-1 overflow-hidden">
            <CardTitle className="text-lg font-medium line-clamp-1">
              {formatTitle(project.name)}
            </CardTitle>
            {project.hidden_from_search && (
              <Badge variant="outline" className="text-xs mt-1 w-fit">
                <EyeOff className="h-3 w-3 mr-1" />
                Hidden from search
              </Badge>
            )}
          </div>
          <div className="flex gap-1 shrink-0">
            {getReadmeStatus(project) ? (
              <Badge
                variant={getReadmeStatus(project)!.variant}
                className="text-xs p-2"
              >
                {getReadmeStatus(project)!.icon}
              </Badge>
            ) : (
              <Badge variant="outline">{project.language || "Unknown"}</Badge>
            )}
            {/* Dropdown Menu for actions */}
            <DropdownMenu modal={false}>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  disabled={isUpdating || isTogglingVisibility || isEditing}
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => onStartEdit(project)}
                  disabled={isEditing}
                >
                  <Edit3 className="mr-2 h-4 w-4" />
                  Edit content
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() =>
                    toggleProjectVisibility(
                      project.name,
                      project.hidden_from_search || false
                    )
                  }
                  disabled={isTogglingVisibility}
                >
                  {(() => {
                    if (isTogglingVisibility) {
                      return <Loader2 className="mr-2 h-4 w-4 animate-spin" />;
                    } else if (project.hidden_from_search) {
                      return <Eye className="mr-2 h-4 w-4" />;
                    } else {
                      return <EyeOff className="mr-2 h-4 w-4" />;
                    }
                  })()}
                  {project.hidden_from_search
                    ? "Show in search"
                    : "Hide from search"}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => updateSingleProject(project.name)}
                  disabled={isUpdating}
                >
                  {isUpdating ? (
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
        <CardDescription className="line-clamp-7 mt-2">
          {isEditing ? (
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-muted-foreground block mb-1">
                  Description (three-liner):
                </label>
                <Textarea
                  value={editState.three_liner}
                  onChange={(e) =>
                    onUpdateEditState("three_liner", e.target.value)
                  }
                  placeholder="Enter a brief 3-line description..."
                  className="min-h-[80px] resize-none"
                  disabled={isEditUpdating}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleSaveEdit}
                  disabled={isEditUpdating}
                  className="h-7"
                >
                  {isEditUpdating ? (
                    <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                  ) : (
                    <Check className="mr-1 h-3 w-3" />
                  )}
                  Save
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onCancelEdit}
                  disabled={isEditUpdating}
                  className="h-7"
                >
                  <X className="mr-1 h-3 w-3" />
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            project.three_liner ||
            project.description ||
            "No description available"
          )}
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

        {project.technologies && project.technologies.length > 0 && (
          <div className="flex flex-wrap gap-1 items-center">
            {isEditing ? (
              <div className="w-full">
                <label className="text-sm font-medium text-muted-foreground block mb-1">
                  Technologies:
                </label>
                <TagInput
                  tags={editState.technologies}
                  onTagsChange={(tags) =>
                    onUpdateEditState("technologies", tags)
                  }
                  placeholder="Add technology (press Enter or comma to add)"
                  disabled={isEditUpdating}
                />
              </div>
            ) : (
              <>
                {project.technologies.slice(0, 3).map((tech, techIndex) => (
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
                      {project.technologies.slice(3).map((tech, idx) => (
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
              </>
            )}
          </div>
        )}

        <Button
          asChild
          variant="outline"
          size="sm"
          className="w-full bg-transparent text-blue-400 hover:text-blue-500"
        >
          <a href={project.url} target="_blank" rel="noopener noreferrer">
            <Github className="mr-2 h-4 w-4" />
            View on GitHub
          </a>
        </Button>
      </CardContent>
    </Card>
  );
};