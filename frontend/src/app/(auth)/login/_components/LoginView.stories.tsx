import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import { LoginView } from "./LoginView";

const meta = {
  component: LoginView,
  args: {
    corpId: "",
    eventCode: "",
    isPending: false,
    showInvalidCreds: false,
    onCorpIdChange: fn(),
    onEventCodeChange: fn(),
    onSubmit: fn(),
  },
} satisfies Meta<typeof LoginView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Idle: Story = {
  args: {
    corpId: "",
    eventCode: "",
    isPending: false,
    showInvalidCreds: false,
  },
};

export const Pending: Story = {
  args: {
    corpId: "alice",
    eventCode: "event-99",
    isPending: true,
    showInvalidCreds: false,
  },
};

export const InvalidCredentials: Story = {
  args: {
    corpId: "alice",
    eventCode: "bad-code",
    isPending: false,
    showInvalidCreds: true,
  },
};
