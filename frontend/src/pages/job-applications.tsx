"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, Briefcase, Calendar, FileText, Mail, ExternalLink } from "lucide-react";
import { config } from "@/config";
import { toast } from "sonner";
import type { JobApplication } from "@/types/JobApplication";

export function JobApplications() {
  const [jobApplications, setJobApplications] = useState<JobApplication[]>([]);
  const [filteredApplications, setFilteredApplications] = useState<JobApplication[]>([]);
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

  const getStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "applied":
        return "default";
      case "interview":
        return "secondary";
      case "accepted":
        return "default";
      case "rejected":
        return "destructive";
      default:
        return "outline";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "applied":
        return "text-blue-600";
      case "interview":
        return "text-yellow-600";
      case "accepted":
        return "text-green-600";
      case "rejected":
        return "text-red-600";
      default:
        return "text-gray-600";
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
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Loading job applications...</p>
            </div>
          </div>
        ) : filteredApplications.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">
                {jobApplications.length === 0 ? "No applications yet" : "No matching applications"}
              </h3>
              <p className="text-muted-foreground mb-4">
                {jobApplications.length === 0
                  ? "Start by analyzing a job description and generating an application"
                  : "Try adjusting your search or filter criteria"}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredApplications.map((application) => (
              <Card key={application.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{application.job_title}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <span>{application.company_name}</span>
                        <Badge 
                          variant={getStatusBadgeVariant(application.status)}
                          className={getStatusColor(application.status)}
                        >
                          {application.status}
                        </Badge>
                      </CardDescription>
                    </div>
                    <div className="text-sm text-muted-foreground text-right">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(application.application_date).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {/* Job Description Preview */}
                    {application.job_description && (
                      <div>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {application.job_description.substring(0, 200)}
                          {application.job_description.length > 200 && "..."}
                        </p>
                      </div>
                    )}

                    {/* Download Links */}
                    <div className="flex flex-wrap gap-2">
                      {application.cv_download_url && (
                        <Button
                          variant="outline"
                          size="sm"
                          asChild
                        >
                          <a
                            href={application.cv_download_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2"
                          >
                            <FileText className="h-4 w-4" />
                            CV
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      )}
                      {application.cover_letter_download_url && (
                        <Button
                          variant="outline"
                          size="sm"
                          asChild
                        >
                          <a
                            href={application.cover_letter_download_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2"
                          >
                            <Mail className="h-4 w-4" />
                            Cover Letter
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      )}
                    </div>

                    {/* Notes */}
                    {application.notes && (
                      <div>
                        <p className="text-sm">
                          <span className="font-medium">Notes: </span>
                          {application.notes}
                        </p>
                      </div>
                    )}

                    {/* Matched Projects Count */}
                    {application.matched_projects && application.matched_projects.length > 0 && (
                      <div className="text-sm text-muted-foreground">
                        {application.matched_projects.length} project(s) matched
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}