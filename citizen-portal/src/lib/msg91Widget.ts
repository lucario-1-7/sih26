/**
 * Thin wrapper around MSG91's real OTP Widget JS SDK
 * (https://verify.msg91.com/otp-provider.js).
 *
 * This is the CLIENT-SIDE half of the integration: the widget talks to
 * MSG91 directly to send, retry, and verify the real OTP — this app's
 * backend is never involved until a verified `access-token` exists. Only
 * WIDGET_ID and TOKEN_AUTH are used here, both meant for client-side
 * embedding per MSG91's own "Client Side Integration" panel (the same way
 * a payment provider's publishable key is meant to be public). The
 * account-level MSG91_AUTH_KEY never appears in this codebase.
 *
 * `exposeMethods: true` suppresses MSG91's own popup UI and exposes
 * `sendOtp` / `verifyOtp` / `retryOtp` so this app's own OTP screen (the
 * existing 2-step phone/OTP UI) keeps its design — only the underlying
 * implementation changes from a fake `setTimeout` to a real widget call.
 *
 * Two real quirks of the actual shipped SDK (confirmed by fetching and
 * reading https://verify.msg91.com/otp-provider.js directly — it is an
 * Angular Elements bundle, not a small hand-written script):
 *
 *  1. `initSendOTP(config)` does NOT synchronously expose `window.sendOtp`
 *     etc. It defers behind `document.readyState`/`DOMContentLoaded`, then
 *     mounts a `<msg91-otp-provider>` custom element whose Angular
 *     component boots, fetches the widget's own configuration from MSG91,
 *     and only in `ngAfterViewInit()` — once all of that has resolved —
 *     calls `exposeMethodsToWindow()`. There is a genuine, unbounded race
 *     between calling `initSendOTP()` and `window.sendOtp` existing.
 *  2. Once exposed, `sendOtp` / `verifyOtp` / `retryOtp` are
 *     callback-based (`fn(value, successCallback, failureCallback)`) and
 *     return `undefined` — they are NOT Promise-returning functions.
 *     `await window.sendOtp(id)` previously resolved immediately to
 *     `undefined`, which this wrapper wrongly treated as "no OTP sent".
 */

const WIDGET_SCRIPT_SRC = 'https://verify.msg91.com/otp-provider.js';

const WIDGET_ID = process.env.NEXT_PUBLIC_MSG91_WIDGET_ID || '';
const TOKEN_AUTH = process.env.NEXT_PUBLIC_MSG91_TOKEN_AUTH || '';

// How long to wait for the widget's async custom-element bootstrap to
// finish exposing sendOtp/verifyOtp/retryOtp on `window` after
// initSendOTP() is called. This is not documented by MSG91 — chosen to
// comfortably cover a real network round-trip (the widget fetches its own
// config from MSG91) plus Angular change detection.
const EXPOSE_METHODS_TIMEOUT_MS = 15000;
const EXPOSE_METHODS_POLL_MS = 100;

function debugLog(event: string, detail?: Record<string, unknown>) {
  if (process.env.NODE_ENV === 'production') return;
  // Never logs the OTP, tokenAuth, access-token, or any MSG91 secret —
  // only the shape/status of what happened, for diagnosing widget issues.
  console.debug(`[msg91-widget] ${event}`, detail ?? {});
}

function maskIdentifier(identifier: string): string {
  return identifier.length > 4 ? `${'*'.repeat(identifier.length - 4)}${identifier.slice(-4)}` : '****';
}

export class Msg91WidgetError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'Msg91WidgetError';
  }
}

type Msg91CallbackPayload = { type?: string; message?: unknown } | string | undefined;

declare global {
  interface Window {
    sendOtp?: (identifier: string, success?: (data: Msg91CallbackPayload) => void, failure?: (err: Msg91CallbackPayload) => void) => void;
    verifyOtp?: (otp: string, success?: (data: Msg91CallbackPayload) => void, failure?: (err: Msg91CallbackPayload) => void) => void;
    retryOtp?: (channel: string | null, success?: (data: Msg91CallbackPayload) => void, failure?: (err: Msg91CallbackPayload) => void) => void;
    initSendOTP?: (config: Record<string, unknown>) => void;
  }
}

let scriptLoadPromise: Promise<void> | null = null;
let initCalled = false;

function loadScript(): Promise<void> {
  if (scriptLoadPromise) return scriptLoadPromise;
  scriptLoadPromise = new Promise((resolve, reject) => {
    if (typeof document === 'undefined') {
      reject(new Msg91WidgetError('MSG91 widget can only load in the browser'));
      return;
    }
    const existing = document.querySelector(`script[src="${WIDGET_SCRIPT_SRC}"]`);
    if (existing) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = WIDGET_SCRIPT_SRC;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Msg91WidgetError('Failed to load the MSG91 verification widget.'));
    document.body.appendChild(script);
  });
  return scriptLoadPromise;
}

/** Resolves once window.sendOtp/verifyOtp/retryOtp all exist, or throws on timeout. */
function waitForExposedMethods(): Promise<void> {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const check = () => {
      if (
        typeof window.sendOtp === 'function' &&
        typeof window.verifyOtp === 'function' &&
        typeof window.retryOtp === 'function'
      ) {
        debugLog('exposed_methods_ready', { waitedMs: Date.now() - start });
        resolve();
        return;
      }
      if (Date.now() - start > EXPOSE_METHODS_TIMEOUT_MS) {
        reject(
          new Msg91WidgetError(
            'The verification widget did not finish loading. Please check your connection and try again.'
          )
        );
        return;
      }
      setTimeout(check, EXPOSE_METHODS_POLL_MS);
    };
    check();
  });
}

