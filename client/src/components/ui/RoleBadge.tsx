import { Badge } from "@/components/ui/Badge";
import type { Role } from "@/types/api";

const LABEL: Record<Role, string> = {
  citizen: "Citizen",
  validator: "Validator",
  field_assistant: "Field Assistant",
  coordinator: "Coordinator",
  faculty: "Faculty",
  industry: "Industry",
  superadmin: "Superadmin",
};

export function RoleBadge({ role }: { role: Role }) {
  return <Badge tone="info">{LABEL[role] ?? role}</Badge>;
}
