# AutoResume

This app creates a resume and a cover letter tailored to a given job posting and follows your current resume format.

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/).
2. Install pdflatex https://tug.org/applications/pdftex/

3. Clone this repository.

4. Navigate into the project directory:

   ```bash
   $ cd AutoResume
   ```

5. Create a new virtual environment:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

6. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

7. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```
8. Add credits to your OpenAI account if there is not already. [Add credits](https://platform.openai.com)

9. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.

10. Run the app:

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5000](http://localhost:5000)
