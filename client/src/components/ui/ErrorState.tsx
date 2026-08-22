import { ApiError } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";

const FRIENDLY_MESSAGES: Record<number, string> = {
  401: "Your session has expired. Please sign in again.",
  403: "You don't have permission to view this.",
  404: "That couldn't be found.",
  409: "That action conflicts with the current state — try refreshing.",
  422: "Some of the information provided wasn't valid.",
  503: "The service is temporarily unavailable. Please try again shortly.",
  500: "Something went wrong on our end.",
};

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return FRIENDLY_MESSAGES[error.status] ?? error.message ?? "Something went wrong.";
  }
  return "Something went wrong.";
}

/**
 * For the INITIAL login flow (OTP request/verify) only — never for requests
 * against an already-authenticated session.
 *
 * `errorMessage()` maps every 401 to "Your session has expired", which is
 * correct for a protected request whose access token turned out to be
 * unrefreshable, but actively wrong here: a 401 from `/auth/otp/verify`
 * means the code was wrong/expired, not that a session (which doesn't exist
 * yet) expired. The backend's `detail` for that case is already
 * precise and safe to show verbatim ("Invalid or expired OTP") — trust it
 * instead of the generic session-expiry copy.
 */
export function authErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message || "Something went wrong. Please try again.";
  }
  return "Something went wrong. Please try again.";
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-6 text-center">
      <p className="text-sm font-medium text-red-800">{errorMessage(error)}</p>
      {onRetry ? (
        <Button variant="secondary" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}
