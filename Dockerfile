FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY swagger_server ${LAMBDA_TASK_ROOT}
CMD [ "app.handler" ]