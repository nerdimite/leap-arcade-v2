/** Read-only clickable-path breadcrumb for the wiki run. */

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
  return (
    <div className="min-w-0 text-xs text-muted-foreground" data-testid="wiki-breadcrumb">
      <span className="font-medium text-foreground">Path</span>
      <span className="mx-1.5">·</span>
      <div className="max-w-full overflow-x-auto overscroll-x-contain [-ms-overflow-style:none] [scrollbar-width:thin] [&::-webkit-scrollbar]:h-1">
        <span className="inline-flex w-max min-w-0 flex-nowrap items-baseline gap-x-1 whitespace-nowrap">
          {crumbs.map((c, i) => (
            <span key={crumbs.slice(0, i + 1).join("\u2192")} className="inline-flex items-baseline gap-x-1">
              {i > 0 ? <span className="text-muted-foreground">→</span> : null}
              <span className="max-w-[14rem] truncate font-medium text-foreground sm:max-w-[18rem]" title={c}>
                {c}
              </span>
            </span>
          ))}
        </span>
      </div>
    </div>
  );
}
