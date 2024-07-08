from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        errors = []
        for field, messages in response.data.items():
            if isinstance(messages, list):
                for message in messages:
                    errors.append({
                        "field": field,
                        "message": message
                    })
            else:
                errors.append({
                    "field": field,
                    "message": messages
                })
        return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    return response
