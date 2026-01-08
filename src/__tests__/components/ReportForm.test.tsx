import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ReportForm, type ReportData } from "@/components/ui/ReportForm";

describe("ReportForm", () => {
  beforeEach(() => {
    // Create portal root if it doesn't exist
    if (!document.getElementById("portal-root")) {
      const portalRoot = document.createElement("div");
      portalRoot.id = "portal-root";
      document.body.appendChild(portalRoot);
    }
  });

  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    itemType: "resort" as const,
    itemName: "Vail",
    itemId: "vail-co",
  };

  describe("modal visibility", () => {
    it("renders modal when isOpen is true", () => {
      render(<ReportForm {...defaultProps} />);

      expect(screen.getByText("Report an Issue")).toBeInTheDocument();
    });

    it("does not render when isOpen is false", () => {
      render(<ReportForm {...defaultProps} isOpen={false} />);

      expect(screen.queryByText("Report an Issue")).not.toBeInTheDocument();
    });
  });

  describe("item display", () => {
    it("shows the item name being reported", () => {
      render(<ReportForm {...defaultProps} />);

      expect(screen.getByText("Vail")).toBeInTheDocument();
      expect(screen.getByText("(resort)")).toBeInTheDocument();
    });

    it("shows correct label for clinic", () => {
      render(<ReportForm {...defaultProps} itemType="clinic" itemName="DaVita Denver" />);

      expect(screen.getByText("DaVita Denver")).toBeInTheDocument();
      expect(screen.getByText("(dialysis clinic)")).toBeInTheDocument();
    });

    it("shows correct label for hospital", () => {
      render(<ReportForm {...defaultProps} itemType="hospital" itemName="Vail Health" />);

      expect(screen.getByText("Vail Health")).toBeInTheDocument();
      expect(screen.getByText("(hospital)")).toBeInTheDocument();
    });
  });

  describe("category selection", () => {
    it("renders all report categories", () => {
      render(<ReportForm {...defaultProps} />);

      expect(screen.getByText("Incorrect information")).toBeInTheDocument();
      expect(screen.getByText("Permanently closed")).toBeInTheDocument();
      expect(screen.getByText("Missing information")).toBeInTheDocument();
      expect(screen.getByText("Other issue")).toBeInTheDocument();
    });

    it("highlights selected category", () => {
      render(<ReportForm {...defaultProps} />);

      const categoryBtn = screen.getByText("Incorrect information").closest("button");
      fireEvent.click(categoryBtn!);

      // Should have the selected styling (pink border)
      expect(categoryBtn).toHaveClass("border-pink-500");
    });

    it("updates placeholder text based on category", () => {
      render(<ReportForm {...defaultProps} />);

      // Select "Permanently closed"
      fireEvent.click(screen.getByText("Permanently closed"));

      const textarea = screen.getByPlaceholderText(/When did this location close/);
      expect(textarea).toBeInTheDocument();
    });
  });

  describe("form validation", () => {
    it("submit button is disabled when no category or description", () => {
      render(<ReportForm {...defaultProps} />);

      const submitBtn = screen.getByText("Submit Report");
      expect(submitBtn).toBeDisabled();
    });

    it("submit button is disabled when only category is selected", () => {
      render(<ReportForm {...defaultProps} />);

      fireEvent.click(screen.getByText("Incorrect information"));

      const submitBtn = screen.getByText("Submit Report");
      expect(submitBtn).toBeDisabled();
    });

    it("submit button is enabled when category and description are provided", () => {
      render(<ReportForm {...defaultProps} />);

      fireEvent.click(screen.getByText("Incorrect information"));
      
      const textarea = screen.getByPlaceholderText(/What information is incorrect/);
      fireEvent.change(textarea, { target: { value: "Phone number is wrong" } });

      const submitBtn = screen.getByText("Submit Report");
      expect(submitBtn).not.toBeDisabled();
    });
  });

  describe("form submission", () => {
    it("calls onSubmit with correct data", async () => {
      const onSubmit = vi.fn();
      render(<ReportForm {...defaultProps} onSubmit={onSubmit} />);

      // Select category
      fireEvent.click(screen.getByText("Incorrect information"));

      // Enter description
      const textarea = screen.getByPlaceholderText(/What information is incorrect/);
      fireEvent.change(textarea, { target: { value: "Phone number is wrong" } });

      // Enter email
      const emailInput = screen.getByPlaceholderText("your@email.com");
      fireEvent.change(emailInput, { target: { value: "test@example.com" } });

      // Submit
      fireEvent.click(screen.getByText("Submit Report"));

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledTimes(1);
      });

      const reportData: ReportData = onSubmit.mock.calls[0][0];
      expect(reportData.itemType).toBe("resort");
      expect(reportData.itemId).toBe("vail-co");
      expect(reportData.itemName).toBe("Vail");
      expect(reportData.category).toBe("wrong_info");
      expect(reportData.description).toBe("Phone number is wrong");
      expect(reportData.contactEmail).toBe("test@example.com");
      expect(reportData.timestamp).toBeDefined();
    });

    it("shows success message after submission", async () => {
      render(<ReportForm {...defaultProps} />);

      // Fill and submit form
      fireEvent.click(screen.getByText("Incorrect information"));
      const textarea = screen.getByPlaceholderText(/What information is incorrect/);
      fireEvent.change(textarea, { target: { value: "Phone number is wrong" } });
      fireEvent.click(screen.getByText("Submit Report"));

      await waitFor(() => {
        expect(screen.getByText("Thank You!")).toBeInTheDocument();
      });

      expect(screen.getByText("Your report has been submitted.")).toBeInTheDocument();
    });

    it("does not include email in report data if empty", async () => {
      const onSubmit = vi.fn();
      render(<ReportForm {...defaultProps} onSubmit={onSubmit} />);

      // Fill form without email
      fireEvent.click(screen.getByText("Incorrect information"));
      const textarea = screen.getByPlaceholderText(/What information is incorrect/);
      fireEvent.change(textarea, { target: { value: "Phone is wrong" } });
      fireEvent.click(screen.getByText("Submit Report"));

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled();
      });

      const reportData: ReportData = onSubmit.mock.calls[0][0];
      expect(reportData.contactEmail).toBeUndefined();
    });
  });

  describe("modal close behavior", () => {
    it("calls onClose when cancel button is clicked", () => {
      const onClose = vi.fn();
      render(<ReportForm {...defaultProps} onClose={onClose} />);

      fireEvent.click(screen.getByText("Cancel"));

      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("calls onClose when close button clicked after submission", async () => {
      const onClose = vi.fn();
      render(<ReportForm {...defaultProps} onClose={onClose} />);

      // Submit form
      fireEvent.click(screen.getByText("Incorrect information"));
      const textarea = screen.getByPlaceholderText(/What information is incorrect/);
      fireEvent.change(textarea, { target: { value: "Phone is wrong" } });
      fireEvent.click(screen.getByText("Submit Report"));

      await waitFor(() => {
        expect(screen.getByText("Thank You!")).toBeInTheDocument();
      });

      // Click close on success screen
      fireEvent.click(screen.getByText("Close"));

      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("resets form state when modal is closed and reopened", async () => {
      const onClose = vi.fn();
      const { rerender } = render(
        <ReportForm {...defaultProps} onClose={onClose} />
      );

      // Fill form partially
      fireEvent.click(screen.getByText("Incorrect information"));
      const textarea = screen.getByPlaceholderText(/What information is incorrect/);
      fireEvent.change(textarea, { target: { value: "Test" } });

      // Close modal
      fireEvent.click(screen.getByText("Cancel"));

      // Reopen modal
      rerender(<ReportForm {...defaultProps} onClose={onClose} isOpen={true} />);

      // Form should be reset - submit should be disabled
      const submitBtn = screen.getByText("Submit Report");
      expect(submitBtn).toBeDisabled();
    });
  });
});
