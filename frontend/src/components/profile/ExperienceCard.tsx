import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Briefcase, Plus, Trash2 } from "lucide-react";
import type { PersonalInfo, Experience } from "@/types/PersonalInfo";

interface ExperienceCardProps {
  experience: Experience[];
  updatePersonalInfo: (field: keyof PersonalInfo, value: any) => void;
}

export function ExperienceCard({ experience, updatePersonalInfo }: Readonly<ExperienceCardProps>) {
  const addExperience = () => {
    const newExperience: Experience = {
      company: "",
      position: "",
      start_date: "",
      end_date: "",
      description: ""
    };
    updatePersonalInfo("experience", [...experience, newExperience]);
  };

  const updateExperience = (index: number, field: keyof Experience, value: string) => {
    const newExperience = [...experience];
    newExperience[index] = { ...newExperience[index], [field]: value };
    updatePersonalInfo("experience", newExperience);
  };

  const removeExperience = (index: number) => {
    const newExperience = experience.filter((_, i) => i !== index);
    updatePersonalInfo("experience", newExperience);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Briefcase className="h-5 w-5" />
          Work Experience
        </CardTitle>
        <CardDescription>
          Add your professional work experience
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {experience.map((exp, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Experience {index + 1}</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeExperience(index)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Company</Label>
                <Input
                  value={exp.company}
                  onChange={(e) => updateExperience(index, "company", e.target.value)}
                  placeholder="Company Name"
                />
              </div>
              <div className="space-y-2">
                <Label>Position</Label>
                <Input
                  value={exp.position}
                  onChange={(e) => updateExperience(index, "position", e.target.value)}
                  placeholder="Job Title"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Start Date</Label>
                <Input
                  type="month"
                  value={exp.start_date}
                  onChange={(e) => updateExperience(index, "start_date", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>End Date</Label>
                <Input
                  type="month"
                  value={exp.end_date}
                  onChange={(e) => updateExperience(index, "end_date", e.target.value)}
                  placeholder="Leave empty if current"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={exp.description}
                onChange={(e) => updateExperience(index, "description", e.target.value)}
                placeholder="Describe your responsibilities and achievements..."
                className="min-h-[80px]"
              />
            </div>
          </div>
        ))}
        <Button
          variant="outline"
          onClick={addExperience}
          className="w-full"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Experience
        </Button>
      </CardContent>
    </Card>
  );
}