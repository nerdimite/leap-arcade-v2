// @vitest-environment happy-dom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { PinpointResultOverlay } from "./PinpointResultOverlay";

describe("PinpointResultOverlay", () => {
  afterEach(() => {
    cleanup();
  });

  it("shows green solved copy with base and time bonus breakdown", () => {
    render(<PinpointResultOverlay kind="solved" baseScore={400} timeBonus={66} />);
    expect(screen.getByRole("status")).toHaveTextContent("Correct! +400 + 66 = 466");
  });

  it("shows green solved copy with base score only when bonus is zero", () => {
    render(<PinpointResultOverlay kind="solved" baseScore={400} timeBonus={0} />);
    expect(screen.getByRole("status")).toHaveTextContent("Correct! +400");
  });

  it("shows red failed copy with zero points", () => {
    render(<PinpointResultOverlay kind="failed" baseScore={0} />);
    expect(screen.getByRole("status")).toHaveTextContent("Out of clues — +0");
  });

  it("never renders answer or alias text from leaked props", () => {
    render(
      <PinpointResultOverlay
        kind="failed"
        baseScore={0}
        // @ts-expect-error — simulate a future API leak in tests
        answer="cloud computing"
        answer_aliases={["cloud", "computing"]}
      />,
    );

    expect(screen.queryByText("cloud computing")).toBeNull();
    expect(screen.queryByText("cloud")).toBeNull();
    expect(screen.queryByText("computing")).toBeNull();
  });
});
