from telegram import MAX_CAPTION_LENGTH
from telegram.ext import Updater

from core.publisher import BasePublisher

from core.store import IdStore
from .models import Post, Image


class ImgurPublisher(BasePublisher):
    def __init__(self, channel_id: str, updater: Updater, store: IdStore):
        super().__init__(channel_id, updater)
        self.store = store
        self.timeout = 60

    def publish(self, post, *args, **kwargs):
        self.store.save_id(post.id)
        self.logger.debug(post)

        try:
            self.post_album(post)
        except Exception as e:
            self.logger.error(e)

    def post_album(self, post: Post):
        self.post_title(post)

        for image in post.images:
            self.post_image(image, post.is_album)

    def post_title(self, post: Post):
        text = self.format_header(post)
        self.bot.send_message(chat_id=self.channel_id,
                              text=text,
                              disable_web_page_preview=True,
                              timeout=self.timeout)

    def post_image(self, image: Image, is_album):
        text = self.format_caption(image) if is_album else ''
        kwargs = {
            'caption': text,
            'chat_id': self.channel_id,
            'disable_notification': True,
            'timeout': self.timeout,
        }
        if image.animated:
            self.bot.send_video(video=image.url, **kwargs)
        else:
            self.bot.send_photo(photo=image.url, **kwargs)

    def post_single(self, post: Post):
        text = '\n'.join([post.title, post.desc])
        caption = self.cut_text(text)

        image = post.images[0]

        kwargs = {
            'caption': caption,
            'chat_id': self.channel_id,
            'disable_notification': True,
            'timeout': self.timeout,
        }
        if image.animated:
            self.bot.send_video(video=image.url, **kwargs)
        else:
            self.bot.send_photo(photo=image.url, **kwargs)

    def format_header(self, post: Post):
        strings = ['🌚 ' + post.title.strip()]
        if post.is_long:
            strings.append(f'🔥 Album with {post.size} images')
        strings.append('🔗 ' + post.url)
        if post.tags:
            strings.append('🏷 ' + ' '.join(['#' + tag for tag in post.tags]))
        if post.desc:
            strings.append(post.desc)
        text = '\n'.join(strings)
        return self.cut_text(text, limit=400)

    def format_caption(self, image: Image):
        return self.cut_text(image.desc, limit=MAX_CAPTION_LENGTH)

    def cut_text(self, text: str, limit=200):
        if text is None:
            return ''
        elif len(text) > limit:
            text = text[:limit - 5]
            without_last = text.split()[:-1]
            text = ' '.join(without_last)
            return text + '...'
        else:
            return text