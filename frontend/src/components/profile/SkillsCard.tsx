import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Code, Plus, Trash2, X } from "lucide-react";
import type { PersonalInfo } from "@/types/PersonalInfo";

interface SkillsCardProps {
  skills: { [category: string]: string[] };
  updatePersonalInfo: (field: keyof PersonalInfo, value: any) => void;
}

export function SkillsCard({
  skills,
  updatePersonalInfo,
}: Readonly<SkillsCardProps>) {
  const [newCategoryName, setNewCategoryName] = useState("");
  const [isAddingCategory, setIsAddingCategory] = useState(false);
  const [newSkills, setNewSkills] = useState<{ [category: string]: string }>(
    {}
  );

  const handleAddCategory = () => {
    if (newCategoryName.trim() && !skills[newCategoryName.trim()]) {
      updatePersonalInfo("skills", {
        ...skills,
        [newCategoryName.trim()]: [],
      });
      setNewCategoryName("");
      setIsAddingCategory(false);
    }
  };

  const handleCancelAddCategory = () => {
    setNewCategoryName("");
    setIsAddingCategory(false);
  };

  const removeSkillCategory = (category: string) => {
    const newSkills = { ...skills };
    delete newSkills[category];
    updatePersonalInfo("skills", newSkills);
  };

  const handleAddSkill = (category: string) => {
    const skillsToAdd = newSkills[category]
      ?.trim()
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s && s.length > 0);

    if (!skillsToAdd || skillsToAdd.length === 0) return;

    const updatedSkills = { ...skills };
    const existingSkills = updatedSkills[category] || [];

    // Filter out duplicates and add all valid skills at once
    const newValidSkills = skillsToAdd.filter(
      (skill) => !existingSkills.includes(skill)
    );

    if (newValidSkills.length > 0) {
      updatedSkills[category] = [...existingSkills, ...newValidSkills];
      updatePersonalInfo("skills", updatedSkills);
    }

    // Clear the input for this category
    setNewSkills((prev) => ({ ...prev, [category]: "" }));
  };

  const handleSkillInputKeyPress = (
    e: React.KeyboardEvent,
    category: string
  ) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddSkill(category);
    }
  };

  const removeSkillFromCategory = (category: string, skillIndex: number) => {
    const updatedSkills = { ...skills };
    updatedSkills[category] =
      updatedSkills[category]?.filter((_, index) => index !== skillIndex) || [];
    updatePersonalInfo("skills", updatedSkills);
  };

  const updateNewSkillInput = (category: string, value: string) => {
    setNewSkills((prev) => ({ ...prev, [category]: value }));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Code className="h-5 w-5" />
          Skills
        </CardTitle>
        <CardDescription>
          Organize your skills by categories (e.g., Programming Languages,
          Frameworks, Tools)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {Object.entries(skills).map(([category, categorySkills]) => (
          <div key={category} className="border rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">{category}</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeSkillCategory(category)}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-3">
              {/* Existing skills */}
              <div className="flex flex-wrap gap-2">
                {categorySkills.map((skill, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    {skill}
                    <button
                      onClick={() => removeSkillFromCategory(category, index)}
                      className="ml-1 hover:bg-destructive/20 rounded-full p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>

              {/* Add new skill input */}
              <div className="flex gap-2">
                <Input
                  placeholder={`Add skill to ${category}...`}
                  value={newSkills[category] || ""}
                  onChange={(e) =>
                    updateNewSkillInput(category, e.target.value)
                  }
                  onKeyUp={(e) => handleSkillInputKeyPress(e, category)}
                  className="flex-1"
                />
                <Button
                  size="sm"
                  onClick={() => handleAddSkill(category)}
                  disabled={!newSkills[category]?.trim()}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        ))}

        {/* Add new category section */}
        {isAddingCategory ? (
          <div className="border rounded-lg p-4 space-y-3 bg-muted/20">
            <h4 className="font-medium text-sm text-muted-foreground">
              New Category
            </h4>
            <div className="flex gap-2">
              <Input
                placeholder="Enter category name..."
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                onKeyUp={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddCategory();
                  }
                  if (e.key === "Escape") {
                    handleCancelAddCategory();
                  }
                }}
                autoFocus
                className="flex-1"
              />
              <Button
                size="sm"
                onClick={handleAddCategory}
                disabled={
                  !newCategoryName.trim() || !!skills[newCategoryName.trim()]
                }
              >
                Add
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleCancelAddCategory}
              >
                Cancel
              </Button>
            </div>
            {newCategoryName.trim() && skills[newCategoryName.trim()] && (
              <p className="text-sm text-destructive">
                Category already exists
              </p>
            )}
          </div>
        ) : (
          <Button
            variant="outline"
            onClick={() => setIsAddingCategory(true)}
            className="w-full"
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Skill Category
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
