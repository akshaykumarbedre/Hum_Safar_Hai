'use server';

/**
 * @fileOverview Generates specific, measurable, and achievable financial goals based on a high-level goal provided by the user.
 *
 * - generateFinancialGoalIdeas - A function that generates financial goal ideas.
 * - GenerateFinancialGoalIdeasInput - The input type for the generateFinancialGoalIdeas function.
 * - GenerateFinancialGoalIdeasOutput - The return type for the generateFinancialGoalIdeas function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateFinancialGoalIdeasInputSchema = z.object({
  highLevelGoal: z
    .string()
    .describe('A high-level financial goal (e.g., retirement, buying a house).'),
});
export type GenerateFinancialGoalIdeasInput = z.infer<
  typeof GenerateFinancialGoalIdeasInputSchema
>;

const GenerateFinancialGoalIdeasOutputSchema = z.object({
  financialGoals: z
    .array(z.string())
    .describe('A list of specific, measurable, and achievable financial goals.'),
});
export type GenerateFinancialGoalIdeasOutput = z.infer<
  typeof GenerateFinancialGoalIdeasOutputSchema
>;

export async function generateFinancialGoalIdeas(
  input: GenerateFinancialGoalIdeasInput
): Promise<GenerateFinancialGoalIdeasOutput> {
  return generateFinancialGoalIdeasFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generateFinancialGoalIdeasPrompt',
  input: {schema: GenerateFinancialGoalIdeasInputSchema},
  output: {schema: GenerateFinancialGoalIdeasOutputSchema},
  prompt: `You are a personal finance expert. Generate a list of specific, measurable, and achievable financial goals related to the following high-level goal:

High-Level Goal: {{{highLevelGoal}}}

Financial Goals:`,
});

const generateFinancialGoalIdeasFlow = ai.defineFlow(
  {
    name: 'generateFinancialGoalIdeasFlow',
    inputSchema: GenerateFinancialGoalIdeasInputSchema,
    outputSchema: GenerateFinancialGoalIdeasOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
