from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import poster
from . import tasks
from .models import Post
from .publisher import publish_post
from .serializers import PostSerializer, PostUpdateSerializer


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request):
    return poster(tasks.fetch_and_publish)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    return poster(lambda: tasks.fetch_and_publish(force=True, blank=True))


@api_view()
@permission_classes([IsAdminUser])
def index(request: Request):
    return render(request, 'reddit/index.html')


class PostViewMixin(generics.GenericAPIView):
    def get_queryset(self):
        qs = Post.objects.filter(status=Post.STATUS_PENDING,
                                 subreddit__on_moderation=True)
        qs = qs.order_by('-created')
        return qs


class PendingPostListView(PostViewMixin, generics.ListAPIView):
    serializer_class = PostSerializer


class PostView(PostViewMixin, generics.UpdateAPIView):
    queryset = PostUpdateSerializer

    def update(self, request: Request, *args, **kwargs):
        post = self.get_object()
        s = self.get_serializer(request.data)  # type: PostUpdateSerializer
        s.is_valid(raise_exception=True)
        accepted = s.get('accepted')
        if accepted:
            post.status = Post.STATUS_ACCEPTED
            post.save()
            publish_post(post)
        else:
            post.status = Post.STATUS_REJECTED
            post.save()
        return Response({
            'accepted': accepted,
        })
