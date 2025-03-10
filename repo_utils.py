import os.path

import git
from git import Repo


def get_commit_id_from_ref(ref: str) -> str:
    """
    returns the commit hash of the given ref
    :param ref: reference with the commit hash at the end
    :return: hexsha of the commit
    """
    index = ref.rfind("/")
    return ref[index + 1:]


def get_all_commit_ids_with_path(repo: git.Repo, path: str, additional: str = "") -> [str]:
    """
    returns git show-ref grep "path"
    :param repo: the repo we work in
    :param path: the path that should be in the reference
    :param additional: additional string to check for with 'in' operator
    :return: all references with path
    """
    refs = []
    if repo.references == ():
        return []
    else:
        for ref in repo.references:
            if ref.path.startswith(path) and additional in ref.path:
                refs.append(get_commit_id_from_ref(ref.name))
    return refs


def init_repo(path: str, repo_name: str, author: str, email: str, bare: bool) -> git.Repo:
    """
    initialize a git repository with the given path and name
    :param path: directory to create the repository in
    :param repo_name: repository name
    :param author: author's name
    :param email: author's email
    :param bare: create bare or non-bare repository
    :return: git.Repo object
    """
    if bare:
        # do not create master branch
        repo = Repo.init(f"{path}/{repo_name}", initial_branch=f"{repo_name}", bare=True)
    else:
        # do not create master branch
        repo = Repo.init(f"{path}/{repo_name}", initial_branch=f"{repo_name}")

    author = git.Actor(author, email)
    empty_tree = repo.index.write_tree()

    initial_commit = repo.index.commit(
        "initial commit",
        [],
        True,
        author,
        author,
    )

    print(f"Repository {repo_name} created\n with latest commit: {initial_commit}\n and tree id: {empty_tree}")

    return repo


def create_repos_with_remotes(repo_names: [str], path: str, bare: bool):
    """
    creates repos that are all linked together by remotes, given their names
    :param repo_names: the repo and remote names
    :param path: repo path of creation
    :param bare: option of repo initialization flag
    :return:
    """
    if bare:
        return create_repos_with_remotes_bare(repo_names, path)
    else:
        return create_repos_with_remotes_non_bare(repo_names, path)


def get_repo_name_workdir(workdir_url: str):
    """
    returns the name of the repository given the git working directory
    :param workdir_url: the git working directory of a repo
    :return: name of the repository
    """
    slash_ind = workdir_url[0:len(workdir_url) - 1].rfind(os.path.sep)
    name = workdir_url[slash_ind + 1:len(workdir_url)]
    return name


def get_repo_name_gitdir(git_dir: str):
    """
    returns the name of the repository given the git directory
    :param git_dir: the git directory of a repo
    :return: name of the repository
    """
    slash_ind = git_dir[0:len(git_dir) - 6].find("Blog_Sites_")
    name = git_dir[slash_ind:len(git_dir) - 5]
    return name


def get_repo_author_gitdir(git_dir: str):
    """
    returns the author name given the git directory
    :param git_dir: the git directory of a repo
    :return: name of the author
    """
    slash_ind = git_dir[0:len(git_dir) - 6].find("Catan_")
    author = git_dir[slash_ind + len("Catan_"):len(git_dir) - 5]
    return author


def create_repos_with_remotes_bare(repo_names: [str], path: str):
    """
    creates a list of repos that are bare
    :param repo_names: the names of the repos to create
    :param path: the path where we create the repos
    :return:
    """
    repos = []

    # initialize repository
    for name in repo_names:
        repos.append(init_repo(path, name, name, "random@example.com", True))

    # create remotes
    for repo in repos:
        for remote in repos:
            # skip self
            if remote.working_dir != repo.working_dir:
                name = get_repo_name_workdir(remote.working_dir)
                repo.create_remote(name, remote.git_dir)
                print(f"created Remote /refs/remote/{name} for {get_repo_name_workdir(repo.working_dir)}")
    return repos


def create_repos_with_remotes_non_bare(repo_names: [str], path: str):
    """
    creates a list of repos that are non-bare
    :param repo_names: the names of the repos to create
    :param path: the path where we create the repos
    :return:
    """
    repos = []

    # initialize repository
    for name in repo_names:
        repos.append(init_repo(path, name, name, "random@example.com", False))

    for repo in repos:
        for remote in repos:
            if remote.working_dir != repo.working_dir:
                name = get_repo_name_workdir(remote.working_dir)
                repo.create_remote(name, remote.git_dir)
                print(f"created Remote /refs/remote/{name} for {get_repo_name_workdir(repo.working_dir)}")
    return repos


