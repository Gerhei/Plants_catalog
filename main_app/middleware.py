from django.utils.deprecation import MiddlewareMixin


class ForumUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user
        try:
            forumuser = user.forumusers
        except AttributeError:
            forumuser = None
        request.forumuser = forumuser
