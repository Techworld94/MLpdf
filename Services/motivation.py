import os
from dotenv import load_dotenv
import asyncio
import google.generativeai as genai
import traceback

load_dotenv()

class MotivationLetterGenerator:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)

    async def generate_motivation_letter(self, extracted_resume, job_title, job_description, company_name):
        """Generates an ATS-friendly and interview-winning motivation letter using Google Generative AI."""
        prompt = (
            f"You are a professional job consultant and an expert in crafting ATS-friendly documents. "
            f"Generate a compelling and professional motivation letter tailored for the position of '{job_title}' "
            f"at '{company_name}'. This letter should make the applicant stand out and increase their chances of getting an interview. "
            f"Focus on the following aspects:\n\n"
            
            f"1. **Introduction**: Start with a strong opening sentence that reflects the applicant's enthusiasm for the role and highlights their alignment with the company's values.\n"
            f"2. **Personalization**: Incorporate details from the job description and company mission to demonstrate a deep understanding of the role and organization.\n"
            f"3. **Key Skills and Achievements**: Highlight specific skills, accomplishments, and experiences from the resume that directly match the job description.\n"
            f"4. **Value Proposition**: Clearly articulate how the applicant's expertise and background can contribute to the company's success.\n"
            f"5. **Professional Tone and ATS Optimization**: Use industry-relevant keywords from the job description to ensure the letter passes ATS screening. "
            f"Keep the tone professional and confident.\n\n"
            
            f"The job description is as follows:\n\n{job_description}\n\n"
            f"The resume text is as follows:\n\n{extracted_resume}\n\n"
            f"Ensure the final output is polished, concise, and ready for submission."
        )

        try:
            response = await self._generate_with_google_ai(prompt)
            return response

        except Exception as e:
            print("Error Traceback:", traceback.format_exc())
            return f"Error generating motivation letter: {str(e)}"
    
    async def _generate_with_google_ai(self, prompt):
        """Helper function to send a prompt to Google Generative AI and receive the response."""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = await asyncio.to_thread(
                model.generate_content,
                prompt
            )
            return response.text 

        except Exception as e:
            raise ValueError(f"Google Generative AI request failed: {str(e)}")