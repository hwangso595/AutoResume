import os
from latex import build_pdf
from contextlib import suppress

import openai
import json
from flask import Flask, redirect, render_template, request, url_for, send_from_directory

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
app.config.from_file("./config.json", load=json.load)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        error = ''
        if "resume" not in request.form or "posting" not in request.form:
            error = "Please fill out both the resume and job posting."
            return redirect(url_for("index", error=error))
        old_resume = request.form["resume"]
        old_resume_split = old_resume.split(app.config['DELIMITER'])
        to_edit = old_resume_split[1]
        if len(old_resume_split) != 3:
            error = "Please split the text into delemiters."
            return redirect(url_for("index", error=error))
        job_posting = request.form["posting"]
        response1 = openai.ChatCompletion.create(
            model=app.config["GPT_MODEL"],
            messages=[{"role": "user", "content": generate_resume_prompt(
                to_edit, job_posting)}]
        )
        edited_snippet = response1["choices"][0]["message"]["content"]
        coverletter = ""
        if request.form.get('generate-cl'):
            cl_prompt = request.form["cl-prompt"]
            response2 = openai.ChatCompletion.create(
                model=app.config["GPT_MODEL"],
                messages=[{"role": "user", "content": generate_coverletter_prompt(
                edited_snippet, job_posting, cl_prompt)}]
            )
            print(response2)
            coverletter = response2["choices"][0]["message"]["content"]
        new_resume = "\n".join([old_resume_split[0], edited_snippet, old_resume_split[2]])
        return redirect(url_for("index", base_resume=old_resume, resume=new_resume, coverletter=coverletter, error=error))

    base_resume = request.args.get("base_resume")
    resume = request.args.get("resume")
    coverletter = request.args.get("coverletter")
    return render_template("index.html", base_resume=base_resume, resume=resume, coverletter=coverletter)


@app.route("/resume", methods=["POST", "GET"])
def download_resume():
    if request.method == "POST":
        i = 0
        while os.path.exists(os.path.join('static', 'resumes', f'resume{i}.pdf')):
            i += 1
        latex = request.form.get('resume')
        with open(os.path.join('static', 'resumes', f'resume{i}.tex'), 'w', newline='') as f:
            f.write(latex)
        pdf = build_pdf(latex)
        pdf.save_to(os.path.join('static', 'resumes', f'resume{i}.pdf'))
        with suppress(FileNotFoundError):
            os.unlink(os.path.join('static', 'resumes', f'resume{i}.tex'))
        with suppress(FileNotFoundError):
            os.unlink(os.path.join('static', 'resumes', f'resume{i}.log'))
        with suppress(FileNotFoundError):
            os.unlink(os.path.join('static', 'resumes', f'resume{i}.aux'))
        with suppress(FileNotFoundError):
            os.unlink(os.path.join('static', 'resumes', f'resume{i}.out'))
    i = 0
    while os.path.exists(os.path.join('static', 'resumes', f'resume{i}.pdf')):
        i += 1
    return send_from_directory(os.path.join('static', 'resumes'), f'resume{i-1}.pdf')

def generate_resume_prompt(current_resume, job_posting):
    return f"""Given the resume and job posting, rewrite the resume based on those critiques using the formatting provided by the original resume, such that the recruiter from that company would hire you.
Here are some guidelines you should follow
- encorporate key words from the job posting
- avoid vague buzzwords
- add as much details and metrics as possible
- don't add additional sections like name or work experience
- don't add elements in the skills section if it is not referenced in one of the work experiences. You may add skills if they you reference them in one of the experiences in the resume.
- emballish if necessary

Resume:
{current_resume}

Job posting:
{job_posting}

Write new resume snippet here:"""


def generate_coverletter_prompt(current_resume, job_posting, cl_prompt,
word_count=app.config["CL_LENGTH"],):
    guidelines = """
- IMPORTANT: be very excited and highly enthused
- try to be as specific as possible
- avoid vague buzzwords
- if possible, research the company and encorporate their values
- encorporate literary devices but don't overdo it
- encorporate key words from the job posting
- have high degree of perplexity and robustness
- tell a personal story and relate it to the job or company
"""
    result = f""" Given the resume, job posting, and prompt, write a {word_count} word cover letter for this job that answers the prompt. The resume is written in latex.
Here are some guidelines you should follow
{guidelines}

Resume:
{current_resume}

Job posting:
{job_posting}

prompt:
{cl_prompt}""" if cl_prompt else f""" Given the resume and job posting, write a {word_count} word cover letter for this job that answers the prompt. The resume is written in latex.
Here are some guidelines you should follow
{guidelines}

Resume:
{current_resume}

Job posting:
{job_posting}"""
    return result + "\n\nWrite cover letter here:"
