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
            f"You are an expert job consultant, skilled in crafting long-form, compelling motivation letters that captivate hiring managers and reflect a deep understanding of the company and role. "
            f"Your task is to generate an **energetic, passionate, and highly detailed** motivation letter for the position of '{job_title}' at '{company_name}', with a focus on creating content that will extend to **2 pages** in length. "
            f"Ensure the letter is comprehensive, engaging, and personalized, and follows this expanded structure:\n\n"
            
            f"Start with a **strong opening** that immediately grabs the reader’s attention. Express the applicant’s **genuine passion** for the role and how it aligns with their **personal values** and **career ambitions**. "
            f"Provide more context about why this specific role excites them, including how it ties into their long-term career goals. Connect the applicant’s enthusiasm with the **core values** or **mission of '{company_name}'** to create an emotional resonance that will engage the reader right away. "
            f"Expand this section with more personal reflections to ensure it is rich with enthusiasm and sets the tone for the entire letter.\n"
            
            f"Demonstrate an in-depth understanding of '{company_name}' and its culture. Discuss how the applicant’s career vision and goals align with the company’s long-term objectives and mission. "
            f"Go beyond just stating alignment; show a **passionate commitment** to helping the company grow and succeed. "
            f"Talk about specific initiatives, challenges, or projects the company is currently working on that the applicant is excited to contribute to, ensuring this section feels personalized and tailored to the company’s needs.\n"
            
            f"This is the most detailed section of the letter, where you will showcase the applicant’s **unique strengths, skills**, and **accomplishments**. "
            f"Provide **multiple examples** of measurable achievements (e.g., ‘Increased sales by 40%’ or ‘Led a project that resulted in a 20% boost in efficiency’). "
            f"Illustrate the **direct impact** these achievements had on previous employers, and how they would translate into immediate value for '{company_name}'. Include a wide range of skills (technical, soft skills, leadership) and provide specific metrics or results. Expand on this section to ensure it’s **robust**, highlighting multiple examples with rich detail.\n"
            
            f"Dedicate an extended portion of the letter to showcasing what makes the applicant **uniquely qualified** for this position. "
            f"Explain why the applicant’s **background**, **perspective**, and **personal traits** bring something extra to the table that other candidates might not. Focus on the **unique combination of experiences**, skill sets, and mindset that position the applicant to not only succeed in the role but make a lasting impact on the company. "
            f"Provide examples of situations or challenges where these unique traits have helped the applicant achieve success in previous roles.\n"
            
            f"End the letter by discussing how the applicant sees themselves **contributing to the future success** of '{company_name}'. "
            f"Explain how they plan to make a difference and **exceed expectations** in the role. Be specific in outlining the potential contributions they can make to help the company achieve its future goals. "
            f"Talk about the applicant’s **long-term commitment** to the role and how they envision growing with the company over time. Ensure this section feels **forward-thinking**, emphasizing that the applicant is ready to take on the challenges of the future.\n"
            
            f"Ensure the letter includes relevant **industry-specific keywords** from the job description to improve the chances of passing ATS screening. "
            f"While the tone should remain professional and polished, maintain an **energetic**, **confident**, and **motivated** style throughout. Make sure the letter **flows naturally**, keeping the reader engaged from beginning to end.\n\n"
            
            f"Job Description:\n\n{job_description}\n\n"
            f"Resume Details:\n\n{extracted_resume}\n\n"
            
            f"Generate a **detailed, energetic, and personalized** motivation letter that is **designed to extend to 2 pages**. Ensure the letter is ATS-friendly, full of impact, and showcases the applicant’s deep passion for the role, their alignment with the company, and their ability to make significant contributions."
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


class CoverLetterGenerator:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)

    async def generate_cover_letter(self, extracted_resume, job_title, job_description, company_name):
        """Generates a highly tailored, ATS-optimized cover letter using Google Generative AI."""
        prompt = (
            f"You are a **highly skilled career consultant**, renowned for creating **ATS-optimized, high-impact cover letters** that **grab attention** and **secure interviews**. "
            f"Your task is to generate a **dynamic, tailored** cover letter for the position of '{job_title}' at '{company_name}', ensuring that it is concise, **energetic**, and **persuasive**, while being no longer than **1 page**. "
            f"The cover letter should immediately captivate the hiring manager and clearly convey why the applicant is **the perfect fit** for the role. Structure the letter as follows:\n\n"
            
            f"1. **Compelling and Energized Opening**: Start with an **eye-catching hook** that grabs attention right away. Express the applicant's **enthusiasm** for the role and make a strong connection to the company’s mission or core values. "
            f"Use engaging language that showcases the applicant’s passion and excitement for the opportunity at '{company_name}'. Make the opening **vibrant** and memorable.\n\n"
            
            f"2. **Why This Role & Company?**: Demonstrate why the applicant is **uniquely qualified** for this role and why they are passionate about working at '{company_name}'. "
            f"Showcase your understanding of the company’s **culture, values**, and **goals**, and explain how the applicant’s skills, personality, and career aspirations align perfectly with the company’s needs. "
            f"Be enthusiastic and specific about what makes the company and the role a **perfect match**.\n\n"
            
            f"3. **Key Skills, Achievements & Results**: Highlight **3-4 key skills** and provide **impactful, quantifiable examples** from the applicant’s resume. "
            f"Use **action verbs** and **specific metrics** (e.g., ‘Increased productivity by 30%’, ‘Led a project team of 12 to achieve X result’) to show how the applicant has achieved success in previous roles. "
            f"Focus on **outcomes and impact** that demonstrate the applicant's potential to drive immediate value at '{company_name}'.\n\n"
            
            f"4. **Powerful Closing & Call to Action**: Conclude with a **strong, confident closing** that reiterates the applicant’s eagerness to contribute to the company’s success. "
            f"Express your excitement about discussing how the applicant’s skills align with the role and make an impact. Include a clear **call to action** and express your **availability** for an interview. "
            f"End with a note of **gratitude** for considering the application, and ensure the tone is upbeat and inviting.\n\n"
            
            f"**Additional Instructions:**\n"
            f"- Ensure the cover letter includes **action verbs** and **ATS-friendly keywords** to maximize chances of passing ATS screening.\n"
            f"- Keep the letter **concise** but impactful, ensuring it fits within **1 page** while maintaining a **professional yet engaging tone**.\n\n"
            
            f"Job Description:\n{job_description}\n\n"
            f"Resume Details:\n{extracted_resume}\n\n"
            f"Generate a **high-energy**, **compelling** cover letter that will leave a lasting impression on the hiring manager, perfectly matching the applicant’s skills to the role and company’s goals."
        )

        try:
            response = await self._generate_with_google_ai(prompt)
            return response

        except Exception as e:
            print("Error Traceback:", traceback.format_exc())
            return f"Error generating cover letter: {str(e)}"
    
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
