import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import type { MatchedProject } from "@/types/project";

interface ProjectSelectionProps {
  matchedProjects: MatchedProject[];
  selectedProjects: MatchedProject[];
  onProjectSelection: (project: MatchedProject, checked: boolean) => void;
}

export function ProjectSelection({
  matchedProjects,
  selectedProjects,
  onProjectSelection,
}: Readonly<ProjectSelectionProps>) {
  if (!matchedProjects.length) return null;

  return (
    <div className="w-full mx-auto">
      <Card className="w-full bg-transparent border-border">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg sm:text-xl">Matched Projects</CardTitle>
          <CardDescription className="text-sm">
            Select up to 4 projects that best match this job (
            {selectedProjects.length}/4 selected)
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-0 px-3">
          <div className="space-y-3">
            {matchedProjects.map((matchedProject, index) => {
              const isSelected = selectedProjects.some(
                (p) => p.project.name === matchedProject.project.name
              );

              return (
                <div
                  key={index}
                  className={`group bg-card relative p-3 sm:p-4 border rounded-lg transition-all duration-200 hover:shadow-md ${
                    isSelected
                      ? "border-primary bg-primary/5 shadow-sm"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={(checked) =>
                        onProjectSelection(matchedProject, !!checked)
                      }
                      disabled={!isSelected && selectedProjects.length >= 4}
                      className="mt-1 flex-shrink-0"
                    />

                    <div className="flex-1 min-w-0">
                      {/* Header with title and score */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2 gap-2">
                        <h4 className="font-medium text-foreground text-sm sm:text-base break-words leading-tight">
                          {matchedProject.project.name}
                        </h4>
                        <Badge
                          variant="secondary"
                          className="self-start sm:self-auto flex-shrink-0 bg-green-100 text-green-800 text-xs whitespace-nowrap"
                        >
                          {(matchedProject.similarity_score * 100).toFixed(1)}% match
                        </Badge>
                      </div>

                      {/* Description */}
                      {matchedProject.project.three_liner && (
                        <p className="text-xs sm:text-sm text-muted-foreground mb-3 leading-relaxed break-words">
                          {matchedProject.project.three_liner}
                        </p>
                      )}

                      {/* Technologies */}
                      {matchedProject.project.technologies?.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {matchedProject.project.technologies
                            .slice(0, 5)
                            .map((tech, techIndex) => (
                              <Badge
                                key={techIndex}
                                variant="outline"
                                className="text-xs break-all"
                              >
                                {tech}
                              </Badge>
                            ))}
                          {matchedProject.project.technologies.length > 5 && (
                            <Badge variant="outline" className="text-xs whitespace-nowrap">
                              +{matchedProject.project.technologies.length - 5} more
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {selectedProjects.length === 0 && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-xs sm:text-sm text-amber-800 break-words">
                Select at least one project to generate your application materials.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default ProjectSelection;