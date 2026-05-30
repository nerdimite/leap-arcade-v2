/** Read-only clickable-path breadcrumb for the wiki run, styled as cabinet pills. */

import { ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";

export type WikiClickBreadcrumbProps = {
  pathRoot: string;
  clickPath: string[];
};

export function WikiClickBreadcrumb(props: WikiClickBreadcrumbProps) {
  const { pathRoot, clickPath } = props;
  const chain = [pathRoot, ...clickPath];
  const crumbs = chain.filter((c, i) => i === 0 || c !== chain[i - 1]);
  if (crumbs.length === 0) {
    return null;
  }
  const lastIndex = crumbs.length - 1;
  return (
    <div
      className="flex min-w-0 items-center gap-2 text-[12px] text-ink-faint"
      data-testid="wiki-breadcrumb"
    >
      <span className="shrink-0 text-[9px] uppercase tracking-[1px]">Path</span>
      <div className="max-w-full overflow-x-auto overscroll-x-contain [-ms-overflow-style:none] [scrollbar-width:thin] [&::-webkit-scrollbar]:h-1">
        <div className="flex w-max items-center gap-2 whitespace-nowrap">
          {crumbs.map((c, i) => {
            const current = i === lastIndex;
            return (
              <span
                key={crumbs.slice(0, i + 1).join("\u203a")}
                className="flex items-center gap-2"
              >
                {i > 0 ? <ChevronRight aria-hidden className="size-3 shrink-0" /> : null}
                <span
                  title={c}
                  className={cn(
                    "max-w-[14rem] truncate rounded-full border-[1.5px] border-line bg-panel px-2.5 py-1 font-medium text-ink-dim sm:max-w-[18rem]",
                    current &&
                      "border-[var(--accent,var(--wiki))] text-[var(--accent,var(--wiki))]",
                  )}
                >
                  {c}
                </span>
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}
