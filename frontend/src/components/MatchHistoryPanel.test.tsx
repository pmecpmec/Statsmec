import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MatchHistoryPanel } from "./MatchHistoryPanel";

describe("MatchHistoryPanel", () => {
  it("renders heading", () => {
    render(<MatchHistoryPanel userId={1} />);
    expect(screen.getByText("Match History")).toBeDefined();
  });
});

