import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { MatchHistoryPanel } from "./MatchHistoryPanel";

describe("MatchHistoryPanel", () => {
  it("renders heading", () => {
    const { getByText } = render(<MatchHistoryPanel userId={1} />);
    expect(getByText("Match History")).toBeInTheDocument();
  });
});

