FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY data.py .

COPY generate_pdf.py .

COPY lambda_handler.py .

CMD [ "python", "lambda_handler.py" ]