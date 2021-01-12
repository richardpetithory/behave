import datetime
import logging
from praw.models import Submission, Comment

from .models import Subreddit, RemovalAction, RemovedPost
from behave.celery import celery_app

logger = logging.getLogger(__name__)


@celery_app.task()
def process_active_subs():
    logger.warning("Processing active subs")

    for subreddit in Subreddit.objects.filter(active=True):
        process_flair_actions(subreddit)


def process_flair_actions(subreddit: Subreddit):
    logger.warning("Processing flairs for sub {subreddit}".format(subreddit=subreddit))

    for flair_action in get_flair_actions_for_sub(subreddit):
        process_flair_action(subreddit, flair_action)


def get_submission_by_id(subreddit: Subreddit, submission_id):
    return subreddit.reddit_api.submission(id=submission_id)


def process_flair_action(subreddit, flair_action):
    submission_id = id_from_target_fullname(flair_action.target_fullname)
    submission = get_submission_by_id(subreddit, submission_id)

    if not RemovedPost.objects.filter(submission_id=submission_id) and not submission.link_flair_text:
        logger.warning("Skipping because no previous log entry found and no flair text set")
        return

    post_removal, is_new = RemovedPost.objects.get_or_create(
        submission_id=submission_id,
        defaults={
            'subreddit': subreddit,
            'author': getattr(submission.author, "name", "<deleted>"),
            'post_url': submission.url,
            'post_title': submission.title,
            'post_body': submission.selftext,
        }
    )

    if not is_new and submission.link_flair_text == post_removal.flair_text_set:
        logger.warning("Skipping because previous log entry found but flair text has not changed")
        return

    if not is_new and submission.link_flair_text != post_removal.flair_text_set and post_removal.removal_comment_id:
        if not subreddit.read_only:
            delete_removal_comment(subreddit, post_removal)
            approve_post(submission)

        post_removal.delete()
        logger.warning("Deleted removal comment for post {submission}".format(submission=submission))
        return

    if submission.link_flair_text:
        try:
            removal_action = RemovalAction.objects.get(
                subreddit=subreddit,
                flair_text=submission.link_flair_text
            )
        except RemovalAction.DoesNotExist:
            logger.warning("Post {post_url} marked with unknown flair: \"{flair_text}\"".format(
                post_url=submission.shortlink,
                flair_text=submission.link_flair_text
            ))
            return

        if not subreddit.read_only:
            removal_comment = post_removal_comment(submission, removal_action)

            if removal_action.lock_post:
                submission.mod.lock()

            if removal_action.ban_duration > 0:
                try:
                    send_ban_message(subreddit, submission)
                    ban_user(subreddit, submission, removal_action)
                except Exception as e:
                    logger.warning("Error banning user: {error}".format(error=e))

            remove_post(submission)

            post_removal.removal_comment_id = removal_comment.id

        post_removal.removal_action = removal_action

    post_removal.removal_date = datetime.datetime.utcnow()
    post_removal.flair_text_set = submission.link_flair_text
    post_removal.save()

    logger.warning("Processed flagged post {submission}".format(
        submission=submission
    ))


def send_ban_message(subreddit: Subreddit, submission: Submission):
    author_name = str(submission.author)

    logger.warning("Sending ban message to {user}".format(user=author_name))

    message = subreddit.default_ban_message.format(submission)

    redditor = subreddit.reddit_api.redditor(author_name)
    redditor.message(subreddit.default_ban_message_subject, message)


def remove_post(submission: Submission):
    submission.mod.remove()


def approve_post(submission: Submission):
    submission.mod.approve()


def post_removal_comment(submission: Submission, removal_action: RemovalAction) -> Comment:
    message = ""

    if removal_action.use_comment_reply_prefix:
        message += removal_action.subreddit.comment_reply_prefix + "\n\n"

    message += removal_action.comment_reply

    if removal_action.use_comment_reply_suffix:
        message += "\n\n" + removal_action.subreddit.comment_reply_suffix

    message = message.format(submission)

    removal_comment = submission.reply(message)

    removal_comment.mod.approve()
    removal_comment.mod.distinguish(how="yes", sticky=True)

    return removal_comment


def delete_removal_comment(subreddit: Subreddit, post_removal):
    logger.warning("Deleting removal comment {post_id}".format(post_id=post_removal.removal_comment_id))

    removal_comment = Comment(id=post_removal.removal_comment_id, reddit=subreddit.reddit_api)
    removal_comment.delete()

    post_removal.removal_comment_id = None
    post_removal.save()


def ban_user(subreddit: Subreddit, submisssion: Submission, removal_action: RemovalAction) -> None:
    author_name = str(submisssion.author)

    logger.warning("Banning user {author_name}".format(author_name=author_name))

    ban_messsage = removal_action.ban_message.format(submisssion)
    ban_note = removal_action.ban_note.format(submisssion)

    subreddit.api.banned.add(
        redditor=author_name,
        duration=removal_action.ban_duration,
        ban_message=ban_messsage,
        ban_reason=removal_action.ban_reason,
        note=ban_note
    )


def get_flair_actions_for_sub(subreddit: Subreddit):
    return [
        mod_action
        for mod_action
        in list(subreddit.api.mod.log(action='editflair', limit=5))
        if mod_action.details == "flair_edit"
    ]


def id_from_target_fullname(target_fullname):
    return target_fullname[3:]
