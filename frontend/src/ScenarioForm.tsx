import React, { useState } from 'react';

export interface ScenarioFormData {
  includeSpouse: boolean;
  spouseAge?: number;
  overrideParams: boolean;
  bracketFillCeiling?: number;
}

export default function ScenarioForm({ onSubmit }: { onSubmit?: (d: ScenarioFormData) => void }) {
  const [includeSpouse, setIncludeSpouse] = useState(false);
  const [spouseAge, setSpouseAge] = useState('');
  const [overrideParams, setOverrideParams] = useState(false);
  const [ceiling, setCeiling] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data: ScenarioFormData = {
      includeSpouse,
      overrideParams,
      ...(includeSpouse ? { spouseAge: Number(spouseAge) } : {}),
      ...(overrideParams ? { bracketFillCeiling: Number(ceiling) } : {}),
    };
    onSubmit?.(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        <input
          type="checkbox"
          data-testid="spouse-checkbox"
          checked={includeSpouse}
          onChange={(e) => setIncludeSpouse(e.target.checked)}
        />
        Include spouse
      </label>
      {includeSpouse && (
        <input
          type="number"
          data-testid="spouse-age"
          value={spouseAge}
          onChange={(e) => setSpouseAge(e.target.value)}
          placeholder="Spouse Age"
        />
      )}
      <label>
        <input
          type="checkbox"
          data-testid="params-checkbox"
          checked={overrideParams}
          onChange={(e) => setOverrideParams(e.target.checked)}
        />
        Override params
      </label>
      {overrideParams && (
        <input
          type="number"
          data-testid="ceiling"
          value={ceiling}
          onChange={(e) => setCeiling(e.target.value)}
          placeholder="Bracket Ceiling"
        />
      )}
      <button type="submit">Submit</button>
    </form>
  );
}
