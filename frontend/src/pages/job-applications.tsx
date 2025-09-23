"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Filter, Briefcase } from "lucide-react";
import { config } from "@/config";
import { toast } from "sonner";
import type { JobApplication } from "@/types/JobApplication";
import { JobApplicationsList } from "@/components/job-applications/job-application-list";

export function JobApplications() {
  const [jobApplications, setJobApplications] = useState<JobApplication[]>([]);
  const [filteredApplications, setFilteredApplications] = useState<
    JobApplication[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Load job applications on component mount
  useEffect(() => {
    loadJobApplications();
  }, []);

  // Filter applications based on search term and status
  useEffect(() => {
    let filtered = jobApplications;

    // Filter by search term (job title or company name)
    if (searchTerm) {
      filtered = filtered.filter(
        (app) =>
          app.job_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          app.company_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== "all") {
      filtered = filtered.filter((app) => app.status === statusFilter);
    }

    setFilteredApplications(filtered);
  }, [jobApplications, searchTerm, statusFilter]);

  const loadJobApplications = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.jobApplications}/`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const applications = await response.json();
      setJobApplications(applications);
    } catch (error) {
      console.error("Error loading job applications:", error);
      toast.error("Failed to load job applications");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-heading text-2xl font-bold text-foreground">
              Job Applications
            </h1>
            <p className="text-muted-foreground mt-1">
              Track and manage all your job applications
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={loadJobApplications}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <Briefcase className="h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="border-b border-border p-6 space-y-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <Label htmlFor="search">Search Applications</Label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                id="search"
                placeholder="Search by job title or company..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="w-full sm:w-48">
            <Label htmlFor="status-filter">Filter by Status</Label>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="All statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="applied">Applied</SelectItem>
                <SelectItem value="interview">Interview</SelectItem>
                <SelectItem value="accepted">Accepted</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Summary */}
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span>Total: {jobApplications.length}</span>
          <span>Filtered: {filteredApplications.length}</span>
        </div>
      </div>

      {/* Applications List */}
      <div className="flex-1 p-6 overflow-auto">
        <JobApplicationsList
          jobApplications={filteredApplications}
          totalCount={jobApplications.length}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