def get_initial_blog_commit_by_name(
        repo: git.Repo,
        blog_author: str,
        blog_name: str
) -> git.Commit | None:
    """
    returns the commit sha of the blog with the given name
    blog_author: the author of the blog
    blog_name: the name of the blog
    :returns: the commit sha of the blog
    """
    for ref in repo.references:
        # check if the reference is a post
        if ref.path.__contains__(f"heads/blogs/{blog_author}"):
            # get the first commit of this reference
            first_commit = repo.commit(get_commit_id_from_ref(ref.name))
            if first_commit.message.__contains__(f"initialize blog: {blog_name}"):
                return first_commit
    return None


def get_initial_blog_commit_by_commit(
        commit: git.Commit,
) -> git.Commit:
    """
    returns the commit sha of the blog with the given name
    blog_author: the author of the blog
    blog_name: the name of the blog
    :returns: the commit sha of the blog
    """
    while len(commit.parents) > 0:
        commit = commit.parents[0]
    return commit


def get_latest_post_commit_by_commit(
        commit: git.Commit,
) -> git.Commit:
    """
    returns the commit sha of the blog with the given name
    blog_author: the author of the blog
    blog_name: the name of the blog
    :returns: the commit sha of the blog
    """
    while len(commit.parents) > 0:
        commit = commit.parents[0]
    return commit


def get_post_commit_by_name(repo: git.Repo, author, post_name: str) -> git.Commit | None:
    """
    returns the commit sha of the post with the given name
    :param repo: repo we are working in
    :param post_name: the name of the post
    :param author: author of the post
    :returns: the commit sha of the post
    """
    for ref in repo.references:
        # break if the ref is not a blog from <author>
        if not f"heads/posts/{author}" in ref.name:
            continue
        # check if the blog name is mentioned in the message
        if post_name in ref.commit.message:
            return ref.commit
    return None


def get_latest_blog_commit_by_name(repo: git.Repo, blog_name: str) -> git.Commit:
    """
    returns the latest commit of a blog when given the blog's name
    :param repo: the repo we are working on
    :param blog_name: the name of the blog
    :return:
    """
    for ref in repo.references:
        if blog_name in ref.commit.message:
            return ref.commit
    return None


def get_latest_post_commit_by_name(repo: git.Repo, post_name: str) -> git.Commit | None:
    """
    returns the latest commit of a post when given the post's name
    :param repo: the repo we are working on
    :param post_name: the name of the post
    :return:
    """
    for ref in repo.references:
        if f"post: {post_name}" in ref.commit.message:
            return ref.commit
    return None


def get_latest_comment_commit_by_name(repo: git.Repo, comment_title: str) -> git.Commit | None:
    """
    returns the latest commit of a comment when given the comment's name
    :param repo: the repo we are working on
    :param comment_title: the name of the comment
    :return:
    """
    for ref in repo.references:
        if f"create comment: {comment_title}" in ref.commit.message:
            return ref.commit
        elif f"update comment: {comment_title}" in ref.commit.message:
            return ref.commit
        elif f"merge comment: {comment_title}" in ref.commit.message:
            return ref.commit
    return None


def get_initial_comment_commit_by_name(repo: git.Repo, comment_title: str) -> git.Commit | None:
    """
    returns the initial commit of a comment when given the comment's name
    :param repo: the repo we are working on
    :param comment_title: the name of the comment
    :return:
    """
    for ref in repo.references:
        # check if the reference is a post
        if ref.path.__contains__("/comments/"):
            # get the first commit of this reference
            first_commit = repo.commit(get_commit_id_from_ref(ref.name))
            if first_commit.message.__contains__(f"create comment: {comment_title}"):
                return ref.commit
    return None


def get_initial_post_commit_by_name(repo: git.Repo, post_name: str) -> git.Commit | None:
    """
    returns the initial commit of a post when given the post's name
    :param repo: the repo we are working on
    :param post_name: the name of the post
    :return: the initial commit
    """
    for ref in repo.references:
        # check if the reference is a post
        if ref.path.__contains__("heads/posts/"):
            # get the first commit of this reference
            first_commit = repo.commit(get_commit_id_from_ref(ref.name))
            if first_commit.message.__contains__(f"create post: {post_name}"):
                return first_commit
    return None


def fetch_all_remotes(repo: git.Repo):
    """
    fetches all data from remotes
    :param repo:
    :return:
    """
    for remote in repo.remotes:
        remote.fetch()


def repo_remote_merge(repo: git.Repo):
    """
    merge the local repo with the remotes
    :param repo: the local repo
    :return:
    """
    repo_merge_remote_comments(repo)
    repo_merge_remote_posts(repo)
    repo_merge_remote_blogs(repo)


def repo_merge_remote_blogs(repo: git.Repo):
    """
    merge the local blogs with the remotes
    :param repo: the repo we are working on
    :param changed: list of posts that were created or changed
    :return:
    """
    for remote in repo.remotes:
        for ref in remote.refs:
            if f"{remote.name}/blogs/" in ref.name:
                merge_remote_blog(repo, ref, remote.name)


