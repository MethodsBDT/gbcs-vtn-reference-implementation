FROM public.ecr.aws/lambda/python:3.9
# TODO: Build image on ARM64
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}
CMD [ "app.handler" ]