"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { FileText } from "lucide-react";
import { toast } from "sonner";
import { config } from "@/config";
import { BasicInfoCard } from "@/components/profile/BasicInfoCard";
import { SkillsCard } from "@/components/profile/SkillsCard";
import { ExperienceCard } from "@/components/profile/ExperienceCard";
import { EducationCard } from "@/components/profile/EducationCard";
import { InstructionsCard } from "@/components/profile/InstructionsCard";
import type { PersonalInfo } from "@/types/PersonalInfo";
import LocalHeader from "@/components/header";

export function PersonalInfo() {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(
    localStorage.getItem("user_id") ?? null
  );
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo>({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    postal_code: "",
    title: "",
    summary: "",
    skills: {},
    experience: [],
    education: [],
  });

  const updatePersonalInfo = (field: keyof PersonalInfo, value: any) => {
    setPersonalInfo((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setIsUpdating(true);
    try {
      let response;
      if (userId) {
        // Update existing
        response = await fetch(
          `${config.api.baseUrl}${config.api.endpoints.personalInfo}/${userId}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(personalInfo),
          }
        );
      } else {
        // Create new
        response = await fetch(
          `${config.api.baseUrl}${config.api.endpoints.personalInfo}/`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(personalInfo),
          }
        );
      }

      if (!response.ok) throw new Error("Failed to save profile");

      const result = await response.json();

      if (result?.id) {
        localStorage.setItem("user_id", result.id);
        setUserId(result.id);
      }

      toast.success("Profile Updated Successfully");
    } catch (error) {
      toast("Failed to update profile", {
        description: error instanceof Error ? `: ${error.message}` : "",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const loadProfile = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.personalInfo}/${userId}`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPersonalInfo({
          first_name: data.first_name || "",
          last_name: data.last_name || "",
          email: data.email || "",
          phone: data.phone || "",
          address: data.address || "",
          city: data.city || "",
          postal_code: data.postal_code || "",
          title: data.title || "",
          summary: data.summary || "",
          skills: data.skills || {},
          experience: data.experience || [],
          education: data.education || [],
        });
      }
    } catch (error) {
      console.error("Failed to load personal information:", error);
      toast.error("Failed to load personal information");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsUpdating(true);
    await loadProfile();
    setIsUpdating(false);
  };

  useEffect(() => {
    if (userId) {
      loadProfile();
    }
  }, [userId]);

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-primary"></div>
        <span className="ml-4 text-lg text-muted-foreground">Loading...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-border p-6">
        <LocalHeader
          title="Personal Information"
          description="
            Configure your personal information for CV generation"
        />

        <div className="flex gap-4 pt-4">
          <Button
            className="cursor-pointer"
            onClick={handleSubmit}
            disabled={isUpdating}
          >
            <FileText className="mr-2 h-4 w-4" />
            {isUpdating ? "Saving..." : "Save Profile"}
          </Button>
          <Button
            className="cursor-pointer"
            variant="outline"
            onClick={handleRefresh}
            disabled={isUpdating}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <BasicInfoCard
          personalInfo={personalInfo}
          updatePersonalInfo={updatePersonalInfo}
        />

        <SkillsCard
          skills={personalInfo.skills || {}}
          updatePersonalInfo={updatePersonalInfo}
        />

        <ExperienceCard
          experience={personalInfo.experience || []}
          updatePersonalInfo={updatePersonalInfo}
        />

        <EducationCard
          education={personalInfo.education || []}
          updatePersonalInfo={updatePersonalInfo}
        />

        <InstructionsCard />
      </div>
    </div>
  );
}
