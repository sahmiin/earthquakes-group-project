FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

RUN dnf install -y \
    gcc \
    gcc-c++ \
    make \
    cairo-devel \
    pango-devel \
    freetype-devel \
    libjpeg-turbo-devel \
    giflib-devel \
    pkg-config \
    cmake \
    && dnf clean all

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY logo.png .

COPY index.html .

COPY data.py .

COPY generate_pdf.py .

COPY ses_helper.py .

COPY report.py .

CMD ["report.handler"]