import { Badge } from "@/components/ui/Badge";
import type { Domain } from "@/types/api";

const LABEL: Record<Domain, string> = {
  citizen: "Citizen",
  government: "Government",
  university: "University",
  industry: "Industry",
  superadmin: "Superadmin",
};

export function DomainBadge({ domain }: { domain: Domain }) {
  return <Badge tone="neutral">{LABEL[domain] ?? domain}</Badge>;
}
