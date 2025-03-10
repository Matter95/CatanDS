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

    def test_exchange(self):
        delete_repo(ROOT_DIR, "Catan_Match")
        delete_repo(REMOTE_DIR, "Catan_Match")

        alice = init_repo(ROOT_DIR, "Catan_Match", "alice", "alice@example.com", False)
        bob = init_repo(REMOTE_DIR, "Catan_Match", "bob", "bob@example.com", False)

        name = get_repo_author_gitdir(bob.git_dir)
        alice.create_remote(name, bob.git_dir)
        print(f"created Remote {name} for {get_repo_author_gitdir(alice.git_dir)}")

        name = get_repo_author_gitdir(alice.git_dir)
        bob.create_remote(name, alice.git_dir)
        print(f"created Remote {name} for {get_repo_author_gitdir(bob.git_dir)}")
