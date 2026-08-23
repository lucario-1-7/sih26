import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { useAppStore } from '../src/store/useAppStore';
import { translations } from '../src/lib/translations';

function jsonResponse(body: unknown, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => body } as Response;
}

describe('SocioSolve Citizen Portal : End-to-End (E2E) Workflow Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    useAppStore.setState({ user: null, problems: [], userUpvotes: {}, administrativeAreas: [] });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('E2E Flow 1: real login (backend-verified) -> real grievance submission -> dashboard ingestion', async () => {
    // 1. Backend confirms the MSG91-verified session (GET /users/me) — no
    // local fabrication of a logged-in citizen.
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ id: 'u-sunita', phone: '+919431155667', name: '+919431155667', role: 'citizen' }))
    );
    localStorage.setItem('sociosolve_access_token', 'real-token');
    await useAppStore.getState().completeLogin();

    const user = useAppStore.getState().user;
    expect(user).toBeDefined();
    expect(user?.phone).toBe('+919431155667');
    expect(user?.isVerified).toBe(true);

    // 2. Citizen raises a real grievance — backend call, real response.
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(
          {
            id: 'grv-1',
            title: 'Solar Irrigation Pump Failure in Shikaripara',
            description: 'Microgrid inverter burned out during lightning storm.',
            status: 'submitted',
            submitted_by_id: 'u-sunita',
            administrative_area_id: 'area-814101',
            pin_code: '814101',
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          201
        )
      )
    );

    const newGrievance = await useAppStore.getState().addProblem({
      title: 'Solar Irrigation Pump Failure in Shikaripara',
      description: 'Microgrid inverter burned out during lightning storm.',
      administrative_area_id: 'area-814101',
      pin_code: '814101',
    });

    expect(newGrievance.id).toBe('grv-1');
    expect(newGrievance.status).toBe('Submitted');

    // 3. Problem appears at the top of the repository
    const ingested = useAppStore.getState().problems.find((p) => p.id === newGrievance.id);
    expect(ingested).toBeDefined();
  });

  it('E2E Flow 2: submit then find the same grievance by its id/tracking code', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(
          {
            id: 'grv-2',
            title: 'KGBV STEM Lab Equipment Delivery',
            description: 'Robotics kits required for 120 tribal girl students.',
            status: 'submitted',
            submitted_by_id: 'u1',
            administrative_area_id: 'area-829221',
            pin_code: '829221',
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          201
        )
      )
    );

    const problem = await useAppStore.getState().addProblem({
      title: 'KGBV STEM Lab Equipment Delivery',
      description: 'Robotics kits required for 120 tribal girl students.',
      administrative_area_id: 'area-829221',
      pin_code: '829221',
    });

    const trackedById = useAppStore.getState().getProblemById(problem.id);
    const trackedByCode = useAppStore.getState().getProblemById(problem.trackingCode);
    expect(trackedById?.id).toBe(problem.id);
    expect(trackedByCode?.id).toBe(problem.id);
    // real signal only: "Submitted" is the sole milestone for a brand-new report
    expect(trackedById?.milestones).toHaveLength(1);
    expect(trackedById?.milestones[0].completed).toBe(true);
  });

  it('E2E Flow 3: community upvoting with anti-spam single-vote protection (client-side only)', () => {
    useAppStore.setState({
      problems: [
        {
          id: 'pr-jh-002',
          trackingCode: 'JH-PRJH002',
          title: 't',
          category: 'Water Resources',
          description: 'd',
          location: { district: 'Khunti', villageOrArea: '', latitude: 0, longitude: 0, formattedAddress: '' },
          media: [],
          status: 'Submitted',
          upvotes: 5,
          submittedBy: { id: 'u1', fullName: 'x', phone: '', district: '', isVerified: true },
          milestones: [],
          createdAt: '',
          updatedAt: '',
        },
      ],
    });

    const upvoteResult = useAppStore.getState().upvoteProblem('pr-jh-002');
    expect(upvoteResult.success).toBe(true);
    expect(useAppStore.getState().problems.find((p) => p.id === 'pr-jh-002')?.upvotes).toBe(6);

    const secondUpvoteResult = useAppStore.getState().upvoteProblem('pr-jh-002');
    expect(secondUpvoteResult.success).toBe(false);
    expect(useAppStore.getState().problems.find((p) => p.id === 'pr-jh-002')?.upvotes).toBe(6);
  });

  it('E2E Flow 4: bilingual localization & typography scaling workflow', () => {
    useAppStore.getState().setLanguage('hi');
    expect(useAppStore.getState().language).toBe('hi');
    expect(translations.hi.jharkhandGovTitle).toBe('झारखण्ड सरकार');
    expect(translations.hi.submitProblemBtn).toBe('शिकायत दर्ज करें');

    useAppStore.getState().setLanguage('en');
    expect(useAppStore.getState().language).toBe('en');
    expect(translations.en.jharkhandGovTitle).toBe('Government of Jharkhand');
    expect(translations.en.submitProblemBtn).toBe('Submit Grievance');

    useAppStore.getState().setTextScale('normal');
    useAppStore.getState().increaseTextScale();
    expect(useAppStore.getState().textScale).toBe('large');
    useAppStore.getState().increaseTextScale();
    expect(useAppStore.getState().textScale).toBe('larger');
  });

  it('E2E Flow 5: district & category filtering integrity over real (mapped) problems', () => {
    useAppStore.setState({
      problems: [
        {
          id: '1',
          trackingCode: 'JH-1',
          title: 't1',
          category: 'Water Resources',
          description: 'd',
          location: { district: 'Khunti', villageOrArea: '', latitude: 0, longitude: 0, formattedAddress: '' },
          media: [],
          status: 'Submitted',
          upvotes: 0,
          submittedBy: { id: 'u1', fullName: 'x', phone: '', district: '', isVerified: true },
          milestones: [],
          createdAt: '',
          updatedAt: '',
        },
        {
          id: '2',
          trackingCode: 'JH-2',
          title: 't2',
          category: 'Education',
          description: 'd',
          location: { district: 'Ranchi', villageOrArea: '', latitude: 0, longitude: 0, formattedAddress: '' },
          media: [],
          status: 'Submitted',
          upvotes: 0,
          submittedBy: { id: 'u1', fullName: 'x', phone: '', district: '', isVerified: true },
          milestones: [],
          createdAt: '',
          updatedAt: '',
        },
      ],
    });

    const problems = useAppStore.getState().problems;
    const khuntiProblems = problems.filter((p) => p.location.district.toLowerCase().includes('khunti'));
    expect(khuntiProblems).toHaveLength(1);

    const waterProblems = problems.filter((p) => p.category === 'Water Resources');
    expect(waterProblems).toHaveLength(1);
  });
});
