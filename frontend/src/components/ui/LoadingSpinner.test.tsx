import { render, screen } from "@testing-library/react";
import { LoadingSpinner } from "./LoadingSpinner";

describe("LoadingSpinner", () => {
  it("renders without label", () => {
    render(<LoadingSpinner />);
    expect(screen.getByLabelText("Loading")).toBeInTheDocument();
  });

  it("renders with label text", () => {
    render(<LoadingSpinner label="Cargando..." />);
    expect(screen.getByLabelText("Cargando...")).toBeInTheDocument();
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("renders sm size with correct dimensions", () => {
    const { container } = render(<LoadingSpinner size="sm" />);
    const spinner = container.querySelector("div > div > div") as HTMLElement;
    expect(spinner.getAttribute("style")).toContain("16px");
  });

  it("renders lg size with correct dimensions", () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    const spinner = container.querySelector("div > div > div") as HTMLElement;
    expect(spinner.getAttribute("style")).toContain("40px");
  });
});