/**
 * Loads the script, calls initSendOTP exactly once per page load, and waits
 * for the widget to actually finish exposing sendOtp/verifyOtp/retryOtp on
 * `window` before returning — calling those functions before this resolves
 * is exactly what produced "MSG91 widget did not expose sendOtp".
 */
export async function ensureMsg91WidgetInitialized(): Promise<void> {
  if (!WIDGET_ID || !TOKEN_AUTH) {
    throw new Msg91WidgetError(
      'MSG91 widget is not configured (NEXT_PUBLIC_MSG91_WIDGET_ID / NEXT_PUBLIC_MSG91_TOKEN_AUTH missing).'
    );
  }
  await loadScript();
  if (!initCalled) {
    if (typeof window.initSendOTP !== 'function') {
      throw new Msg91WidgetError('MSG91 widget script loaded but initSendOTP is unavailable.');
    }
    debugLog('initSendOTP_call', { widgetId: WIDGET_ID.slice(0, 4) + '…' });
    window.initSendOTP({
      widgetId: WIDGET_ID,
      tokenAuth: TOKEN_AUTH,
      exposeMethods: true,
      // Required by the SDK (throws "success callback function missing!"
      // otherwise) but unused: every call site below passes its own
      // per-call success/failure callbacks to sendOtp/verifyOtp/retryOtp,
      // which is how this exposeMethods:true integration actually reports
      // outcomes.
      success: () => debugLog('top_level_success_callback_fired'),
      failure: (err: unknown) => debugLog('top_level_failure_callback_fired', { hasError: !!err }),
    });
    initCalled = true;
  }
  await waitForExposedMethods();
}

function extractString(payload: Msg91CallbackPayload): string | null {
  if (typeof payload === 'string') return payload || null;
  if (payload && typeof payload === 'object' && typeof payload.message === 'string' && payload.message) {
    return payload.message;
  }
  return null;
}

function describeFailure(payload: Msg91CallbackPayload, fallback: string): string {
  if (typeof payload === 'object' && payload && typeof payload.message === 'string' && payload.message) {
    return payload.message;
  }
  if (typeof payload === 'string' && payload) return payload;
  return fallback;
}

/** identifier: national format the SDK expects, e.g. "919876543210" (no '+'). */
export async function sendMsg91Otp(identifier: string): Promise<void> {
  await ensureMsg91WidgetInitialized();
  if (typeof window.sendOtp !== 'function') {
    throw new Msg91WidgetError('MSG91 widget did not expose sendOtp.');
  }
  debugLog('sendOtp_call', { identifier: maskIdentifier(identifier) });
  await new Promise<void>((resolve, reject) => {
    try {
      window.sendOtp!(
        identifier,
        (data) => {
          debugLog('sendOtp_success', { hasReqId: extractString(data) !== null });
          resolve();
        },
        (err) => {
          const reason = describeFailure(err, 'MSG91 could not send the OTP for this number.');
          debugLog('sendOtp_failure', { reason });
          reject(new Msg91WidgetError(reason));
        }
      );
    } catch (err) {
      const reason = err instanceof Error ? err.message : 'MSG91 could not send the OTP for this number.';
      debugLog('sendOtp_thrown', { reason });
      reject(new Msg91WidgetError(reason));
    }
  });
}

export async function retryMsg91Otp(): Promise<void> {
  await ensureMsg91WidgetInitialized();
  if (typeof window.retryOtp !== 'function') {
    throw new Msg91WidgetError('MSG91 widget did not expose retryOtp.');
  }
  debugLog('retryOtp_call');
  await new Promise<void>((resolve, reject) => {
    try {
      window.retryOtp!(
        null,
        () => {
          debugLog('retryOtp_success');
          resolve();
        },
        (err) => {
          const reason = describeFailure(err, 'MSG91 could not resend the OTP.');
          debugLog('retryOtp_failure', { reason });
          reject(new Msg91WidgetError(reason));
        }
      );
    } catch (err) {
      const reason = err instanceof Error ? err.message : 'MSG91 could not resend the OTP.';
      debugLog('retryOtp_thrown', { reason });
      reject(new Msg91WidgetError(reason));
    }
  });
}

/** Returns the widget-issued access-token on success — never a phone number,
 * never generated locally. This token (and only this token) is what the
 * backend verifies. */
export async function verifyMsg91Otp(otp: string): Promise<string> {
  await ensureMsg91WidgetInitialized();
  if (typeof window.verifyOtp !== 'function') {
    throw new Msg91WidgetError('MSG91 widget did not expose verifyOtp.');
  }
  debugLog('verifyOtp_call');
  return new Promise<string>((resolve, reject) => {
    try {
      window.verifyOtp!(
        otp,
        (data) => {
          const accessToken = extractString(data);
          if (!accessToken) {
            debugLog('verifyOtp_success_no_token');
            reject(new Msg91WidgetError('MSG91 confirmed the OTP but did not return an access token.'));
            return;
          }
          debugLog('verifyOtp_success', { hasAccessToken: true });
          resolve(accessToken);
        },
        (err) => {
          const reason = describeFailure(err, 'Incorrect or expired OTP. Please try again.');
          debugLog('verifyOtp_failure', { reason });
          reject(new Msg91WidgetError(reason));
        }
      );
    } catch (err) {
      const reason = err instanceof Error ? err.message : 'Incorrect or expired OTP. Please try again.';
      debugLog('verifyOtp_thrown', { reason });
      reject(new Msg91WidgetError(reason));
    }
  });
}
