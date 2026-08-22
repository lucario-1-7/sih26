"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import type { NavItem } from "@/lib/rbac/config";

export function Sidebar({ items, sectionLabel }: { items: NavItem[]; sectionLabel: string }) {
  const pathname = usePathname();

  return (
    <nav aria-label={sectionLabel} className="w-56 shrink-0 border-r border-slate-200 bg-white p-4">
      <p className="mb-3 px-2 text-xs font-semibold uppercase tracking-wide text-slate-400">{sectionLabel}</p>
      <ul className="flex flex-col gap-1">
        {items.map((item) => {
          const isActive = pathname === item.href.split("?")[0];
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={`block rounded-md px-2 py-2 text-sm font-medium ${
                  isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
