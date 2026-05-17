export const wikiQueryKeys = {
  all: ["wiki"] as const,
  play: () => [...wikiQueryKeys.all, "play"] as const,
};
