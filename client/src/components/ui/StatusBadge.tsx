import { Badge } from "@/components/ui/Badge";

const STATUS_TONE: Record<string, "neutral" | "success" | "warning" | "danger" | "info"> = {
  proposed: "info",
  accepted: "info",
  active: "success",
  on_hold: "warning",
  completed: "success",
  cancelled: "danger",
  pending: "neutral",
  in_progress: "info",
  blocked: "danger",
  submitted: "info",
  verified: "success",
  rejected: "danger",
  draft: "neutral",
  published: "success",
};

function humanize(status: string): string {
  return status
    .split("_")
    .map((word) => word[0]?.toUpperCase() + word.slice(1))
    .join(" ");
}

export function StatusBadge({ status }: { status: string }) {
  return <Badge tone={STATUS_TONE[status] ?? "neutral"}>{humanize(status)}</Badge>;
}
