import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { GraduationCap, Plus, Trash2 } from "lucide-react";
import type { PersonalInfo, Education } from "@/types/PersonalInfo";

interface EducationCardProps {
  education: Education[];
  updatePersonalInfo: (field: keyof PersonalInfo, value: any) => void;
}

export function EducationCard({ education, updatePersonalInfo }: Readonly<EducationCardProps>) {
  const addEducation = () => {
    const newEducation: Education = {
      institution: "",
      degree: "",
      field: "",
      start_date: "",
      end_date: "",
      description: ""
    };
    updatePersonalInfo("education", [...education, newEducation]);
  };

  const updateEducation = (index: number, field: keyof Education, value: string) => {
    const newEducation = [...education];
    newEducation[index] = { ...newEducation[index], [field]: value };
    updatePersonalInfo("education", newEducation);
  };

  const removeEducation = (index: number) => {
    const newEducation = education.filter((_, i) => i !== index);
    updatePersonalInfo("education", newEducation);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <GraduationCap className="h-5 w-5" />
          Education
        </CardTitle>
        <CardDescription>
          Add your educational background
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {education.map((edu, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Education {index + 1}</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeEducation(index)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Institution</Label>
                <Input
                  value={edu.institution}
                  onChange={(e) => updateEducation(index, "institution", e.target.value)}
                  placeholder="University Name"
                />
              </div>
              <div className="space-y-2">
                <Label>Degree</Label>
                <Input
                  value={edu.degree}
                  onChange={(e) => updateEducation(index, "degree", e.target.value)}
                  placeholder="Bachelor's, Master's, PhD, etc."
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Field of Study</Label>
              <Input
                value={edu.field}
                onChange={(e) => updateEducation(index, "field", e.target.value)}
                placeholder="Computer Science, Engineering, etc."
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Start Date</Label>
                <Input
                  type="month"
                  value={edu.start_date}
                  onChange={(e) => updateEducation(index, "start_date", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>End Date</Label>
                <Input
                  type="month"
                  value={edu.end_date}
                  onChange={(e) => updateEducation(index, "end_date", e.target.value)}
                  placeholder="Leave empty if ongoing"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={edu.description}
                onChange={(e) => updateEducation(index, "description", e.target.value)}
                placeholder="Notable achievements, GPA, relevant coursework..."
                className="min-h-[60px]"
              />
            </div>
          </div>
        ))}
        <Button
          variant="outline"
          onClick={addEducation}
          className="w-full"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Education
        </Button>
      </CardContent>
    </Card>
  );
}