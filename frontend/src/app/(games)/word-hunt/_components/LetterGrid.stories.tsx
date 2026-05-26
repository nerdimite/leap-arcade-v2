import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import { LetterGrid } from "./LetterGrid";
import {
  allFoundClues,
  devopsTrace,
  midDragPreview,
  sampleGrid,
  springTrace,
} from "../_lib/storyFixtures";

const meta = {
  component: LetterGrid,
  args: {
    rows: sampleGrid.length,
    cols: sampleGrid[0]?.length ?? 0,
    grid: sampleGrid,
    highlighted: [],
    preview: null,
    missFlash: null,
    landAnimation: null,
    onDragStart: fn(),
    onDragMove: fn(),
    onDragEnd: fn(),
  },
} satisfies Meta<typeof LetterGrid>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Empty: Story = {};

export const InProgress: Story = {
  args: {
    highlighted: [devopsTrace, springTrace],
  },
};

export const AllFound: Story = {
  args: {
    highlighted: allFoundClues
      .map((clue) => clue.coordinates)
      .filter((coordinates): coordinates is NonNullable<typeof coordinates> => coordinates != null),
  },
};

export const MidDrag: Story = {
  args: {
    highlighted: [devopsTrace],
    preview: midDragPreview,
  },
};

export { Empty as Default };
