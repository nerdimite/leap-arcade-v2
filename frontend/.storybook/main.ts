import type { StorybookConfig } from "@storybook/nextjs-vite"

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  addons: [
    "@storybook/addon-a11y",
    "@storybook/addon-docs",
    "@chromatic-com/storybook",
    "@storybook/addon-vitest",
  ],
  framework: "@storybook/nextjs-vite",
  staticDirs: ["../public"],
}

export default config
