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

// Project Selection Component
export function ProjectSelection({
  matchedProjects,
  selectedProjects,
  onProjectSelection,
}: Readonly<ProjectSelectionProps>) {
  if (!matchedProjects.length) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matched Projects</CardTitle>
        <CardDescription>
          Select up to 4 projects that best match this job (
          {selectedProjects.length}/4 selected)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {matchedProjects.map((matchedProject, index) => {
            const isSelected = selectedProjects.some(
              (p) => p.project.name === matchedProject.project.name
            );

            return (
              <div
                key={index}
                className={`group relative p-4 border rounded-lg transition-all duration-200 hover:shadow-md ${
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
                    className="mt-1"
                  />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-foreground truncate">
                        {matchedProject.project.name}
                      </h4>
                      <Badge
                        variant="secondary"
                        className="ml-2 flex-shrink-0 bg-green-100 text-green-800"
                      >
                        {(matchedProject.similarity_score * 100).toFixed(1)}%
                        match
                      </Badge>
                    </div>

                    {matchedProject.project.three_liner && (
                      <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
                        {matchedProject.project.three_liner}
                      </p>
                    )}

                    {matchedProject.project.technologies?.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {matchedProject.project.technologies
                          .slice(0, 5)
                          .map((tech, techIndex) => (
                            <Badge
                              key={techIndex}
                              variant="outline"
                              className="text-xs"
                            >
                              {tech}
                            </Badge>
                          ))}
                        {matchedProject.project.technologies.length > 5 && (
                          <Badge variant="outline" className="text-xs">
                            +{matchedProject.project.technologies.length - 5}{" "}
                            more
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
            <p className="text-sm text-amber-800">
              Select at least one project to generate your application
              materials.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
