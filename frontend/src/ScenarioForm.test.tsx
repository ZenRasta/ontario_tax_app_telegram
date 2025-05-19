import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ScenarioForm, { ScenarioFormData } from './ScenarioForm';

test('dynamic fields toggle and JSON serialises', async () => {
  const user = userEvent.setup();
  const handleSubmit = jest.fn();
  render(<ScenarioForm onSubmit={handleSubmit} />);

  expect(screen.queryByTestId('spouse-age')).toBeNull();
  await user.click(screen.getByTestId('spouse-checkbox'));
  expect(screen.getByTestId('spouse-age')).toBeInTheDocument();

  expect(screen.queryByTestId('ceiling')).toBeNull();
  await user.click(screen.getByTestId('params-checkbox'));
  expect(screen.getByTestId('ceiling')).toBeInTheDocument();

  await user.type(screen.getByTestId('spouse-age'), '63');
  await user.type(screen.getByTestId('ceiling'), '92000');
  await user.click(screen.getByText(/submit/i));

  const expected: ScenarioFormData = {
    includeSpouse: true,
    spouseAge: 63,
    overrideParams: true,
    bracketFillCeiling: 92000,
  };
  expect(handleSubmit).toHaveBeenCalledWith(expected);
});
