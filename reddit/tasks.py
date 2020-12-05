import datetime
import logging
from praw.models import Submission, Comment

from .models import Subreddit, RemovalAction, RemovedPost
from behave.celery import celery_app

logger = logging.getLogger(__name__)


@celery_app.task()
def process_active_subs():
    for subreddit in Subreddit.objects.filter(active=True):
        process_flair_actions(subreddit)


def process_flair_actions(subreddit: Subreddit):
    for flair_action in get_flair_actions_for_sub(subreddit):
        process_flair_action(subreddit, flair_action)


def process_flair_action(subreddit, flair_action):
    submission_id = id_from_target_fullname(flair_action.target_fullname)
    submission = subreddit.reddit_api.submission(id=submission_id)

    if not RemovedPost.objects.filter(submission_id=submission_id) and not submission.link_flair_text:
        return

    post_removal, is_new = RemovedPost.objects.get_or_create(
        submission_id=submission_id,
        defaults={
            'subreddit': subreddit,
            'author': submission.author.name,
            'post_url': submission.url,
            'post_title': submission.title
        }
    )

    if not is_new and submission.link_flair_text == post_removal.flair_text_set:
        return

    if not is_new and submission.link_flair_text != post_removal.flair_text_set and post_removal.removal_comment_id:
        delete_removal_comment(subreddit, post_removal)
        approve_post(submission)
        post_removal.delete()
        logger.warning("Deleted removal comment for post {submission}".format(submission=submission))
        return

    if submission.link_flair_text:
        try:
            removal_action = RemovalAction.objects.get(flair_text=submission.link_flair_text)
        except RemovalAction.DoesNotExist:
            logger.warning("Post {post_url} marked with unknown flair: \"{flair_text}\"".format(
                post_url=submission.shortlink,
                flair_text=submission.link_flair_text
            ))
            return

        removal_comment = post_removal_comment(submission, removal_action)

        if removal_action.lock_post:
            submission.mod.lock()

        if removal_action.ban_duration > 0:
            ban_user(subreddit, submission, removal_action)

        remove_post(submission)

        post_removal.removal_comment_id = removal_comment.id

    post_removal.removal_date = datetime.datetime.utcnow()
    post_removal.flair_text_set = submission.link_flair_text
    post_removal.save()

    logger.warning("Processed flagged post {submission}".format(
        submission=submission
    ))


def remove_post(submission: Submission):
    submission.mod.remove()


def approve_post(submission: Submission):
    submission.mod.approve()


def post_removal_comment(submission: Submission, removal_action: RemovalAction) -> Comment:
    message = ""

    if removal_action.use_default_ban_message:
        message = removal_action.subreddit.default_ban_message
    else:
        if removal_action.use_comment_reply_prefix:
            message += removal_action.subreddit.comment_reply_prefix + "\n\n"

        message += message

        if removal_action.use_comment_reply_suffix:
            message += "\n\n" + removal_action.subreddit.comment_reply_suffix

    message.format(submission)

    removal_comment = submission.reply(message)

    removal_comment.mod.approve()
    removal_comment.mod.distinguish(how="yes", sticky=True)

    return removal_comment


def delete_removal_comment(subreddit: Subreddit, post_removal):
    removal_comment = Comment(id=post_removal.removal_comment_id, reddit=subreddit.reddit_api)
    removal_comment.delete()

    post_removal.removal_comment_id = None
    post_removal.save()


def ban_user(subreddit: Subreddit, submisssion: Submission, removal_action: RemovalAction) -> None:
    subreddit.api.banned.add(
        redditor=submisssion.author,
        duration=removal_action.ban_duration,
        ban_message=removal_action.ban_message,
        ban_reason=removal_action.ban_reason,
        note=removal_action.ban_note
    )


def get_flair_actions_for_sub(subreddit: Subreddit):
    for mod_action in subreddit.api.mod.log(action='editflair', limit=10):
        if mod_action.details == "flair_edit":
            yield mod_action


def id_from_target_fullname(target_fullname):
    return target_fullname[3:]
