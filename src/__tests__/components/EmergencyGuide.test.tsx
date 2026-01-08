import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EmergencyGuide, EmergencyGuideTrigger } from "@/components/ui/EmergencyGuide";

describe("EmergencyGuide", () => {
  beforeEach(() => {
    // Create portal root if it doesn't exist
    if (!document.getElementById("portal-root")) {
      const portalRoot = document.createElement("div");
      portalRoot.id = "portal-root";
      document.body.appendChild(portalRoot);
    }
  });

  describe("modal visibility", () => {
    it("renders modal when isOpen is true", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      expect(screen.getByText("🩺 Where Should I Go?")).toBeInTheDocument();
    });

    it("does not render modal content when isOpen is false", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={false} onClose={onClose} />);

      expect(screen.queryByText("🩺 Where Should I Go?")).not.toBeInTheDocument();
    });
  });

  describe("option selection", () => {
    it("renders all four emergency options", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      expect(screen.getByText("Call 911")).toBeInTheDocument();
      expect(screen.getByText("Ski Patrol")).toBeInTheDocument();
      expect(screen.getByText("Urgent Care")).toBeInTheDocument();
      expect(screen.getByText("Emergency Room")).toBeInTheDocument();
    });

    it("shows option details when an option is selected", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      // Click on Ski Patrol option
      fireEvent.click(screen.getByText("Ski Patrol"));

      // Should show examples
      expect(screen.getByText("Examples:")).toBeInTheDocument();
      expect(screen.getByText("Can't ski down on your own")).toBeInTheDocument();
      expect(screen.getByText("Suspected broken bone")).toBeInTheDocument();

      // Should show action
      expect(
        screen.getByText("Contact any lift operator or call resort emergency line")
      ).toBeInTheDocument();

      // Should show back button
      expect(screen.getByText("← Back")).toBeInTheDocument();
    });

    it("shows 911 call button when 911 option is selected", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      // Click on Call 911 option
      fireEvent.click(screen.getByText("Call 911"));

      // Should show the call button
      const callButton = screen.getByText("📞 Call 911 Now");
      expect(callButton).toBeInTheDocument();
      expect(callButton.closest("a")).toHaveAttribute("href", "tel:911");
    });

    it("does not show 911 call button for non-911 options", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      // Click on Urgent Care option
      fireEvent.click(screen.getByText("Urgent Care"));

      // Should NOT show the 911 call button
      expect(screen.queryByText("📞 Call 911 Now")).not.toBeInTheDocument();
    });
  });

  describe("navigation", () => {
    it("returns to option list when back button is clicked", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      // Select an option
      fireEvent.click(screen.getByText("Ski Patrol"));

      // Verify we're in detail view
      expect(screen.getByText("Examples:")).toBeInTheDocument();

      // Click back
      fireEvent.click(screen.getByText("← Back"));

      // Should be back at option list (examples no longer visible)
      expect(screen.queryByText("Examples:")).not.toBeInTheDocument();
      expect(screen.getByText("Call 911")).toBeInTheDocument();
    });

    it("calls onClose when close button is clicked", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      // Select an option to get to detail view with Close button
      fireEvent.click(screen.getByText("Ski Patrol"));

      // Click close
      fireEvent.click(screen.getByText("Close"));

      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("resets selection state when modal is closed and reopened", () => {
      const onClose = vi.fn();
      const { rerender } = render(
        <EmergencyGuide isOpen={true} onClose={onClose} />
      );

      // Select an option
      fireEvent.click(screen.getByText("Ski Patrol"));

      // Close modal
      fireEvent.click(screen.getByText("Close"));

      // Reopen modal
      rerender(<EmergencyGuide isOpen={true} onClose={onClose} />);

      // Selection should be reset (shows option list, not details)
      expect(screen.getByText("Call 911")).toBeInTheDocument();
      expect(screen.queryByText("Examples:")).not.toBeInTheDocument();
    });
  });

  describe("disclaimer", () => {
    it("shows safety disclaimer", () => {
      const onClose = vi.fn();
      render(<EmergencyGuide isOpen={true} onClose={onClose} />);

      expect(
        screen.getByText(/This is general guidance only.*call 911/i)
      ).toBeInTheDocument();
    });
  });
});

describe("EmergencyGuideTrigger", () => {
  it("renders the trigger button with correct text", () => {
    const onClick = vi.fn();
    render(<EmergencyGuideTrigger onClick={onClick} />);

    expect(screen.getByText("Where Should I Go?")).toBeInTheDocument();
    expect(screen.getByText("🩺")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const onClick = vi.fn();
    render(<EmergencyGuideTrigger onClick={onClick} />);

    fireEvent.click(screen.getByRole("button"));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("applies custom className", () => {
    const onClick = vi.fn();
    render(<EmergencyGuideTrigger onClick={onClick} className="custom-class" />);

    const button = screen.getByRole("button");
    expect(button).toHaveClass("custom-class");
  });
});
