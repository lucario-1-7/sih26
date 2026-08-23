import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { useAppStore } from '../src/store/useAppStore';

function jsonResponse(body: unknown, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => body } as Response;
}

describe('AppStore Zustand Store', () => {
  beforeEach(() => {
    localStorage.clear();
    useAppStore.setState({ user: null, problems: [], userUpvotes: {}, administrativeAreas: [] });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should start with no logged-in user — no demo/default account', () => {
    expect(useAppStore.getState().user).toBeNull();
  });

  it('should initialize with default English language and normal text scale', () => {
    const state = useAppStore.getState();
    expect(state.language).toBe('en');
    expect(state.textScale).toBe('normal');
  });

  it('should toggle language between English and Hindi', () => {
    useAppStore.getState().setLanguage('hi');
    expect(useAppStore.getState().language).toBe('hi');

    useAppStore.getState().setLanguage('en');
    expect(useAppStore.getState().language).toBe('en');
  });

  it('should scale text size correctly (increase, decrease, cycle)', () => {
    useAppStore.getState().setTextScale('normal');
    expect(useAppStore.getState().textScale).toBe('normal');

    useAppStore.getState().increaseTextScale();
    expect(useAppStore.getState().textScale).toBe('large');

    useAppStore.getState().increaseTextScale();
    expect(useAppStore.getState().textScale).toBe('larger');

    useAppStore.getState().decreaseTextScale();
    expect(useAppStore.getState().textScale).toBe('large');

    useAppStore.getState().cycleTextScale();
    expect(useAppStore.getState().textScale).toBe('larger');

    useAppStore.getState().cycleTextScale();
    expect(useAppStore.getState().textScale).toBe('normal');
  });

  it('should allow upvoting a problem only once per session (client-side only — no backend upvote endpoint exists)', () => {
    useAppStore.setState({
      problems: [
        {
          id: 'pr-jh-005',
          trackingCode: 'JH-PRJH005',
          title: 't',
          category: 'Water Resources',
          description: 'd',
          location: { district: '', villageOrArea: '', latitude: 0, longitude: 0, formattedAddress: '' },
          media: [],
          status: 'Submitted',
          upvotes: 3,
          submittedBy: { id: 'u1', fullName: 'x', phone: '', district: '', isVerified: true },
          milestones: [],
          createdAt: '',
          updatedAt: '',
        },
      ],
    });

    const res1 = useAppStore.getState().upvoteProblem('pr-jh-005');
    expect(res1.success).toBe(true);
    expect(useAppStore.getState().problems.find((p) => p.id === 'pr-jh-005')?.upvotes).toBe(4);
    expect(useAppStore.getState().hasUserUpvoted('pr-jh-005')).toBe(true);

    const res2 = useAppStore.getState().upvoteProblem('pr-jh-005');
    expect(res2.success).toBe(false);
    expect(res2.message).toContain('already upvoted');
  });

  it('addProblem calls the real backend and only adds the problem on real success', async () => {
    const created = {
      id: 'new-id',
      title: 'Water contamination in Kanke block',
      description: 'High iron content in tubewell water affecting 200 households.',
      status: 'submitted',
      submitted_by_id: 'u1',
      administrative_area_id: 'area-834006',
      pin_code: '834006',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(created, 201)));

    const newProblem = await useAppStore.getState().addProblem({
      title: 'Water contamination in Kanke block',
      description: 'High iron content in tubewell water affecting 200 households.',
      administrative_area_id: 'area-834006',
      pin_code: '834006',
    });

    expect(newProblem.id).toBe('new-id');
    expect(newProblem.status).toBe('Submitted');

    const found = useAppStore.getState().getProblemById(newProblem.id);
    expect(found).toBeDefined();
    expect(found?.title).toBe('Water contamination in Kanke block');
  });

  it('addProblem never fabricates a submission when the backend rejects it', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'Select an area', code: 'VALIDATION_ERROR' }, 422))
    );

    await expect(
      useAppStore.getState().addProblem({
        title: 'Missing area',
        description: 'This should fail because no valid area was chosen.',
        administrative_area_id: '',
      })
    ).rejects.toThrow();

    expect(useAppStore.getState().problems).toHaveLength(0);
  });
});
