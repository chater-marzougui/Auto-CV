import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { User, Mail, Phone, MapPin, Briefcase } from "lucide-react";
import type { PersonalInfo } from "@/types/PersonalInfo";

interface BasicInfoCardProps {
  personalInfo: PersonalInfo;
  updatePersonalInfo: (field: keyof PersonalInfo, value: any) => void;
}

export function BasicInfoCard({ personalInfo, updatePersonalInfo }: Readonly<BasicInfoCardProps>) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          Personal Information
        </CardTitle>
        <CardDescription>
          Basic contact information and professional details
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Name */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="first_name">First Name *</Label>
            <Input
              id="first_name"
              value={personalInfo.first_name}
              onChange={(e) =>
                updatePersonalInfo("first_name", e.target.value)
              }
              placeholder="John"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="last_name">Last Name *</Label>
            <Input
              id="last_name"
              value={personalInfo.last_name}
              onChange={(e) =>
                updatePersonalInfo("last_name", e.target.value)
              }
              placeholder="Doe"
              required
            />
          </div>
        </div>

        {/* Contact */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="flex items-center gap-2">
              <Mail className="h-4 w-4" />
              Email *
            </Label>
            <Input
              id="email"
              type="email"
              value={personalInfo.email}
              onChange={(e) => updatePersonalInfo("email", e.target.value)}
              placeholder="john.doe@example.com"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone" className="flex items-center gap-2">
              <Phone className="h-4 w-4" />
              Phone
            </Label>
            <Input
              id="phone"
              value={personalInfo.phone || ""}
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
              value={personalInfo.address || ""}
              onChange={(e) =>
                updatePersonalInfo("address", e.target.value)
              }
              placeholder="123 Tech Street"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="city">City</Label>
              <Input
                id="city"
                value={personalInfo.city || ""}
                onChange={(e) => updatePersonalInfo("city", e.target.value)}
                placeholder="San Francisco"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="postal_code">Postal Code</Label>
              <Input
                id="postal_code"
                value={personalInfo.postal_code || ""}
                onChange={(e) =>
                  updatePersonalInfo("postal_code", e.target.value)
                }
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
              value={personalInfo.title || ""}
              onChange={(e) => updatePersonalInfo("title", e.target.value)}
              placeholder="Software Developer"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="summary">Professional Summary</Label>
            <Textarea
              id="summary"
              value={personalInfo.summary || ""}
              onChange={(e) =>
                updatePersonalInfo("summary", e.target.value)
              }
              placeholder="Experienced software developer with expertise in modern web technologies..."
              className="min-h-[100px]"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}