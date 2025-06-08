class JWTAuthMiddleware:
    """
    Middleware to handle JWT authentication.
    This middleware checks for the presence of a JWT token in the request headers.
    If the token is valid, it sets the user in the request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       access_token = request.COOKIES.get('access_token')
       if access_token:
           request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
       response = self.get_response(request)
       return response