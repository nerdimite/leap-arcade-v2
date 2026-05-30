export const wordHuntQueryKeys = {
  all: ["word_hunt"] as const,
  play: () => [...wordHuntQueryKeys.all, "play"] as const,
}
