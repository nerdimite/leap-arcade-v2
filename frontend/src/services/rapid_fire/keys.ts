export const rapidFireQueryKeys = {
  all: ["rapid-fire"] as const,
  play: () => [...rapidFireQueryKeys.all, "play"] as const,
}
