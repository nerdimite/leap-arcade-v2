import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { WikiClickBreadcrumb } from "./WikiClickBreadcrumb";

const meta = {
  component: WikiClickBreadcrumb,
  args: {
    pathRoot: "Earth",
    clickPath: ["Ocean", "Atlantic", "Caribbean Sea"],
  },
} satisfies Meta<typeof WikiClickBreadcrumb>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
