import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import type { GameTileProps } from "./GameTile";
import { LobbyView } from "./LobbyView";
import type { MiniLeaderboardRow } from "./MiniLeaderboard";
import { MiniLeaderboard } from "./MiniLeaderboard";

const wikiTile = (
  props: Partial<GameTileProps> & Pick<GameTileProps, "badge" | "locked">,
): GameTileProps => ({
  name: "Wikipedia Speed Run",
  description: "Navigate Wikipedia by links only — reach the target page as fast as you can.",
  maxPoints: 100,
  href: "/wiki",
  ...props,
});

const rapidTile = (
  props: Partial<GameTileProps> & Pick<GameTileProps, "badge" | "locked">,
): GameTileProps => ({
  name: "Rapid Fire Quiz",
  description: "Fast multiple-choice questions with a countdown — answer quickly for speed bonuses.",
  maxPoints: 100,
  href: "/rapid-fire",
  ...props,
});

const pictureTile = (
  props: Partial<GameTileProps> & Pick<GameTileProps, "badge" | "locked">,
): GameTileProps => ({
  name: "Picture Illustration",
  description: "Images reveal a concept step by step — type the answer early for more points.",
  maxPoints: 100,
  href: "/picture",
  ...props,
});

const fourPicsTile = (
  props: Partial<GameTileProps> & Pick<GameTileProps, "badge" | "locked">,
): GameTileProps => ({
  name: "Four Pics, One Lie",
  description: "Spot the image that does not belong with the other three.",
  maxPoints: 100,
  href: "/four-pics",
  ...props,
});

const crosswordTile = (
  props: Partial<GameTileProps> & Pick<GameTileProps, "badge" | "locked">,
): GameTileProps => ({
  name: "Crossword Puzzle",
  description: "Classic across and down clues — finish fast for a time bonus.",
  maxPoints: 100,
  href: "/crossword",
  ...props,
});

const storySidebarEntries: MiniLeaderboardRow[] = [
  { rank: 1, corp_id: "c1", display_name: "Player One", total_score: 400, games_completed: 5 },
  { rank: 2, corp_id: "c2", display_name: "Player Two", total_score: 360, games_completed: 4 },
];

const meta = {
  component: LobbyView,
} satisfies Meta<typeof LobbyView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const AllAvailable: Story = {
  args: {
    tiles: [
      wikiTile({ badge: "Not started", locked: false }),
      rapidTile({ badge: "Not started", locked: false }),
      pictureTile({ badge: "Not started", locked: false }),
      fourPicsTile({ badge: "Not started", locked: false }),
      crosswordTile({ badge: "Not started", locked: false }),
    ],
    sidebar: (
      <MiniLeaderboard entries={storySidebarEntries} currentCorpId={null} />
    ),
  },
};

export const MixedStatuses: Story = {
  args: {
    tiles: [
      wikiTile({ badge: "In progress", score: 40, locked: false }),
      rapidTile({ badge: "Completed", score: 95, locked: true }),
      pictureTile({ badge: "Not started", locked: false }),
      fourPicsTile({ badge: "Abandoned", score: 12, locked: true }),
      crosswordTile({ badge: "Not started", locked: false }),
    ],
    sidebar: <MiniLeaderboard entries={storySidebarEntries} currentCorpId="c2" />,
  },
};

export const AllLocked: Story = {
  args: {
    tiles: [
      wikiTile({ badge: "Completed", score: 300, locked: true }),
      rapidTile({ badge: "Completed", score: 280, locked: true }),
      pictureTile({ badge: "Completed", score: 260, locked: true }),
      fourPicsTile({ badge: "Abandoned", score: 40, locked: true }),
      crosswordTile({ badge: "Completed", score: 310, locked: true }),
    ],
    sidebar: <div className="text-muted-foreground text-sm">Sidebar placeholder</div>,
  },
};

export { AllAvailable as Default };
