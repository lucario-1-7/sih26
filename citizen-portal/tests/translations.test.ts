import { describe, it, expect } from 'vitest';
import { translations } from '../src/lib/translations';

describe('Translations Dictionaries', () => {
  it('should have both English (en) and Hindi (hi) dictionaries defined', () => {
    expect(translations.en).toBeDefined();
    expect(translations.hi).toBeDefined();
  });

  it('should have exact key parity between English and Hindi', () => {
    const enKeys = Object.keys(translations.en).sort();
    const hiKeys = Object.keys(translations.hi).sort();

    expect(enKeys).toEqual(hiKeys);
  });

  it('should not contain any empty strings in English translations', () => {
    Object.entries(translations.en).forEach(([key, value]) => {
      expect(value, `Key "${key}" in English should not be empty`).toBeTruthy();
      expect(typeof value).toBe('string');
    });
  });

  it('should not contain any empty strings in Hindi translations', () => {
    Object.entries(translations.hi).forEach(([key, value]) => {
      expect(value, `Key "${key}" in Hindi should not be empty`).toBeTruthy();
      expect(typeof value).toBe('string');
    });
  });

  it('should contain the updated "Submit Grievance" translations', () => {
    expect(translations.en.submitProblemBtn).toBe('Submit Grievance');
    expect(translations.hi.submitProblemBtn).toBe('शिकायत दर्ज करें');
  });

  it('should contain Government of Jharkhand titles in both languages', () => {
    expect(translations.en.jharkhandGovTitle).toBe('Government of Jharkhand');
    expect(translations.hi.jharkhandGovTitle).toBe('झारखण्ड सरकार');
  });
});
