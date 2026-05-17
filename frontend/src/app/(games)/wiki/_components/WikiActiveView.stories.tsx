import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import type { WikiActivePuzzle } from "@/services/wiki/schema";

import { WikiActiveView } from "./WikiActiveView";

const sampleCurrent: WikiActivePuzzle = {
  game_session_id: "gs-story",
  attempt_id: "attempt-1",
  round_id: "round-1",
  puzzle_index: 3,
  puzzle_count: 5,
  clue: "Navigate from Earth to the Moon using in-article links.",
  current_title: "Earth",
  time_limit_ms: 180_000,
  time_remaining_ms: 45_000,
  steps_taken: 4,
  click_path: ["Solar System"],
  article_html: `
    <p>Earth is the third planet from the Sun.</p>
    <p><a data-wiki-title="Moon" href="#">Moon</a></p>
  `,
  back_enabled: true,
};

const meta = {
  component: WikiActiveView,
  args: {
    current: sampleCurrent,
    pathRoot: "Earth",
    timerRemainingMs: 45_000,
    completedCount: 2,
    totalScore: 420,
    navPending: false,
    onNavigate: fn(async () => Promise.resolve()),
    onBack: fn(),
  },
} satisfies Meta<typeof WikiActiveView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
