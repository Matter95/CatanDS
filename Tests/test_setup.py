from unittest import TestCase

from git import Repo, repo

from repo_utils import (
    init_repo,
    fetch_all_remotes,
    get_repo_author_gitdir,
    repo_remote_merge
)
from test_utils import onerror, delete_repo, create_post_text, create_comment_text
from definitions import ROOT_DIR, REMOTE_DIR


class TestBlogFunctions(TestCase):

    def test_creation(self):
        repo_path = ROOT_DIR
        remote_path = REMOTE_DIR
        delete_repo(repo_path, "Blog_Sites_Alice")
        delete_repo(remote_path, "Blog_Sites_Bob")

        alice = init_repo(repo_path, "Blog_Sites_Alice", "Alice", "alice@example.com", False)

        email = "alice@example.com"
        blog_title = "Example Blog"
        # create a blog
        create_blog(alice, blog_title, email)
        create_blog(alice, "Another Blog", email)
        create_post(alice, f"Alice's Post", email, blog_title, create_post_text(2))
        update_blogs(alice)

        create_post(alice, f"Alice's Post", email, blog_title, create_post_text(5))
        create_comment(alice, f"Comment1", "Alice", email, "Alice's Post", "Alice", create_comment_text(2))
        create_comment(alice, f"Comment2", "Bob", "bob@example.com", "Alice's Post", "Alice", create_comment_text(4))
        update_blogs(alice)

        create_comment(alice, f"Comment1", "Alice", email, "Alice's Post", "Alice", create_comment_text(5))
        update_blogs(alice)

    def test_exchange(self):
        repo_path = ROOT_DIR
        remote_path = REMOTE_DIR
        delete_repo(repo_path, "Blog_Sites_Alice")
        delete_repo(remote_path, "Blog_Sites_Bob")

        alice = init_repo(repo_path, "Blog_Sites_Alice", "alice", "alice@example.com", False)
        bob = init_repo(remote_path, "Blog_Sites_Bob", "bob", "bob@example.com", False)

        name = get_repo_author_gitdir(bob.git_dir)
        alice.create_remote(name, bob.git_dir)
        print(f"created Remote {name} for {get_repo_author_gitdir(alice.git_dir)}")

        name = get_repo_author_gitdir(alice.git_dir)
        bob.create_remote(name, alice.git_dir)
        print(f"created Remote {name} for {get_repo_author_gitdir(bob.git_dir)}")

        email = "alice@example.com"
        blog_title = "Example Blog"
        # create a blog
        create_blog(alice, blog_title, email)
        create_blog(alice, "The Blog", email)
        create_blog(alice, "Another Blog", email)
        create_post(alice, f"Alice's Post", email, blog_title, create_post_text(2))
        update_blogs(alice)

        email = "bob@example.com"
        blog_title = "Bob's First Blog"
        # create a blog
        create_blog(bob, blog_title, email)
        create_post(bob, f"Post One", email, blog_title, create_post_text(1))
        create_post(bob, f"Post Two", email, blog_title, create_post_text(2))
        create_comment(bob, f"Bob's Comment One", "Bob", email, "Post One", "Bob", create_comment_text(3))
        create_comment(bob, f"Bob's Comment Two", "Bob", "bob@example.com", "Post Two", "Bob", create_comment_text(1))
        update_blogs(bob)
        fetch_all_remotes(alice)

        repo_remote_merge(alice)
        alice.git.checkout('Blog_Sites_Bob')
        create_comment(alice, f"Alice's Comment One", "Alice", "bob@example.com", "Post Two", "Bob", create_comment_text(3))

        fetch_all_remotes(bob)
        repo_remote_merge(bob)
        update_blogs(bob)

        fetch_all_remotes(alice)
