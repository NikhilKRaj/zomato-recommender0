import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("UI error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-red-200 bg-red-50 p-md text-center" role="alert">
          <p className="text-headline-sm text-red-800">Something went wrong displaying this page.</p>
          <button
            type="button"
            onClick={() => this.setState({ hasError: false })}
            className="mt-sm text-body-md text-red-600 underline"
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
