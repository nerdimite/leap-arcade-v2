export const pinpointQueryKeys = {
  all: ["pinpoint"] as const,
  play: () => [...pinpointQueryKeys.all, "play"] as const,
};
