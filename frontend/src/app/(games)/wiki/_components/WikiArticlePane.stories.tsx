import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import { WikiArticlePane } from "./WikiArticlePane";

const sampleHtml = `
  <p>Wikipedia-style body with a navigable link:</p>
  <p><a data-wiki-title="Moon" href="#">Jump to Moon article</a></p>
`;

const meta = {
  component: WikiArticlePane,
  args: {
    currentTitle: "Earth",
    articleHtml: sampleHtml,
    navPending: false,
    backEnabled: true,
    onBack: fn(),
    onNavigate: fn(async () => Promise.resolve()),
  },
} satisfies Meta<typeof WikiArticlePane>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const NavPending: Story = {
  args: {
    navPending: true,
  },
};
