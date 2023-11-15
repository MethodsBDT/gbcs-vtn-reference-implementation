FROM public.ecr.aws/lambda/python:3.9

#COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY * /usr/src/app
RUN pip install -r requirements.txt
CMD [ "app.handler" ]