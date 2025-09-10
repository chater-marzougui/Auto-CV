"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { FileText, User, Mail, Phone, MapPin, Briefcase } from "lucide-react"

interface PersonalInfo {
  first_name: string
  last_name: string
  email: string
  phone: string
  address: string
  city: string
  postal_code: string
  title: string
  summary: string
}

export function PersonalInfo() {
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
  })

  const updatePersonalInfo = (field: keyof PersonalInfo, value: string) => {
    setPersonalInfo((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border p-6">
        <h1 className="font-heading text-2xl font-bold text-foreground">CV Generator</h1>
        <p className="text-muted-foreground mt-1">Configure your personal information for CV generation</p>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Personal Information
            </CardTitle>
            <CardDescription>This information will be used in your generated CVs and cover letters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Name */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  value={personalInfo.first_name}
                  onChange={(e) => updatePersonalInfo("first_name", e.target.value)}
                  placeholder="John"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={personalInfo.last_name}
                  onChange={(e) => updatePersonalInfo("last_name", e.target.value)}
                  placeholder="Doe"
                />
              </div>
            </div>

            {/* Contact */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={personalInfo.email}
                  onChange={(e) => updatePersonalInfo("email", e.target.value)}
                  placeholder="john.doe@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone" className="flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Phone
                </Label>
                <Input
                  id="phone"
                  value={personalInfo.phone}
                  onChange={(e) => updatePersonalInfo("phone", e.target.value)}
                  placeholder="+1-555-0123"
                />
              </div>
            </div>

            {/* Address */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="address" className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Address
                </Label>
                <Input
                  id="address"
                  value={personalInfo.address}
                  onChange={(e) => updatePersonalInfo("address", e.target.value)}
                  placeholder="123 Tech Street"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={personalInfo.city}
                    onChange={(e) => updatePersonalInfo("city", e.target.value)}
                    placeholder="San Francisco"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="postal_code">Postal Code</Label>
                  <Input
                    id="postal_code"
                    value={personalInfo.postal_code}
                    onChange={(e) => updatePersonalInfo("postal_code", e.target.value)}
                    placeholder="94105"
                  />
                </div>
              </div>
            </div>

            {/* Professional Info */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title" className="flex items-center gap-2">
                  <Briefcase className="h-4 w-4" />
                  Professional Title
                </Label>
                <Input
                  id="title"
                  value={personalInfo.title}
                  onChange={(e) => updatePersonalInfo("title", e.target.value)}
                  placeholder="Software Developer"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="summary">Professional Summary</Label>
                <Textarea
                  id="summary"
                  value={personalInfo.summary}
                  onChange={(e) => updatePersonalInfo("summary", e.target.value)}
                  placeholder="Experienced software developer with expertise in modern web technologies..."
                  className="min-h-[100px]"
                />
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <Button className="flex-1">
                <FileText className="mr-2 h-4 w-4" />
                Save Profile
              </Button>
              <Button variant="outline">Load Saved Profile</Button>
            </div>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>How to Use</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>1. Fill in your personal information above</p>
            <p>2. Go to the Job Analysis tab and paste a job description</p>
            <p>3. Click "Analyze Job" to see matching projects</p>
            <p>4. Click "Generate Application" to create your tailored CV and cover letter</p>
            <p>5. Download the generated documents from the Job Analysis page</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
