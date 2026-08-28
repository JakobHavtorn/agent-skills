# Test Cases: taxhelper

## Should trigger

1. "What does rubrik 51 cover in my årsopgørelse?"
2. "Look up field 417 on my tax assessment"
3. "Generate a review worksheet for my Danish tax return"
4. "Can I get kørselsfradrag for my commute to Aarhus?"
5. "Search for rules about renteudgifter in the tax database"

## Should NOT trigger

1. "How do I file my US taxes?" — not Danish tax, outside scope
2. "What's the VAT rate in Denmark?" — business tax, not personal assessment
3. "Calculate my tax refund" — the skill does not give personalized tax advice

## Expected behavior

- Uses MCP tools if a taxhelper MCP server is configured, otherwise falls back to CLI
- Resolves rubrik/field references before writing explanations
- Includes rubrik/felt number, year, lock/blanket status, and source URL in answers
- States uncertainty clearly when retrieved data is incomplete
- Never presents retrieved text as personalized tax advice
- Does not invent thresholds, rates, deadlines, or source URLs
- For PDF flow: generates a worksheet first, then fills a local copy only from explicit values
- Reminds that official Skattestyrelsen/TastSelv systems are authoritative
