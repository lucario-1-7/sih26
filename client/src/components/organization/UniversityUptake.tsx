import type { OrganizationSummary } from "@/types/api";

/** "Which university has taken up this project" - value comes straight from
 * the project API response's `university` field (server/app/services/
 * project_service.py resolves it; null until the project is accepted, never
 * a placeholder name). Reused everywhere a project is shown in enough
 * detail to name its university - matches the existing dt/dd label pattern
 * used across project/challenge detail pages. */
export function UniversityUptake({ university }: { university: OrganizationSummary | null }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase text-slate-400">Taken up by</dt>
      <dd className="mt-1 text-sm text-slate-700">
        {university ? university.name : "Not yet taken up by a university"}
      </dd>
    </div>
  );
}

/** Compact inline variant for list rows (cards/tables), where a full dt/dd
 * pair would be too tall. */
export function UniversityUptakeInline({ university }: { university: OrganizationSummary | null }) {
  return (
    <span className="text-xs text-slate-500">
      {university ? `Taken up by ${university.name}` : "Not yet taken up"}
    </span>
  );
}
