'use server';

/**
 * @fileOverview A flow for analyzing spending data and providing insights.
 *
 * - analyzeSpending - A function that handles the spending analysis process.
 * - AnalyzeSpendingInput - The input type for the analyzeSpending function.
 * - AnalyzeSpendingOutput - The return type for the analyzeSpending function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AnalyzeSpendingInputSchema = z.object({
  spendingData: z
    .string()
    .describe(
      'Spending data in JSON format.  Each entry should have a category, amount, and date.'
    ),
});
export type AnalyzeSpendingInput = z.infer<typeof AnalyzeSpendingInputSchema>;

const AnalyzeSpendingOutputSchema = z.object({
  summary: z.string().describe('A summary of the spending analysis.'),
  insights: z.array(z.string()).describe('Specific insights and suggestions.'),
});
export type AnalyzeSpendingOutput = z.infer<typeof AnalyzeSpendingOutputSchema>;

export async function analyzeSpending(input: AnalyzeSpendingInput): Promise<AnalyzeSpendingOutput> {
  return analyzeSpendingFlow(input);
}

const prompt = ai.definePrompt({
  name: 'analyzeSpendingPrompt',
  input: {schema: AnalyzeSpendingInputSchema},
  output: {schema: AnalyzeSpendingOutputSchema},
  prompt: `You are a personal finance advisor. Analyze the following spending data and provide a summary of spending habits and insights, including areas of overspending and suggestions for saving money.

Spending Data:
{{spendingData}}`,
});

const analyzeSpendingFlow = ai.defineFlow(
  {
    name: 'analyzeSpendingFlow',
    inputSchema: AnalyzeSpendingInputSchema,
    outputSchema: AnalyzeSpendingOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
