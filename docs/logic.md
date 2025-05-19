# Calculation Notes

## Basic Personal Amount Phase-out

Both federal and Ontario basic personal amounts decrease once net income
exceeds their respective age amount thresholds. The reduction formula is:

```
adjusted_amount = base_amount - max(0, income - threshold) * rate
```

Where `rate` is 15% federally and 5% provincially. Negative amounts are
clipped at zero.

## OAS Clawback

Old Age Security benefits are included in taxable income. If net income
exceeds the clawback threshold, 15% of the excess is added to tax payable up to
the annual OAS benefit. The engine therefore reports the clawback within the
`total_income_tax` field.