def merge_remote_blog(repo: git.Repo, update: git.Reference, remote_name: str):
    """
    merges blogs if necessary or updates the local references, adds new unreferenced posts as well
    :param repo: the repo we are working on
    :param update: the blog we want to create or merge with local posts
    :param remote_name: name of the remote
    :return:
    """
    blog_id = get_commit_id_from_ref(update.name)
    blog_author = update.name[len(f"{remote_name}/blogs/"):]
    slash = blog_author.find("/")
    blog_author = blog_author[:slash]
    # filter changed for the current blog
    try:
        # check if the blog exists already, throws an error if it does not
        local_refs = repo.git.execute(["git", "show-ref", "--hash", f"refs/heads/blogs/{blog_author}/{blog_id}"])
        latest_post = repo.commit(local_refs)
    except git.exc.GitCommandError:
        # blog does not exist, just update reference
        repo.git.update_ref(f"refs/heads/blogs/{remote_name}/{blog_id}", update.commit)
    else:
        # the blog already exists, merge with existing local blog
        try:
            # check if the update commit is an ancestor of the latest local commit, throws error if not
            repo.git.execute(["git", "merge-base", "--is-ancestor", update.commit.hexsha, latest_post.hexsha])
            # if you reach here the blog is an ancestor, ignore
        except git.exc.GitCommandError:
            # not an ancestor, merge blog
            repo.git.update_ref(f"refs/heads/blogs/{remote_name}/{blog_id}", update.commit)


def repo_merge_remote_posts(repo: git.Repo):
    """
    merge the local posts with the remotes
    :param repo: the repo we are working on
    :return:
    """
    for remote in repo.remotes:
        for ref in remote.refs:
            if f"{remote.name}/posts/" in ref.name:
                merge_remote_post(repo, ref, remote.name)


def merge_remote_post(repo: git.Repo, update: git.Reference, remote_name: str):
    """
    merges posts if necessary or updates the local references
    :param repo: the repo we are working on
    :param update: the post we want to create or merge with local posts
    :param remote_name: name of the remote branch
    :return: list of created or changed posts
    """
    post_id = get_commit_id_from_ref(update.name)
    post_author = update.name[len(f"{remote_name}/posts/"):]
    slash = post_author.find("/")
    post_author = post_author[:slash]

    try:
        # check if the post exists already
        local_refs = repo.git.execute(["git", "show-ref", "--hash", f"refs/heads/posts/{post_id}"])
    except git.exc.GitCommandError:
        # the post does not exist, just update reference
        repo.git.update_ref(f"refs/heads/posts/{post_author}/{post_id}", update.commit)
    # the post already exists, merge with existing post
    else:
        latest_post = repo.commit(local_refs)
        try:
            # check if the update commit is an ancestor of the latest local commit, if yes ignore
            repo.git.execute(["git", "merge-base", "--is-ancestor", update.commit.hexsha, latest_post.hexsha])
        except git.exc.GitCommandError:
            repo.git.update_ref(f"refs/heads/posts/{post_author}/{post_id}", post_id)


def repo_merge_remote_comments(repo: git.Repo):
    """
    merge the local posts with the remotes
    :param repo: the repo we are working on
    :return:
    """
    for remote in repo.remotes:
        for ref in remote.refs:
            if f"{remote.name}/comments/" in ref.name:
                merge_remote_comments(repo, ref, remote.name)


def merge_remote_comments(repo: git.Repo, update: git.Reference, remote_name: str):
    """
    merges posts if necessary or updates the local references
    :param repo: the repo we are working on
    :param update: the post we want to create or merge with local posts
    :param remote_name: name of the remote branch
    :return: list of created or changed posts
    """
    comment_commit_id = get_commit_id_from_ref(update.name)

    try:
        # check if the comment exists already
        local_refs = repo.git.execute(["git", "show-ref", "--hash", f"refs/heads/comments/{comment_commit_id}"])
    except git.exc.GitCommandError:
        # the post does not exist, just update reference
        repo.git.update_ref(f"refs/heads/comments/{comment_commit_id}", update.commit)
    # the comment already exists, merge with existing post
    else:
        latest_comment = repo.commit(local_refs)
        try:
            # check if the update commit is an ancestor of the latest local commit, if yes ignore
            repo.git.execute(["git", "merge-base", "--is-ancestor", update.commit.hexsha, latest_comment.hexsha])
        except git.exc.GitCommandError:
            repo.git.update_ref(f"refs/heads/comments/{comment_commit_id}", comment_commit_id)


def clear_index_of_files(repo: git.Repo):
    index_files = [item.path for item in repo.index.entries.values()]

    if index_files:
        repo.index.remove(index_files, working_tree=False)
