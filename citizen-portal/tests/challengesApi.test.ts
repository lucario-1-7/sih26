import { describe, it, expect, vi, afterEach } from 'vitest';
import {
  mapBackendChallengeToProblem,
  challengesApi,
  BackendChallengeResponse,
} from '../src/lib/api/challengesApi';

function jsonResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

describe('Challenges API Adapter', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('maps a real BackendChallengeResponse to the frontend Problem structure', () => {
    const mockBackendItem: BackendChallengeResponse = {
      id: '550e8400-e29b-41d4-a716-446655440000',
      title: 'Solar Desiccant Dryer Network in Gumla',
      description: 'Lac farmers losing crop value due to post-harvest humidity spikes.',
      status: 'open',
      severity: 'high',
      submitted_by_id: 'usr-1234',
      administrative_area_id: 'area-9876',
      pin_code: '835207',
      cluster_id: 'cluster-1',
      on_behalf_of_name: 'Birsa Munda FPO',
      on_behalf_of_phone: '+91 94311 00000',
      content_domain: 'agriculture',
      created_at: '2026-02-15T10:00:00Z',
      updated_at: '2026-02-16T09:00:00Z',
    };

    const problem = mapBackendChallengeToProblem(mockBackendItem, { areaName: 'Gumla' });

    expect(problem.id).toBe(mockBackendItem.id);
    expect(problem.title).toBe(mockBackendItem.title);
    expect(problem.description).toBe(mockBackendItem.description);
    // real backend status "open" -> "Under Review" (see mapBackendStatusToFrontend)
    expect(problem.status).toBe('Under Review');
    expect(problem.category).toBe('Agriculture');
    expect(problem.submittedBy.fullName).toBe('Birsa Munda FPO');
    expect(problem.location.district).toBe('Gumla');
    // real signals only: submitted + under-review + clustered (cluster_id is set)
    expect(problem.milestones.length).toBe(3);
    expect(problem.milestones.every((m) => m.completed)).toBe(true);
  });

  it('shows an unclassified challenge honestly rather than guessing a category', () => {
    const mockItem: BackendChallengeResponse = {
      id: 'abc12345-0000-0000-0000-000000000000',
      title: 'New report, not yet classified',
      description: 'The async ML worker has not run yet.',
      status: 'submitted',
      submitted_by_id: 'usr-1',
      administrative_area_id: 'area-1',
      content_domain: null,
      created_at: '2026-02-15T10:00:00Z',
      updated_at: '2026-02-15T10:00:00Z',
    };
    const problem = mapBackendChallengeToProblem(mockItem);
    // only the "Submitted" milestone exists — nothing else is fabricated
    expect(problem.milestones).toHaveLength(1);
    expect(problem.milestones[0].stage).toBe('Submitted');
  });

  it('getMyChallenges calls the real /challenges endpoint and returns real items', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ items: [{ id: '1', title: 'x' }], next_cursor: null })
    );
    vi.stubGlobal('fetch', fetchMock);

    const items = await challengesApi.getMyChallenges('user-1');

    expect(items).toHaveLength(1);
    const [url] = fetchMock.mock.calls[0];
    expect(String(url)).toContain('/challenges?submitted_by_id=user-1');
  });

  it('getMyChallenges propagates a real error instead of returning fabricated data', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
    vi.stubGlobal('fetch', fetchMock);

    await expect(challengesApi.getMyChallenges('user-1')).rejects.toThrow();
  });

  it('createChallenge posts the real payload and returns the real created challenge', async () => {
    const created: BackendChallengeResponse = {
      id: 'new-id',
      title: 'Water filtration in Latehar',
      description: 'High fluoride concentration causing skeletal fluorosis.',
      status: 'submitted',
      submitted_by_id: 'usr-1',
      administrative_area_id: 'area-829221',
      pin_code: '829221',
      created_at: '2026-02-15T10:00:00Z',
      updated_at: '2026-02-15T10:00:00Z',
    };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(created, 201));
    vi.stubGlobal('fetch', fetchMock);

    const result = await challengesApi.createChallenge({
      title: 'Water filtration in Latehar',
      description: 'High fluoride concentration causing skeletal fluorosis.',
      administrative_area_id: 'area-829221',
      pin_code: '829221',
    });

    expect(result.id).toBe('new-id');
    const [, init] = fetchMock.mock.calls[0];
    const body = JSON.parse((init as RequestInit).body as string);
    expect(body.administrative_area_id).toBe('area-829221');
  });

  it('createChallenge propagates a real 422 error instead of silently succeeding', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ detail: 'Title must be at least 5 characters', code: 'VALIDATION_ERROR' }, 422)
    );
    vi.stubGlobal('fetch', fetchMock);

    await expect(
      challengesApi.createChallenge({
        title: 'x',
        description: 'too short',
        administrative_area_id: 'area-1',
      })
    ).rejects.toThrow(/Title must be at least 5 characters/);
  });
});
