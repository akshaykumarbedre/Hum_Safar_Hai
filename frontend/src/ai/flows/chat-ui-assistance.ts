'use server';

/**
 * @fileOverview This file defines a Genkit flow for providing intelligent suggestions and guidance in a chat UI
 * based on user financial data.
 *
 * - chatAssistance - A function that processes user queries and financial data to provide helpful and informative responses.
 * - ChatAssistanceInput - The input type for the chatAssistance function.
 * - ChatAssistanceOutput - The return type for the chatAssistance function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const ChatAssistanceInputSchema = z.object({
  query: z.string().describe('The user query or question.'),
  financialData: z.string().describe('The user financial data in JSON format.'),
});
export type ChatAssistanceInput = z.infer<typeof ChatAssistanceInputSchema>;

const ChatAssistanceOutputSchema = z.object({
  response: z.string().describe('The AI generated response to the user query based on the financial data.'),
});
export type ChatAssistanceOutput = z.infer<typeof ChatAssistanceOutputSchema>;

export async function chatAssistance(input: ChatAssistanceInput): Promise<ChatAssistanceOutput> {
  return chatAssistanceFlow(input);
}

const chatAssistancePrompt = ai.definePrompt({
  name: 'chatAssistancePrompt',
  input: {schema: ChatAssistanceInputSchema},
  output: {schema: ChatAssistanceOutputSchema},
  prompt: `You are a personal financial assistant. Use the provided financial data to answer the user's question in a helpful and informative way. Do not interpret the data yourself, instead respond with suggestions and guidance.

User Query: {{{query}}}

Financial Data: {{{financialData}}}`,
});

const chatAssistanceFlow = ai.defineFlow(
  {
    name: 'chatAssistanceFlow',
    inputSchema: ChatAssistanceInputSchema,
    outputSchema: ChatAssistanceOutputSchema,
  },
  async input => {
    const {output} = await chatAssistancePrompt(input);
    return output!;
  }
);
